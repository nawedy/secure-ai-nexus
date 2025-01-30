# Use multi-stage build for security
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Second stage
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY src/ src/
COPY scripts/ scripts/

# Create non-root user
RUN useradd -m -u 1000 secureai
RUN chown -R secureai:secureai /app
USER secureai

# Set environment variables
ENV PYTHONPATH=/app
ENV AZURE_MONITOR_CONNECTION_STRING=""
ENV LOG_LEVEL=INFO

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R secureai:secureai /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
