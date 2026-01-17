# Tutor AI: Generative AI Application Specification: Personal Learning Assistant

## Project Overview

### Problem Description
Learners often struggle to efficiently consume and understand educational content from various sources (videos, articles, podcasts). The process of watching long videos, reading lengthy articles, and finding answers to specific questions is time-consuming and doesn't adapt to individual learning needs or questions that arise during study.

### Target Audience
- **Primary**: Self-directed learners and students seeking to understand complex topics
- **Secondary**: Professionals needing to quickly learn new skills for career development
- **Tertiary**: Curious individuals exploring new subjects and hobbies

## Main Use Cases (User Stories)

### Use Case 1: Lecture Upload and Processing
**As a learner**, I want to upload lecture recordings (audio/video) and get them processed, so that I can search and ask questions about the content later.

**User Flow:**
1. User uploads lecture file (video, audio) through drag-and-drop interface
2. System transcribes the audio using Whisper with timestamps
3. System processes transcript and creates searchable embeddings
4. User receives confirmation when processing is complete
5. Lecture appears in user's dashboard for interaction

### Use Case 2: Q&A Search Within Lectures
**As a student**, I want to ask specific questions about uploaded lectures and get accurate answers with source citations, so that I can quickly find information without re-watching entire recordings.

**User Flow:**
1. User selects a lecture from their dashboard
2. User types a question about the lecture content
3. System uses RAG to find relevant transcript segments
4. System generates answer with timestamp citations
5. User can click timestamps to jump to specific moments in lecture

### Use Case 3: Course Organization
**As a learner**, I want to organize multiple lectures into courses for better structure, so that I can group related content and navigate between lectures efficiently.

**User Flow:**
1. User creates a course with name and description
2. User adds existing lectures to the course
3. User can view all lectures within a course
4. User can navigate to individual lecture pages for Q&A
5. User can manage course membership (add/remove lectures)

## System Architecture

### Inputs
- **File Upload**: Audio/video files (MP4, MP3, WAV, M4A) for lecture recordings
- **Text Input**: Questions about lecture content
- **Course Management**: Lecture organization into courses
- **User Authentication**: Login/registration for data isolation

### Outputs
- **Transcriptions**: Time-stamped text transcripts of uploaded lectures
- **Q&A Responses**: Answers to questions with source citations and timestamps
- **Search Results**: Relevant transcript segments for user queries
- **PDF Exports**: Downloadable transcripts and summaries
- **Course Organization**: Structured grouping of related lectures

## System Parameters

### Transcription Controls
- **Audio Quality**: Auto-detect, High quality, Standard quality
- **Language**: Auto-detect, English, Spanish, French, German, etc.
- **Timestamp Precision**: Every 30 seconds, Every minute, Every 5 minutes
- **Processing Speed**: Real-time, Standard, High quality (slower)

### Search and Q&A Controls
- **Search Scope**: Current lecture only
- **Answer Detail**: Brief answer, Detailed explanation, Comprehensive response
- **Source Citations**: Show timestamps, Hide timestamps, Show transcript snippets
- **Result Count**: 3 results, 5 results, 10 results per query

### Course Organization
- **Lecture Grouping**: By subject, By date, By instructor, Custom
- **Course Management**: Create courses, Add/remove lectures, Course descriptions
- **Navigation**: Quick access to lectures within courses

### Export Options
- **Format**: Transcript only, Summary only, Full transcript with timestamps
- **File Type**: PDF, TXT, DOCX
- **Content**: Questions and answers, Citations only, Complete session

### Advanced Parameters
- **LLM Model**: llama3.1:8b (faster), llama3.1:70b (more accurate)
- **Embedding Model**: nomic-embed-text (default)
- **Chunk Size**: Small chunks (more precise), Large chunks (more context)
- **Retrieval Strategy**: Semantic search, Keyword search, Hybrid approach

## Limitations and Risk Mitigation

### Quality Limitations
**Risk**: Generated content may contain factual inaccuracies or outdated information.
**Mitigation**: 
- Implement fact-checking integration with verified sources
- User review and approval workflow
- Confidence scoring for generated content
- Source citation requirements

### Hallucination Management
**Risk**: AI may generate plausible but incorrect information.
**Mitigation**:
- Confidence indicators for each content section
- "Verify with sources" prompts for critical information
- Version control and rollback capabilities
- Peer review features for collaborative environments

### Ethical Considerations
**Risk**: Potential bias in content generation or inappropriate material.
**Mitigation**:
- Content filtering and moderation systems
- Bias detection algorithms
- Cultural sensitivity checks
- Accessibility compliance (WCAG 2.1)

### Privacy and Security
**Risk**: Sensitive educational content or personal data exposure.
**Mitigation**:
- End-to-end encryption for all content
- GDPR and FERPA compliance
- Local processing options for sensitive materials
- User data anonymization and retention policies

### Intellectual Property
**Risk**: Copyright infringement in generated content.
**Mitigation**:
- Originality checks against existing materials
- Proper attribution and citation systems
- License-aware generation (Creative Commons, Public Domain)
- Clear terms of service for content ownership

## Acceptance Criteria

### Functional Requirements
1. **Lecture Upload**: Successfully upload and process audio/video files within 5 minutes
2. **Transcription Accuracy**: 95% accuracy for clear audio, 85% for challenging audio
3. **Q&A Response Time**: Generate answers within 10 seconds with source citations
4. **Course Organization**: Create courses and organize lectures efficiently
5. **PDF Export**: Generate downloadable transcripts and summaries

### Quality Metrics
1. **Answer Relevance**: 85% of answers directly address user questions
2. **Citation Accuracy**: 90% of timestamps correctly point to relevant content
3. **Search Precision**: Top 3 results contain the answer 80% of the time
4. **Transcription Quality**: Readable and accurate timestamps for navigation

### Performance Requirements
1. **Upload Processing**: Files processed within 2x the audio duration
2. **Search Response**: Query results returned within 3 seconds
3. **Concurrent Users**: Support 100 simultaneous users
4. **File Size**: Handle lectures up to 2GB and 4 hours duration

### User Experience Criteria
1. **Intuitive Upload**: New users successfully upload first lecture within 2 minutes
2. **Effective Search**: Users find needed information without re-watching lectures
3. **Mobile Compatibility**: Full functionality on mobile devices
4. **Accessibility**: WCAG 2.1 AA compliance for all interfaces

## Technical Specifications

### Core Technologies
- **Backend**: Python with FastAPI framework
- **AI Models**: Ollama Llama3.1 for Q&A, Faster-Whisper for audio transcription
- **Vector Database**: Qdrant for semantic search and embeddings
- **Database**: PostgreSQL for user data and lecture metadata
- **Frontend**: React 19 with TypeScript for responsive interface
- **Authentication**: JWT-based user authentication
- **File Processing**: FFmpeg for audio/video handling

### Integration Points
- **Ollama Integration**: Local LLM inference for privacy and control
- **Whisper Integration**: GPU-accelerated transcription service
- **Vector Store**: Semantic similarity search for Q&A responses
- **PDF Generation**: Export transcripts and summaries for offline use

### Deployment Architecture
- **Containerization**: Docker with Docker Compose for easy deployment
- **GPU Support**: CUDA-enabled containers for faster transcription
- **Local Deployment**: Self-hosted option for data privacy
- **Monitoring**: Health checks and structured logging
- **Security**: User data isolation and secure file handling

## Current Implementation Status

### Completed Features
1. **Lecture Upload System**: Drag-and-drop interface for audio/video files
2. **Transcription Service**: Whisper-based transcription with timestamps
3. **Q&A System**: RAG-powered question answering with source citations
4. **User Authentication**: JWT-based login and registration
5. **Course Management**: Organize lectures into courses with descriptions
6. **PDF Export**: Download transcripts and summaries
7. **Individual Lecture Search**: Search within specific lectures
8. **Responsive Frontend**: React-based interface with mobile support

### Technology Stack Implementation
- **Backend**: FastAPI with PostgreSQL and Qdrant
- **AI Processing**: Ollama Llama3.1 and Faster-Whisper
- **Frontend**: React 19 with TypeScript and Tailwind CSS
- **Deployment**: Docker Compose with GPU support

## Success Metrics

### User Engagement
- Daily active users: Target 100+ within 3 months
- Lecture processing rate: 500+ lectures per week
- User retention: 70% monthly retention rate
- Feature adoption: 80% of users use Q&A features

### Learning Impact
- Time savings: Average 75% reduction in finding specific information
- Search efficiency: Users find answers in 10 seconds vs 10 minutes of re-watching
- Content accessibility: Full transcript access for all uploaded materials
- Knowledge retention: Better understanding through targeted Q&A

## Additional Information

[GitHub](https://github.com/PetarWho/TutorAI)

*Description: Clean, functional interface with three main sections:*
1. *Left panel: Lecture upload and course management*
2. *Center: Q&A interface with transcript viewer and timestamp navigation*
3. *Right panel: Search results, citations, and export options*

![Dashboard screenshot](img/dashboard.png)
![LangGraph Workflow](img/workflow.png)

*The full project can be found on my [GitHub](https://github.com/PetarWho/TutorAI)*