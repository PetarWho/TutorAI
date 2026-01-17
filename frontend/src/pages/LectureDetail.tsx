import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { lectureAPI } from '../services/api';
import type { TimestampSource } from '../services/api';
import { Button } from '../components/ui/Button';
import { Textarea } from '../components/ui/Textarea';
import { 
  ArrowLeft, 
  Download, 
  FileText, 
  Play, 
  Send,
  MessageSquare
} from 'lucide-react';

const LectureDetail: React.FC = () => {
  const { lectureId } = useParams<{ lectureId: string }>();
  const { user, token } = useAuth();
  const [lecture, setLecture] = useState<any>(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<TimestampSource[]>([]);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);

  useEffect(() => {
    const fetchLectureData = async () => {
      if (!token || !lectureId) return;
      
      try {
        const lectureData = await lectureAPI.getLectureDetails(lectureId, token);
        setLecture(lectureData);
      } catch (error) {
        console.error('Failed to fetch lecture data:', error);
        // Fallback to generic title if API fails
        setLecture({ title: `Lecture ${lectureId}` });
      }
    };

    fetchLectureData();
  }, [lectureId, token]);

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || !token) return;

    setIsLoadingQuestion(true);
    try {
      const response = await lectureAPI.askQuestion(lectureId!, question, token);
      setAnswer(response.answer);
      setSources(response.sources);
    } catch (error) {
      console.error('Failed to ask question:', error);
    } finally {
      setIsLoadingQuestion(false);
    }
  };

  const handleDownloadPDF = async (type: 'transcript' | 'summary') => {
    if (!token) return;
    
    try {
      const response = await lectureAPI.generatePDF(lectureId!, type, token);
      const downloadResponse = await lectureAPI.downloadPDF(lectureId!, response.filename, token);
      
      const url = window.URL.createObjectURL(new Blob([downloadResponse.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = response.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download PDF:', error);
    }
  };

  if (!user) return <div>Please log in to view lecture details.</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <Link to="/dashboard">
          <Button variant="ghost" size="sm" className="pl-0 hover:bg-transparent hover:text-blue-600" leftIcon={<ArrowLeft className="h-4 w-4" />}>
            Back to Dashboard
          </Button>
        </Link>
      </div>

      {/* Main Content */}
      <div className="space-y-6">
        {/* Q&A Section */}
        <div className="bg-white shadow-sm border border-gray-100 rounded-2xl overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-100 bg-gray-50/50">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <MessageSquare className="h-5 w-5 mr-2 text-blue-600" />
              {lecture?.title || 'Loading...'}
            </h3>
          </div>
          <div className="p-6">
            {/* Download Buttons */}
            <div className="flex gap-3 mb-6">
              <Button variant="secondary" size="sm" onClick={() => handleDownloadPDF('transcript')} leftIcon={<Download className="h-4 w-4" />}>
                Download Transcript
              </Button>
              <Button variant="secondary" size="sm" onClick={() => handleDownloadPDF('summary')} leftIcon={<FileText className="h-4 w-4" />}>
                Download Summary
              </Button>
            </div>

            <form onSubmit={handleAskQuestion} className="space-y-4">
              <Textarea
                label="Ask question"
                rows={3}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask anything about this lecture (e.g., 'What was the main conclusion?')"
              />
              <Button 
                type="submit" 
                className="w-full" 
                isLoading={isLoadingQuestion} 
                disabled={!question.trim()}
                leftIcon={!isLoadingQuestion && <Send className="h-4 w-4" />}
              >
                Ask Question
              </Button>
            </form>

            {/* Answer */}
            {answer && (
              <div className="mt-8">
                <div className="bg-blue-50 rounded-xl p-5 border border-blue-100">
                  <h4 className="text-sm font-bold text-blue-900 mb-2 uppercase tracking-wide">AI Answer</h4>
                  <p className="text-gray-800 leading-relaxed">{answer}</p>
                </div>
              </div>
            )}

            {/* Sources */}
            {sources.length > 0 && (
              <div className="mt-6">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">Sources & Timestamps</h4>
                <div className="space-y-3">
                  {sources.map((source, index) => (
                    <div key={index} className="p-4 bg-gray-50 border border-gray-100 rounded-xl hover:border-blue-200 transition-colors">
                      <div className="flex items-start gap-4">
                        <Button 
                          size="sm" 
                          variant="secondary"
                          onClick={() => {/* TODO: Implement video jumping */}}
                          leftIcon={<Play className="h-3 w-3" />}
                          className="flex-shrink-0"
                        >
                          {source.video_timestamp}
                        </Button>
                        <div className="flex-1">
                           <p className="text-sm text-gray-700 leading-snug">{source.text}</p>
                           <p className="text-xs text-gray-400 mt-1">
                             Segment: {source.start_str} - {source.end_str}
                           </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LectureDetail;