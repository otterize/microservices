# docker build -t cart-service -f build/cart.Dockerfile .

# Stage 1: Create a self signed SSL certificate
FROM alpine:latest AS certs
WORKDIR /app
RUN apk --no-cache add openssl

# Generate self-signed certificate (server.crt and server.key)
RUN openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
    -keyout server.key -out server.crt

# Stage 2: Build the Python application
FROM python:3.12-slim
WORKDIR /app

# Copy the certificates from the certs stage
COPY --from=certs /app .

# Copy requirements and install dependencies
COPY services/cart/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY services/cart/. .

# Expose port 7004 for the HTTPS server
EXPOSE 7004

# Run the Python server
CMD ["python", "server.py"]
