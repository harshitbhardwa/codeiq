# Multi-stage build for better space efficiency
FROM python:3.10-slim as builder

# Install build dependencies and cleanup in one layer
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libopenblas-dev \
    liblapack-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements with aggressive cleanup
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge && \
    find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /opt/venv -type f -name "*.pyc" -delete && \
    find /opt/venv -type f -name "*.pyo" -delete

# Production stage
FROM python:3.10-slim

# Install runtime dependencies only and cleanup in one layer
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libopenblas0 \
    liblapack3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/build

# Set environment variables
ENV PYTHONPATH=/app
ENV GIT_REPO_PATH=/app/repo
ENV DB_HOST=localhost
ENV DB_PORT=5433
ENV DB_USER=user
ENV DB_PASSWORD=password
ENV DB_NAME=code_analysis
ENV API_HOST=0.0.0.0
ENV API_PORT=5000
ENV API_DEBUG=False
ENV VECTOR_DIMENSION=384
ENV FAISS_INDEX_PATH=/app/data/faiss_index
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/app/logs/app.log

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ready || exit 1

# Run the application
CMD ["/opt/venv/bin/python", "app.py"]