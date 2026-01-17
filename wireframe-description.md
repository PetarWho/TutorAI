# Tutor AI - Main Screen Wireframe Description

## Overall Layout
**Design Style**: Functional, clean interface focused on lecture interaction and Q&A
**Color Scheme**: Professional blue (#3b82f6) with white background and gray accents
**Typography**: Inter font family for readability and clarity

## Screen Sections

### 1. Header Bar (Top)
- **Logo**: "Tutor AI" with brain/book icon
- **Navigation**: Dashboard | Upload | Courses | Settings | Logout
- **User Profile**: Avatar with user name and login status

### 2. Left Panel - Lecture Management (30% width)
**Section A: Upload Interface**
- Drag-and-drop area for audio/video files
- File upload button with format indicators (MP4, MP3, WAV, M4A)
- Recent uploads list with processing status indicators
- Upload progress bars with time estimates

**Section B: Course Organization**
- Course list with lecture counts
- "Create Course" button
- Add lecture to course dropdown
- Course list view with lecture counts

**Section C: Lecture Library**
- List of uploaded lectures with metadata
- Duration, upload date, file size
- Status indicators (Processing, Ready, Error)
- Quick actions: View, Delete, Add to Course

### 3. Center Panel - Q&A Interface (50% width)
**Tab Navigation**: Transcript | Q&A | Export

**Transcript Tab**:
- Full lecture transcript with timestamps
- Clickable timestamps for navigation
- Highlighted text segments from search results
- Scroll with time synchronization

**Q&A Tab**:
- Question input field with submit button
- Conversation history with questions and answers
- Source citations with clickable timestamps
- "Ask follow-up" suggestions

**Export Tab**:
- PDF generation options (transcript, summary)
- Download buttons for generated files
- Export history

### 4. Right Panel - Results & Actions (20% width)
**Section A: Current Answer**
- AI-generated answer display
- Source citations list with timestamps
- "Regenerate answer" button

**Section B: Quick Actions**
- Jump to timestamp button
- Export to PDF button
- Copy citation link

**Section C: Lecture Info**
- Lecture title and duration
- Upload date and processing status
- Course assignment
- File size and format

**Section D: Help & Tips**
- Question suggestions
- Search tips
- Keyboard shortcuts

## Interactive Elements

### Upload Interface
- Drag-over visual feedback
- File validation indicators
- Progress animations
- Error messages with suggestions

### Q&A Interface
- Typing indicator during AI processing
- Expandable/collapsible answer sections
- Clickable timestamps that jump to video position
- Reaction buttons (helpful, not helpful)

### Transcript Navigation
- Auto-scroll during audio playback
- Highlight current speaking segment
- Zoom controls for text size
- Find functionality within transcript

## Mobile Responsive Considerations

### Tablet View
- Left panel becomes slide-out drawer
- Center panel takes full width
- Right panel moves to bottom as action cards
- Floating action button for uploads

### Mobile View
- Single column layout
- Bottom navigation for main functions
- Swipe gestures for tab switching
- Simplified upload interface

## Accessibility Features

### Reading Assistance
- Adjustable font sizes for transcripts
- High contrast mode
- Screen reader compatibility
- Keyboard navigation for all controls

### Interaction Support
- Full keyboard access to Q&A interface
- Focus indicators for navigation
- Haptic feedback for actions

## Error Handling UI

### Upload Errors
- Clear error messages for unsupported formats
- File size limit warnings
- Network error retry options
- Processing failure notifications

### Q&A Errors
- "No relevant information found" messages
- Question rephrasing suggestions
- Contact support for persistent issues

## Performance Indicators

### Processing Status
- Transcription progress with time estimates
- Vector embedding status
- Search processing indicators
- System health notifications

### Response Time Feedback
- Answer generation timers
- Search result loading indicators
- Network status indicators

---

**Note**: This wireframe reflects the actual implemented Tutor AI system with focus on practical functionality for uploading lectures, transcribing content, and performing Q&A searches with timestamp citations.
