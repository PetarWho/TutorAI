# Lecture-to-Tutor AI Backend

A scalable backend system that transforms long lecture recordings into searchable, trustworthy AI tutors using Retrieval-Augmented Generation (RAG).

## Features

- 🎥 **Audio/Video Upload**: Accept lecture recordings in various formats
- 🎯 **Accurate Transcription**: Whisper-based transcription with timestamps
- 📚 **PDF Generation**: Export transcripts and summaries as PDFs
- 🔍 **Smart Search**: RAG-powered Q&A with source citations
- ⏰ **Timestamp Navigation**: Jump to specific moments in lectures
- 👥 **User Management**: JWT-based authentication and user isolation
- 📖 **Course Organization**: Group lectures into courses for multi-lecture search
- 🐳 **Docker Deployment**: GPU-accelerated containerized deployment

## Quick Start

### Prerequisites

- Docker & Docker Compose
- NVIDIA GPU (optional, for faster performance)
- Ollama (automatically deployed)

### Deployment

#### GPU Deployment (Recommended)
```bash
# Clone and deploy
git clone <repository-url>
cd lecture-scraper/backend
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

#### CPU-only Deployment
```bash
./scripts/deploy.sh --cpu
```

### Manual Deployment

```bash
# Build and start services
docker-compose up -d --build

# Setup Ollama models
docker exec lecture-rag-backend ollama pull nomic-embed-text
docker exec lecture-rag-backend ollama pull llama3.1:70b  # or llama3.1:8b for CPU
```

## API Documentation

Once deployed, visit:
- **API Documentation**: http://localhost:8069/docs
- **ReDoc**: http://localhost:8069/redoc

## Core Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Lecture Management
- `POST /lectures/upload` - Upload lecture audio/video
- `GET /lectures/my-lectures` - Get user's lectures
- `POST /lectures/{lecture_id}/ask` - Ask questions about lecture
- `GET /lectures/{lecture_id}/transcript` - Get full transcript with timestamps
- `GET /lectures/{lecture_id}/search` - Search within lecture

### Course Management
- `POST /courses/` - Create course
- `GET /courses/` - Get user's courses
- `POST /courses/{course_id}/lectures` - Add lecture to course
- `POST /courses/search` - Search across multiple lectures

### PDF Generation
- `POST /lectures/{lecture_id}/pdf` - Generate transcript or summary PDF
- `GET /lectures/{lecture_id}/pdf/{filename}` - Download PDF

## Architecture

```
├── app/
│   ├── api/           # FastAPI routes
│   ├── core/          # Security and core functionality
│   ├── db/            # Database and vector store
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic
│   └── utils/         # Utilities
├── data/              # Persistent storage
├── scripts/           # Deployment scripts
└── Docker files       # Container configuration
```

## Technology Stack

- **API Framework**: FastAPI
- **Transcription**: Faster-Whisper (GPU-accelerated)
- **LLM**: Ollama (local inference)
- **Vector Store**: Qdrant
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Containerization**: Docker + Docker Compose

## Configuration

Environment variables (`.env` file):
```env
OLLAMA_LLM_MODEL=llama3.1:70b
OLLAMA_EMBED_MODEL=nomic-embed-text
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Development

### Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.db.database import init_db; init_db()"

# Start Ollama (separate terminal)
ollama serve

# Download models
ollama pull nomic-embed-text
ollama pull llama3.1:70b

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8069
```

### Project Structure

- **Upload**: Audio/video files are transcribed using Whisper
- **Process**: Transcripts are chunked and embedded using Ollama
- **Store**: Embeddings stored in Qdrant vector database
- **Query**: RAG retrieves relevant chunks and generates answers
- **Response**: Answers include source citations with timestamps

## Performance Considerations

- **GPU Usage**: CUDA-enabled Docker for 10x faster transcription
- **Memory Management**: Efficient chunking for large lectures
- **Caching**: Vector indices cached for fast retrieval
- **Scalability**: Stateless API design for horizontal scaling

## Security Features

- JWT-based authentication
- User data isolation
- Request rate limiting
- Input validation and sanitization
- Secure file handling

## Monitoring

- Health checks on all services
- Structured logging
- Container health monitoring
- API performance metrics

## Troubleshooting

### Common Issues

1. **GPU not detected**: Ensure NVIDIA drivers and Docker GPU support are installed
2. **Ollama connection**: Check if Ollama container is running on port 11434
3. **Memory issues**: Reduce model size or increase system RAM
4. **Slow transcription**: Verify GPU acceleration is working

### Logs

```bash
# View backend logs
docker logs lecture-rag-backend

# View Ollama logs
docker logs ollama

# View all services
docker ps
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

[Your License Here]