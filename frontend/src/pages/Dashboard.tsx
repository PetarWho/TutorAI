import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { lectureAPI } from "../services/api";
import type { Lecture } from "../services/api";
import { Input } from "../components/ui/Input";
import {
  BookOpen,
  Clock,
  FileText,
  MessageCircle,
  Search,
  Upload,
  AlertCircle,
  Download,
} from "lucide-react";
import { format } from "date-fns";
import { Button } from "../components/ui/Button";

const Dashboard: React.FC = () => {
  const { user, token } = useAuth();
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  const formatDuration = (duration: number): string => {
    const hours = Math.floor(duration / 3600);
    const minutes = Math.floor((duration % 3600) / 60);
    const seconds = Math.floor(duration % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  };

  useEffect(() => {
    const fetchLectures = async () => {
      if (!token) return;

      try {
        const response = await lectureAPI.getMyLectures(token);
        setLectures(response.lectures);
      } catch (error) {
        console.error("Failed to fetch lectures:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLectures();
  }, [token]);

  const filteredLectures = lectures.filter(
    (lecture) =>
      lecture.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lecture.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleDownloadPDF = async (
    lectureId: string,
    type: "transcript" | "summary"
  ) => {
    if (!token) return;

    try {
      const response = await lectureAPI.generatePDF(lectureId, type, token);
      const downloadResponse = await lectureAPI.downloadPDF(
        lectureId,
        response.filename,
        token
      );

      const url = window.URL.createObjectURL(new Blob([downloadResponse.data]));
      const link = document.createElement("a");
      link.href = url;
      link.download = response.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download PDF:", error);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center p-8 bg-white rounded-xl shadow-lg max-w-md w-full border border-gray-100">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            Authentication Required
          </h2>
          <p className="text-gray-600">Please log in to view your dashboard.</p>
        </div>
      </div>
    );
  }

  const totalDuration = Math.round(
    lectures.reduce((a, l) => a + (l.duration || 0), 0) / 3600
  );

  const currentMonthCount = lectures.filter((l) => {
    const d = new Date(l.upload_date);
    const n = new Date();
    return (
      d.getMonth() === n.getMonth() && d.getFullYear() === n.getFullYear()
    );
  }).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6 md:p-8 transition-all duration-300">
        <div className="max-w-7xl mx-auto space-y-8">
          
          {/* Header Card */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
                  Welcome back, {user.username}!
                </h1>
                <p className="text-gray-500 mt-2 text-lg">
                  Manage your lectures and track your learning progress
                </p>
              </div>

              <Link to="/upload">
                <Button size="lg" leftIcon={<Upload className="h-5 w-5" />}>
                  Upload Lecture
                </Button>
              </Link>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                label: "Total Lectures",
                value: lectures.length,
                icon: BookOpen,
                color: "text-blue-600",
                bg: "bg-blue-50",
              },
              {
                label: "Total Duration",
                value: `${totalDuration}h`,
                icon: Clock,
                color: "text-green-600",
                bg: "bg-green-50",
              },
              {
                label: "This Month",
                value: currentMonthCount,
                icon: FileText,
                color: "text-amber-600",
                bg: "bg-amber-50",
              },
              {
                label: "Questions Asked",
                value: 0,
                icon: MessageCircle,
                color: "text-purple-600",
                bg: "bg-purple-50",
              },
            ].map(({ label, value, icon: Icon, color, bg }) => (
              <div
                key={label}
                className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">{label}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {value}
                    </p>
                  </div>
                  <div className={`p-3 rounded-xl ${bg}`}>
                    <Icon className={`h-6 w-6 ${color}`} />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Lectures Section */}
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-baseline gap-2">
                <h2 className="text-xl font-bold text-gray-900">
                  Your Lectures
                </h2>
                <span className="text-sm font-medium text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                  {filteredLectures.length}
                </span>
              </div>

              <div className="w-full sm:w-72">
                <Input 
                  icon={<Search className="h-4 w-4" />}
                  placeholder="Search lectures..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-20 bg-white rounded-xl border border-gray-100 border-dashed">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
                <p className="text-gray-500">Loading your library...</p>
              </div>
            ) : filteredLectures.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 bg-white rounded-xl border border-gray-100 border-dashed text-center px-4">
                <div className="bg-gray-50 p-4 rounded-full mb-4">
                  <BookOpen className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">No lectures found</h3>
                <p className="text-gray-500 mt-1 max-w-sm mb-4">
                  {searchTerm 
                    ? `No results matching "${searchTerm}"` 
                    : "Get started by uploading your first lecture material."}
                </p>
                {!searchTerm && (
                   <Link to="/upload">
                     <Button variant="outline" size="sm">Upload now</Button>
                   </Link>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-12">
                {filteredLectures.map((lecture) => (
                  <div
                    key={lecture.lecture_id}
                    className="group bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-100 transition-all duration-200 flex flex-col overflow-hidden"
                  >
                    <div className="p-5 flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div className="bg-blue-50 text-blue-700 text-xs font-semibold px-2 py-1 rounded">
                          Lecture
                        </div>
                        <span className="text-xs text-gray-400">
                          {format(new Date(lecture.upload_date), "MMM d")}
                        </span>
                      </div>
                      
                      <h3 className="font-bold text-gray-900 line-clamp-2 mb-1 group-hover:text-blue-600 transition-colors">
                        {lecture.title}
                      </h3>
                      
                      <div className="mt-4 space-y-2">
                        <div className="flex items-center text-xs text-gray-500">
                          <Clock className="h-3.5 w-3.5 mr-2" />
                          {lecture.duration
                            ? formatDuration(lecture.duration)
                            : "Processing..."}
                        </div>
                        <div className="flex items-center text-xs text-gray-500 truncate">
                          <FileText className="h-3.5 w-3.5 mr-2 flex-shrink-0" />
                          <span className="truncate">{lecture.filename}</span>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 bg-gray-50 border-t border-gray-100 grid gap-3">
                      <Link to={`/lecture/${lecture.lecture_id}`}>
                        <Button className="w-full" size="sm" variant="secondary">
                          <MessageCircle className="h-4 w-4 mr-2" /> Ask Questions
                        </Button>
                      </Link>

                      <div className="grid grid-cols-2 gap-2">
                        <Button 
                          onClick={() => handleDownloadPDF(lecture.lecture_id, "transcript")}
                          variant="ghost" 
                          size="sm"
                          className="text-xs h-8"
                        >
                          <Download className="h-3 w-3 mr-1" /> Transcript
                        </Button>
                        <Button 
                          onClick={() => handleDownloadPDF(lecture.lecture_id, "summary")}
                          variant="ghost" 
                          size="sm"
                          className="text-xs h-8"
                        >
                          <FileText className="h-3 w-3 mr-1" /> Summary
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;