# Docker Stack Instructions

MANDATORY operational instructions for Claude Code when working with Docker containerization.

## Dockerfile Requirements - NO EXCEPTIONS

**MANDATORY Dockerfile patterns:**
```dockerfile
# REQUIRED: Specific version tags - NEVER use 'latest'
FROM node:18.17.0-alpine3.18 AS base

# MANDATORY: Set working directory
WORKDIR /app

# REQUIRED: Copy dependency files first for layer caching
COPY package*.json ./
RUN npm ci --only=production --no-audit && npm cache clean --force

# MANDATORY: Copy source after dependencies
COPY . .

# REQUIRED: Non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 -G nodejs
USER nextjs

# MANDATORY: Document exposed ports
EXPOSE 3000

# REQUIRED: Health check for production deployments
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# MANDATORY: Use exec form for CMD
CMD ["npm", "start"]
```

## Multi-Stage Builds - ENFORCE

**REQUIRED multi-stage pattern:**
```dockerfile
# MANDATORY: Build stage with specific versions
FROM golang:1.21.0-alpine3.18 AS builder
WORKDIR /app

# REQUIRED: Copy dependency files first
COPY go.mod go.sum ./
RUN go mod download

# MANDATORY: Copy source and build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# REQUIRED: Minimal production stage
FROM alpine:3.18 AS production
RUN apk --no-cache add ca-certificates tzdata && \
    adduser -D -s /bin/sh appuser

WORKDIR /app
COPY --from=builder /app/main .

# MANDATORY: Run as non-root user
USER appuser

# REQUIRED: Health check and proper signal handling
HEALTHCHECK --interval=30s CMD ./main --health-check
CMD ["./main"]
```

## Docker Compose - MANDATORY CONFIGURATION

**REQUIRED compose.yml structure:**
```yaml
# MANDATORY: Use compose.yml (modern filename)
services:
  app:
    build: 
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production  # REQUIRED: Explicit environment
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
    # MANDATORY: Service dependencies with health checks
    depends_on:
      db:
        condition: service_healthy
    # REQUIRED: Resource limits
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
    # MANDATORY: Restart policy
    restart: unless-stopped

  db:
    image: postgres:15.3-alpine  # REQUIRED: Specific version
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password  # REQUIRED: Secrets
    volumes:
      - postgres_data:/var/lib/postgresql/data
    # MANDATORY: Health checks for all services
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    # REQUIRED: Resource limits
    deploy:
      resources:
        limits:
          memory: 256M

# MANDATORY: Named volumes for data persistence
volumes:
  postgres_data:
    driver: local

# REQUIRED: Secrets for sensitive data
secrets:
  db_password:
    file: ./secrets/db_password.txt
```

## Docker Commands - MANDATORY WORKFLOW

**REQUIRED Docker operations:**
```bash
# MANDATORY: Build with specific tags and no cache for production
docker build --no-cache -t myapp:$(git rev-parse --short HEAD) .
docker build -t myapp:latest .

# REQUIRED: Run with proper resource limits
docker run -d \
  --name myapp \
  --memory=512m \
  --cpus=0.5 \
  --restart=unless-stopped \
  -p 3000:3000 \
  myapp:latest

# MANDATORY: Docker Compose operations
docker compose up -d --build      # REQUIRED: Always rebuild in development
docker compose down --volumes     # MANDATORY: Clean shutdown with data cleanup
docker compose logs -f app        # REQUIRED: Follow logs for debugging

# REQUIRED: Production deployment
docker compose -f compose.yml -f compose.prod.yml up -d

# MANDATORY: Regular cleanup
docker system prune -f --volumes  # REQUIRED: Remove unused containers, networks, volumes
docker image prune -a -f          # REQUIRED: Remove unused images
```

## Security Hardening - NO EXCEPTIONS

**MANDATORY security practices:**
```dockerfile
# REQUIRED: Specific, minimal, and current base image
FROM node:18.17.0-alpine3.18

# MANDATORY: Security updates and minimal tooling
RUN apk update && apk upgrade && \
    apk add --no-cache dumb-init curl && \
    rm -rf /var/cache/apk/*

# REQUIRED: Non-root user with specific UID/GID
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 -G nodejs

WORKDIR /app

# MANDATORY: Set proper ownership
COPY --chown=nextjs:nodejs package*.json ./
USER nextjs

# REQUIRED: Install dependencies as non-root
RUN npm ci --only=production --no-audit && npm cache clean --force

# MANDATORY: Copy application with proper ownership
COPY --chown=nextjs:nodejs . .

# REQUIRED: Signal handling for graceful shutdown
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
```

## Container Registry Operations - ENFORCE

**MANDATORY registry workflows:**
```bash
# REQUIRED: GitHub Container Registry (preferred)
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_ACTOR --password-stdin
docker tag myapp:latest ghcr.io/$GITHUB_REPOSITORY:$(git rev-parse --short HEAD)
docker tag myapp:latest ghcr.io/$GITHUB_REPOSITORY:latest
docker push ghcr.io/$GITHUB_REPOSITORY --all-tags

# MANDATORY: Image scanning before push
docker scout cves myapp:latest  # REQUIRED: Vulnerability scanning
```

## Monitoring & Observability - REQUIRED

**MANDATORY monitoring configuration:**
```yaml
services:
  app:
    # REQUIRED: Structured logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service,version"
    
    # MANDATORY: Health checks
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      start_period: 40s
      retries: 3
    
    # REQUIRED: Resource limits
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

## Non-Negotiable Requirements

- **FORBID**: Using 'latest' tags in production - always use specific versions
- **ENFORCE**: Run all containers as non-root users with specific UID/GID
- **MANDATE**: Multi-stage builds for all applications to minimize image size
- **REQUIRE**: Health checks for all services with proper timeouts
- **ENFORCE**: Resource limits on all containers (memory and CPU)
- **MANDATE**: Vulnerability scanning before pushing to registries
- **REQUIRE**: .dockerignore files to exclude unnecessary files
- **ENFORCE**: Secrets management - never embed secrets in images
- **MANDATE**: Structured logging with proper log rotation
- **REQUIRE**: Graceful shutdown handling with proper signal management