# Production Nginx Dockerfile
FROM nginx:alpine

# Metadata
LABEL org.opencontainers.image.title="AI Telegram Bot - Nginx Reverse Proxy"
LABEL org.opencontainers.image.description="Nginx reverse proxy for AI TG Bot services"
LABEL org.opencontainers.image.vendor="AI TG Bot Team"
LABEL maintainer="AI TG Bot Team"

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create health check file
RUN echo '{"status":"healthy","service":"nginx"}' > /usr/share/nginx/html/health.json

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]

