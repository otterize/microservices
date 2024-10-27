# docker build -t users-service -f build/users.Dockerfile .

# Stage 1: Create a self signed SSL certificate
FROM alpine:latest AS certs
WORKDIR /app
RUN apk --no-cache add openssl

# Generate self-signed certificate (server.crt and server.key)
RUN openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
    -keyout server.key -out server.crt

# Stage 2: Build the Go application
FROM golang:1.23-alpine AS builder
WORKDIR /app

# Copy the certificates from the certs stage
COPY --from=certs /app .

# Download dependencies
COPY services/users/go.mod services/users/go.sum ./
RUN go mod download

# Copy the rest of the application code and build the Go application
COPY services/users/. .
RUN go build -o main .

# Expose port 7001 for the HTTPS server
EXPOSE 7001

# Run the Go application
CMD ["./main"]
