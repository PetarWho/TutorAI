import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { courseAPI, lectureAPI } from '../services/api';
import type { Course, Lecture } from '../services/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { 
  BookOpen, 
  Plus, 
  Search,
  Settings,
  GraduationCap,
  X,
} from 'lucide-react';
import { format } from 'date-fns';

const CourseManagement: React.FC = () => {
  const { user, token } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [courseLectures, setCourseLectures] = useState<Lecture[]>([]);
  const [allLectures, setAllLectures] = useState<Lecture[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showAddLectureForm, setShowAddLectureForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [newCourse, setNewCourse] = useState({ name: '', description: '' });

  useEffect(() => {
    const fetchCourses = async () => {
      if (!token) return;
      
      try {
        const response = await courseAPI.getCourses(token);
        setCourses(response);
      } catch (error) {
        console.error('Failed to fetch courses:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCourses();
  }, [token]);

  useEffect(() => {
    const fetchAllLectures = async () => {
      if (!token) return;
      
      try {
        const response = await lectureAPI.getMyLectures(token);
        setAllLectures(response.lectures);
      } catch (error) {
        console.error('Failed to fetch all lectures:', error);
      }
    };

    fetchAllLectures();
  }, [token]);

  useEffect(() => {
    const fetchCourseLectures = async () => {
      if (!selectedCourse || !token) return;
      
      try {
        const response = await courseAPI.getCourseLectures(selectedCourse.id, token);
        setCourseLectures(response.lectures);
      } catch (error) {
        console.error('Failed to fetch course lectures:', error);
      }
    };

    fetchCourseLectures();
  }, [selectedCourse, token]);

  const handleCreateCourse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    try {
      await courseAPI.create(newCourse, token);
      setNewCourse({ name: '', description: '' });
      setShowCreateForm(false);
      
      const response = await courseAPI.getCourses(token);
      setCourses(response);
    } catch (error: unknown) {
      console.error('Failed to create course:', error);
    }
  };

  const handleAddLecture = async (lectureId: string) => {
    if (!selectedCourse || !token) return;

    try {
      await courseAPI.addLectureToCourse(selectedCourse.id, lectureId, token);
      // Refresh course lectures
      const response = await courseAPI.getCourseLectures(selectedCourse.id, token);
      setCourseLectures(response.lectures);
      // Refresh courses to update lecture count
      const coursesResponse = await courseAPI.getCourses(token);
      setCourses(coursesResponse);
      setShowAddLectureForm(false);
    } catch (error) {
      console.error('Failed to add lecture to course:', error);
    }
  };

  const filteredCourses = courses.filter(course =>
    course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (course.description && course.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (!user) return <div>Please log in to manage courses.</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold leading-tight text-gray-900">
            Course Management
          </h2>
          <p className="text-gray-500 mt-1">Organize your lectures into structured courses.</p>
        </div>
        <Button onClick={() => setShowCreateForm(true)} leftIcon={<Plus className="h-4 w-4" />}>
          New Course
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Course List */}
        <div className="lg:col-span-1 flex flex-col h-[calc(100vh-200px)]">
          <div className="bg-white shadow-sm border border-gray-100 rounded-2xl flex flex-col h-full overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50/50 space-y-3">
              <h3 className="font-semibold text-gray-900">Your Courses</h3>
              <Input
                placeholder="Search courses..."
                icon={<Search className="h-4 w-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                </div>
              ) : filteredCourses.length === 0 ? (
                <div className="text-center py-10 px-4">
                  <GraduationCap className="mx-auto h-10 w-10 text-gray-300 mb-2" />
                  <p className="text-sm text-gray-500">No courses found</p>
                </div>
              ) : (
                filteredCourses.map((course) => (
                  <div
                    key={course.id}
                    className={`p-4 rounded-xl cursor-pointer transition-all ${
                      selectedCourse?.id === course.id
                        ? 'bg-blue-50 border-blue-200 ring-1 ring-blue-200 shadow-sm'
                        : 'bg-white border border-gray-100 hover:border-gray-200 hover:bg-gray-50'
                    }`}
                    onClick={() => setSelectedCourse(course)}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <h4 className={`font-semibold text-sm ${selectedCourse?.id === course.id ? 'text-blue-900' : 'text-gray-900'}`}>
                        {course.name}
                      </h4>
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                        {course.lecture_count}
                      </span>
                    </div>
                    {course.description && (
                      <p className="text-xs text-gray-500 line-clamp-2 mb-2">{course.description}</p>
                    )}
                    <div className="text-[10px] text-gray-400">
                      Updated {format(new Date(course.created_at), 'MMM d, yyyy')}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Course Detail */}
        <div className="lg:col-span-2">
          {selectedCourse ? (
            <div className="bg-white shadow-sm border border-gray-100 rounded-2xl h-full p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">{selectedCourse.name}</h3>
                  {selectedCourse.description && (
                    <p className="text-gray-500 mt-1">{selectedCourse.description}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => setShowAddLectureForm(true)} leftIcon={<Plus className="h-4 w-4" />}>
                    Add Lecture
                  </Button>
                  <Button variant="ghost" size="sm" leftIcon={<Settings className="h-4 w-4" />}>
                    Settings
                  </Button>
                </div>
              </div>

              <div className="border-t border-gray-100 pt-6">
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                  Lectures 
                  <span className="ml-2 text-xs font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                    {courseLectures.length}
                  </span>
                </h4>
                
                {courseLectures.length === 0 ? (
                  <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                    <BookOpen className="mx-auto h-10 w-10 text-gray-300 mb-3" />
                    <p className="text-sm text-gray-500">No lectures in this course yet.</p>
                    <Button variant="outline" size="sm" className="mt-4" onClick={() => setShowAddLectureForm(true)}>Add Lecture</Button>
                  </div>
                ) : (
                  <div className="grid gap-3">
                    {courseLectures.map((lecture) => (
                      <div key={lecture.lecture_id} className="group flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:border-blue-100 hover:shadow-sm transition-all">
                        <div className="flex items-center gap-3 overflow-hidden">
                          <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                             <BookOpen className="h-5 w-5" />
                          </div>
                          <div className="min-w-0">
                            <h5 className="text-sm font-medium text-gray-900 truncate">{lecture.title}</h5>
                            <p className="text-xs text-gray-500 truncate">{lecture.filename}</p>
                          </div>
                        </div>
                        <Link to={`/lecture/${lecture.lecture_id}`}>
                          <Button size="sm" variant="secondary" className="opacity-0 group-hover:opacity-100 transition-opacity">
                            View
                          </Button>
                        </Link>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white shadow-sm border border-gray-100 rounded-2xl h-full flex flex-col items-center justify-center p-8 text-center">
              <div className="p-4 bg-gray-50 rounded-full mb-4">
                 <GraduationCap className="h-12 w-12 text-gray-300" />
              </div>
              <h3 className="text-lg font-medium text-gray-900">Select a course</h3>
              <p className="text-gray-500 mt-1 max-w-sm">
                Choose a course from the sidebar to view its details and manage lectures
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Create Course Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm transition-opacity" onClick={() => setShowCreateForm(false)}></div>
          <div className="flex items-center justify-center min-h-screen p-4">
            <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-md p-6 transform transition-all">
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-lg font-bold text-gray-900">Create New Course</h3>
                <button onClick={() => setShowCreateForm(false)} className="text-gray-400 hover:text-gray-500">
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <form onSubmit={handleCreateCourse} className="space-y-4">
                <Input
                  label="Course Name"
                  id="name"
                  required
                  value={newCourse.name}
                  onChange={(e) => setNewCourse({ ...newCourse, name: e.target.value })}
                  placeholder="e.g., Advanced Biology"
                />
                
                <Textarea
                  label="Description (Optional)"
                  id="description"
                  rows={3}
                  value={newCourse.description}
                  onChange={(e) => setNewCourse({ ...newCourse, description: e.target.value })}
                  placeholder="What is this course about?"
                />

                <div className="flex gap-3 mt-6 pt-2">
                  <Button type="button" variant="secondary" className="flex-1" onClick={() => setShowCreateForm(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" className="flex-1">
                    Create Course
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Add Lecture Modal */}
      {showAddLectureForm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm transition-opacity" onClick={() => setShowAddLectureForm(false)}></div>
          <div className="flex items-center justify-center min-h-screen p-4">
            <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-2xl p-6 transform transition-all">
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-lg font-bold text-gray-900">Add Lecture to {selectedCourse?.name}</h3>
                <button onClick={() => setShowAddLectureForm(false)} className="text-gray-400 hover:text-gray-500">
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="max-h-96 overflow-y-auto">
                <h4 className="font-medium text-gray-900 mb-3">Available Lectures</h4>
                <div className="space-y-2">
                  {allLectures.filter(lecture => 
                    !courseLectures.some(courseLecture => courseLecture.lecture_id === lecture.lecture_id)
                  ).map((lecture) => (
                    <div key={lecture.lecture_id} className="flex items-center justify-between p-3 border border-gray-100 rounded-lg hover:bg-gray-50">
                      <div className="flex-1">
                        <h5 className="text-sm font-medium text-gray-900">{lecture.title}</h5>
                        <p className="text-xs text-gray-500">{lecture.filename}</p>
                      </div>
                      <Button 
                        size="sm" 
                        onClick={() => handleAddLecture(lecture.lecture_id)}
                        disabled={courseLectures.some(cl => cl.lecture_id === lecture.lecture_id)}
                      >
                        Add
                      </Button>
                    </div>
                  ))}
                  {allLectures.filter(lecture => 
                    !courseLectures.some(courseLecture => courseLecture.lecture_id === lecture.lecture_id)
                  ).length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      No available lectures to add
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseManagement;