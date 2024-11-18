# docker build -t newsletter-service -f build/newsletter.Dockerfile .

# Stage 1: Create a self signed SSL certificate
FROM alpine:latest AS certs
WORKDIR /app
RUN apk --no-cache add openssl

# Generate self-signed certificate (server.crt and server.key)
RUN openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
    -keyout server.key -out server.crt

# Stage 2: Build the Node application
FROM node:21
WORKDIR /app

# Copy the certificates from the certs stage
# COPY --from=certs /app .

# Download and install dependencies
COPY services/newsletter/package*.json ./
RUN npm install

# Copy the rest of the application code
COPY services/newsletter/. .

# Expose port 7003 for the HTTPS server
EXPOSE 7003

# Start the server
CMD ["node", "index.js"]
