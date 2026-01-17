# Use NVIDIA CUDA base image for GPU support
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$PATH:$CUDA_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 && \
    pip install --no-cache-dir -r requirements.txt

# Copy wait-for-it.sh and init-ollama.sh scripts first
COPY scripts/wait-for-it.sh /app/wait-for-it.sh
COPY scripts/init-ollama.sh /app/scripts/init-ollama.sh

# Make scripts executable
RUN chmod +x /app/wait-for-it.sh
RUN chmod +x /app/scripts/init-ollama.sh

# Copy the rest of the application code
COPY . .

# Create data directories
RUN mkdir -p data/lectures data/indexes data/pdfs

# Expose port
EXPOSE 8069

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8069/ || exit 1

# Start backend after Ollama is ready
CMD ["/bin/sh", "-c", "/app/wait-for-it.sh ollama:11434 --timeout=120 --strict && uvicorn app.main:app --host 0.0.0.0 --port 8069"]
