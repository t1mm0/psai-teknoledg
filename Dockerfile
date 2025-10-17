# Dockerfile for PSAI_A + Teknoledg Unified System
# Purpose: Containerized deployment for Render.com
# Last Modified: 2024-12-19 | By: AI Assistant | Completeness: 95/100

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs data briefs static

# Set permissions
RUN chmod +x *.py

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/api/health || exit 1

# Start the application
CMD ["python", "unified_system.py"]
