# Use multi-stage build for security
FROM python:3.9-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create and work in a non-root user's directory
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Second stage
FROM python:3.9-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application files
COPY . .

# Create non-root user
RUN useradd -m -u 1000 secureai
RUN chown -R secureai:secureai /app
USER secureai

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8080
ENV UVICORN_LOG_LEVEL=debug

# Expose port
EXPOSE 8080

# Add GCP specific labels
LABEL org.opencontainers.image.source=https://github.com/nawedy/secure-ai-nexus
LABEL org.opencontainers.image.description="SecureAI Platform GCP Deployment"
LABEL org.opencontainers.image.licenses=MIT

# Add health check with longer timeout
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application with more verbose output
CMD ["sh", "-c", "python -V && uvicorn src.main:app --host 0.0.0.0 --port 8080 --log-level debug"]
