import React, { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { lectureAPI } from "../services/api";
import { useDropzone } from "react-dropzone";
import { Button } from "../components/ui/Button"; // Import reusables
import { Input } from "../components/ui/Input";
import {
  ArrowLeft,
  FileAudio,
  FileVideo,
  Upload,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";

const UploadPage: React.FC = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "success" | "error">("idle");
  const [uploadedLectureId, setUploadedLectureId] = useState<string | null>(null);
  const [lectureName, setLectureName] = useState<string>("");

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (!token || acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      if (!file) return;

      const validTypes = [
        "audio/mp3", "audio/mpeg", "audio/mpg", "audio/wav", "audio/m4a",
        "video/mp4", "video/webm", "video/quicktime",
      ];
      
      const fileName = file.name.toLowerCase();
      const validExtensions = ['.mp3', '.wav', '.m4a', '.mp4', '.webm', '.mov'];
      const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
      
      if (!validTypes.includes(file.type) && !hasValidExtension) {
        setUploadStatus("error");
        return;
      }

      setIsUploading(true);
      setUploadProgress(0);
      setUploadStatus("idle");

      try {
        const response = await lectureAPI.upload(file, token, (progress) => {
          setUploadProgress(progress);
        }, lectureName);
        setUploadedLectureId(response.lecture_id);
        setUploadStatus("success");
      } catch (error: unknown) {
        console.error("Upload failed:", error);
        setUploadStatus("error");
        
        // Provide more specific error messages
        if (error && typeof error === 'object' && 'response' in error) {
          const axiosError = error as any;
          if (axiosError.response?.status === 413) {
            console.error("File too large - please try a smaller file or contact support");
          }
        }
      } finally {
        setIsUploading(false);
      }
    },
    [token]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "audio/*": [".mp3", ".wav", ".m4a"],
      "video/*": [".mp4", ".webm", ".mov"],
    },
    multiple: false,
    disabled: isUploading,
  });

  const resetUpload = () => {
    setUploadStatus("idle");
    setUploadedLectureId(null);
    setUploadProgress(0);
  };

  if (!user) return <div>Please log in to upload lectures.</div>;

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Button 
          variant="ghost" 
          onClick={() => navigate("/dashboard")} 
          className="mb-4 pl-0 hover:bg-transparent hover:text-blue-600"
          leftIcon={<ArrowLeft className="h-4 w-4" />}
        >
          Back to Dashboard
        </Button>
        <h1 className="text-3xl font-bold text-gray-900">Upload Lecture</h1>
        <p className="text-gray-500 mt-2">
          Add your audio or video files to start asking questions and getting insights
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Upload Area */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 md:p-8">
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Lecture Name</h3>
              <p className="text-sm text-gray-500 mb-4">
                Enter a custom name for your lecture (optional)
              </p>
              <Input
                placeholder="e.g., Introduction to Biology"
                value={lectureName}
                onChange={(e) => setLectureName(e.target.value)}
                disabled={isUploading}
              />
            </div>

            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Upload File</h3>
              <p className="text-sm text-gray-500">
                Drag and drop your lecture file or click to browse
              </p>
            </div>

            <div
              {...getRootProps()}
              className={`relative border-2 border-dashed rounded-xl p-10 transition-all duration-200 cursor-pointer text-center ${
                isDragActive
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 bg-gray-50 hover:border-blue-400 hover:bg-blue-50/50"
              } ${isUploading ? "cursor-not-allowed opacity-75" : ""}`}
            >
              <input {...getInputProps()} className="hidden" />
              
              {isUploading ? (
                <div className="py-8 space-y-6">
                  <div className="flex justify-center">
                    <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
                  </div>
                  <div>
                    <p className="text-lg font-medium text-gray-900 mb-2">
                      Processing your lecture...
                    </p>
                    <p className="text-sm text-gray-600">
                      This may take a few moments depending on file size
                    </p>
                  </div>
                  <div className="max-w-md mx-auto">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-2 text-right">
                      {uploadProgress}%
                    </p>
                  </div>
                </div>
              ) : (
                <div className="py-8 space-y-6">
                  <div className="flex justify-center gap-4">
                    <div className="p-4 bg-blue-100 rounded-2xl">
                      <FileVideo className="h-8 w-8 text-blue-600" />
                    </div>
                    <div className="p-4 bg-green-100 rounded-2xl">
                      <FileAudio className="h-8 w-8 text-green-600" />
                    </div>
                  </div>
                  <div>
                    <p className="text-xl font-semibold text-gray-900 mb-2">
                      {isDragActive ? "Drop your file here" : "Drag & drop your lecture file"}
                    </p>
                    <p className="text-gray-500 mb-6">
                      or click the button below to browse
                    </p>
                    <Button type="button" disabled={isUploading} leftIcon={<Upload className="h-4 w-4" />}>
                      Select File
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Upload Status */}
          {uploadStatus === "success" && uploadedLectureId && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-6">
              <div className="flex items-start">
                <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
                <div className="ml-4 flex-1">
                  <h3 className="text-lg font-medium text-green-900 mb-2">
                    Upload Successful!
                  </h3>
                  <p className="text-green-800 mb-6 text-sm">
                    Your lecture has been processed and is ready for questioning.
                  </p>
                  <div className="flex flex-wrap gap-3">
                    <Button onClick={() => navigate(`/lecture/${uploadedLectureId}`)}>
                      Ask Questions
                    </Button>
                    <Button variant="secondary" onClick={resetUpload}>
                      Upload Another
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {uploadStatus === "error" && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <div className="flex items-start">
                <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="ml-4 flex-1">
                  <h3 className="text-lg font-medium text-red-900 mb-2">
                    Upload Failed
                  </h3>
                  <p className="text-red-800 mb-6 text-sm">
                    Please ensure your file is a valid audio or video format
                    (MP3, WAV, M4A, MP4, WebM, MOV) and under 1GB.
                  </p>
                  <Button variant="danger" onClick={resetUpload}>
                    Try Again
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Supported Formats</h3>
            <div className="space-y-6">
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                  <FileAudio className="h-4 w-4 text-green-600 mr-2" />
                  Audio Files
                </h4>
                <ul className="space-y-2 text-sm text-gray-500 ml-6 list-disc">
                  <li>MP3 (recommended)</li>
                  <li>WAV</li>
                  <li>M4A</li>
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                  <FileVideo className="h-4 w-4 text-blue-600 mr-2" />
                  Video Files
                </h4>
                <ul className="space-y-2 text-sm text-gray-500 ml-6 list-disc">
                  <li>MP4 (recommended)</li>
                  <li>WebM</li>
                  <li>MOV</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 rounded-2xl border border-blue-100 p-6">
            <h3 className="font-semibold text-blue-900 mb-4">Processing Info</h3>
            <ul className="space-y-3 text-sm text-blue-800">
              <li className="flex items-start">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                <span>Automatic transcription via speech-to-text</span>
              </li>
              <li className="flex items-start">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                <span>Cloud processing for speed</span>
              </li>
              <li className="flex items-start">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                <span>Max file size: 1GB</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;