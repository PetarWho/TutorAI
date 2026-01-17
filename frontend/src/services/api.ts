import axios from 'axios';
import type { AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8069';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API responses
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface Course {
  id: number;
  name: string;
  description?: string;
  user_id: number;
  created_at: string;
  lecture_count: number;
}

export interface Lecture {
  id: number;
  lecture_id: string;
  title: string;
  user_id: number;
  course_id?: number;
  filename: string;
  upload_date: string;
  duration?: number;
  qdrant_collection: string;
}

export interface QuestionRequest {
  question: string;
}

export interface AnswerResponse {
  answer: string;
  sources: TimestampSource[];
}

export interface TimestampSource {
  text: string;
  start_time: number;
  end_time: number;
  start_str: string;
  end_str: string;
  video_timestamp: string;
}

export interface TranscriptSegment {
  start_time: number;
  end_time: number;
  text: string;
  start_str: string;
  end_str: string;
}

export interface TranscriptResponse {
  segments: TranscriptSegment[];
  total_duration: number;
}

export interface PDFRequest {
  type: 'transcript' | 'summary';
}

export interface PDFResponse {
  pdf_path: string;
  filename: string;
}

export interface MultiLectureSearchRequest {
  query: string;
  course_id?: number;
  limit?: number;
}

export interface MultiLectureSource {
  lecture_id: string;
  lecture_filename: string;
  text: string;
  start_time: number;
  end_time: number;
  start_str: string;
  end_str: string;
  video_timestamp: string;
  course_name?: string;
}

// Auth API
export const authAPI = {
  register: async (userData: { email: string; username: string; password: string; full_name?: string }) => {
    const response: AxiosResponse<User> = await api.post('/auth/register', userData);
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response: AxiosResponse<{ access_token: string; token_type: string }> = await api.post(
      '/auth/login',
      new URLSearchParams({ username: email, password }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    return response.data;
  },

  getCurrentUser: async (token: string) => {
    const response: AxiosResponse<User> = await api.get('/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },
};

// Lecture API
export const lectureAPI = {
  upload: async (file: File, token: string, onProgress?: (progress: number) => void, lectureName?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (lectureName && lectureName.trim()) {
      formData.append('title', lectureName.trim());
    }

    const response: AxiosResponse<{ lecture_id: string }> = await api.post('/lectures/upload', formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
      maxContentLength: 1024 * 1024 * 1024, // 1GB
      maxBodyLength: 1024 * 1024 * 1024, // 1GB
    });
    return response.data;
  },

  getMyLectures: async (token: string) => {
    const response: AxiosResponse<{ lectures: Lecture[] }> = await api.get('/lectures/my-lectures', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  askQuestion: async (lectureId: string, question: string, token: string) => {
    const response: AxiosResponse<AnswerResponse> = await api.post(
      `/lectures/${lectureId}/ask`,
      { question },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  getTranscript: async (lectureId: string, token: string) => {
    const response: AxiosResponse<TranscriptResponse> = await api.get(`/lectures/${lectureId}/transcript`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  searchTranscript: async (lectureId: string, query: string, limit: number = 5, token: string) => {
    const response: AxiosResponse<{ results: unknown[]; query: string; total_found: number }> = await api.get(
      `/lectures/${lectureId}/search?q=${encodeURIComponent(query)}&limit=${limit}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  generatePDF: async (lectureId: string, type: 'transcript' | 'summary', token: string) => {
    const response: AxiosResponse<PDFResponse> = await api.post(
      `/lectures/${lectureId}/pdf`,
      { type },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  downloadPDF: async (lectureId: string, filename: string, token: string) => {
    const response = await api.get(`/lectures/${lectureId}/pdf/${filename}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      responseType: 'blob',
    });
    return response;
  },

  getLectureDetails: async (lectureId: string, token: string) => {
    const response: AxiosResponse<Lecture> = await api.get(`/lectures/${lectureId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },
};

// Course API
export const courseAPI = {
  create: async (courseData: { name: string; description?: string }, token: string) => {
    const response: AxiosResponse<Course> = await api.post('/courses/', courseData, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  getCourses: async (token: string) => {
    const response: AxiosResponse<Course[]> = await api.get('/courses/', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  addLectureToCourse: async (courseId: number, lectureId: string, token: string) => {
    const response: AxiosResponse<{ message: string }> = await api.post(
      `/courses/${courseId}/lectures`,
      { lecture_id: lectureId },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  getCourseLectures: async (courseId: number, token: string) => {
    const response: AxiosResponse<{ lectures: Lecture[] }> = await api.get(`/courses/${courseId}/lectures`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  searchMultipleLectures: async (searchData: MultiLectureSearchRequest, token: string) => {
    const response: AxiosResponse<{ results: MultiLectureSource[]; query: string; total_found: number }> = await api.post(
      '/courses/search',
      searchData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },
};

export default api;
