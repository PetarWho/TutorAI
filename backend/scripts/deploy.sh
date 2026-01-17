#!/bin/bash

# Deployment script for Lecture RAG Backend

set -e

echo "🚀 Deploying Lecture RAG Backend..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check for GPU support
GPU_SUPPORT=false
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected"
    GPU_SUPPORT=true
else
    echo "⚠️  No NVIDIA GPU detected, using CPU-only deployment"
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/lectures data/indexes data/pdfs logs

# Set permissions
chmod 755 data data/lectures data/indexes data/pdfs logs

# Choose deployment mode
if [ "$GPU_SUPPORT" = true ] && [ "$1" != "--cpu" ]; then
    echo "🔥 Starting GPU-enabled deployment..."
    docker-compose up -d --build
else
    echo "💻 Starting CPU-only deployment..."
    docker-compose -f docker-compose.cpu.yml up -d --build
fi

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Setup Ollama models
echo "🤖 Setting up Ollama models..."
if [ "$GPU_SUPPORT" = true ] && [ "$1" != "--cpu" ]; then
    docker exec lecture-rag-backend bash -c "curl -f http://ollama:11434/api/tags || exit 1"
    docker exec lecture-rag-backend bash -c "ollama pull nomic-embed-text && ollama pull llama3.1:70b"
else
    docker exec lecture-rag-backend-cpu bash -c "curl -f http://ollama:11434/api/tags || exit 1"
    docker exec lecture-rag-backend-cpu bash -c "ollama pull nomic-embed-text && ollama pull llama3.1:8b"
fi

# Check if services are running
echo "🔍 Checking service health..."
if [ "$GPU_SUPPORT" = true ] && [ "$1" != "--cpu" ]; then
    BACKEND_CONTAINER="lecture-rag-backend"
else
    BACKEND_CONTAINER="lecture-rag-backend-cpu"
fi

# Check backend health
for i in {1..10}; do
    if curl -f http://localhost:8069/ > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    else
        echo "⏳ Waiting for backend to be healthy... (attempt $i/10)"
        sleep 10
    fi
done

# Display deployment info
echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Service URLs:"
echo "   Backend API: http://localhost:8069"
echo "   API Docs: http://localhost:8069/docs"
echo "   Ollama: http://localhost:11434"
echo ""
echo "📊 Container Status:"
docker ps --filter "name=lecture-rag" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "📝 Next Steps:"
echo "   1. Register a user: POST http://localhost:8069/auth/register"
echo "   2. Login: POST http://localhost:8069/auth/login"
echo "   3. Upload a lecture: POST http://localhost:8069/lectures/upload"
echo "   4. Ask questions: POST http://localhost:8069/lectures/{lecture_id}/ask"
echo ""
echo "🛠️  Management Commands:"
echo "   View logs: docker logs $BACKEND_CONTAINER"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
