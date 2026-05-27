import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import apiClient from "../api/client";

interface Lesson {
  id: string;
  title: string;
  description: string;
  topic: string;
  level: string;
}

export function Home() {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const response = await apiClient.get("/lessons");
        setLessons(response.data);
      } catch (error) {
        console.error("Failed to fetch lessons", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLessons();
  }, []);

  return (
    <div className="py-10">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Welcome to MathApp</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Learn math through active learning and adaptive lessons. Sign up or log in to get started.
        </p>
      </div>

      <div className="max-w-7xl mx-auto">
        <h2 className="text-2xl font-semibold mb-6">Available Lessons Catalog</h2>
        {isLoading ? (
          <div className="text-center text-gray-500 py-10">Loading lessons...</div>
        ) : lessons.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {lessons.map((lesson) => (
              <Link 
                key={lesson.id} 
                to={`/lessons/${lesson.id}`}
                className="block bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow hover:border-indigo-300"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold text-gray-900">{lesson.title}</h3>
                  <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs font-semibold rounded-full capitalize">
                    {lesson.level}
                  </span>
                </div>
                <p className="text-gray-600 mb-4 line-clamp-2">{lesson.description}</p>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500 capitalize bg-gray-100 px-2 py-1 rounded">
                    {lesson.topic}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-500 py-10 bg-white rounded-lg border border-dashed border-gray-300">
            No lessons available yet. Check back soon!
          </div>
        )}
      </div>
    </div>
  );
}
