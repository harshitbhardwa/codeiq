FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/build

# Set environment variables
ENV PYTHONPATH=/app
ENV GIT_REPO_PATH=/app/repo
ENV DB_HOST=localhost
ENV DB_PORT=5432
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
CMD ["python", "app.py"] 