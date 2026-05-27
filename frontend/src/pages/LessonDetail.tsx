import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import apiClient from "../api/client";

interface Problem {
  id: string;
  question: string;
  difficulty: string;
  hint?: string;
  explanation?: string;
  answer?: string;
}

interface Lesson {
  id: string;
  title: string;
  description: string;
  explanation?: string;
  topic: string;
  level: string;
  problems: Problem[];
}

export function LessonDetail() {
  const { id } = useParams<{ id: string }>();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [feedbacks, setFeedbacks] = useState<Record<string, { is_correct: boolean; feedback: string; explanation?: string }>>({});
  const [submitting, setSubmitting] = useState<Record<string, boolean>>({});
  const [showHints, setShowHints] = useState<Record<string, boolean>>({});
  const [gaveUp, setGaveUp] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const fetchLesson = async () => {
      try {
        const response = await apiClient.get(`/lessons/${id}`);
        setLesson(response.data);
      } catch (err) {
        console.error("Failed to fetch lesson", err);
        setError("Could not load the lesson details.");
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      fetchLesson();
    }
  }, [id]);

  const handleAnswerChange = (problemId: string, val: string) => {
    setAnswers((prev) => ({ ...prev, [problemId]: val }));
  };

  const handleSubmit = async (problemId: string, e: React.FormEvent) => {
    e.preventDefault();
    if (!answers[problemId]) return;

    setSubmitting((prev) => ({ ...prev, [problemId]: true }));
    try {
      const response = await apiClient.post(`/problems/${problemId}/submit`, {
        problem_id: problemId,
        submitted_answer: answers[problemId]
      });
      setFeedbacks((prev) => ({ ...prev, [problemId]: response.data }));
    } catch (err: any) {
      console.error(err);
      if (err.response?.status === 401) {
        alert("You must be logged in to submit answers.");
      } else {
        alert("Failed to submit answer. Check console for details.");
      }
    } finally {
      setSubmitting((prev) => ({ ...prev, [problemId]: false }));
    }
  };

  if (isLoading) {
    return <div className="text-center py-10 mt-10">Loading lesson...</div>;
  }

  if (error || !lesson) {
    return (
      <div className="text-center py-10 mt-10 text-red-600">
        {error || "Lesson not found"}
        <div className="mt-4">
          <Link to="/" className="text-indigo-600 hover:underline">
            &larr; Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-10 px-4">
      <Link to="/" className="text-indigo-600 hover:text-indigo-800 mb-6 inline-block">
        &larr; Back to Catalog
      </Link>
      
      <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{lesson.title}</h1>
        <div className="flex gap-2 mb-6">
          <span className="bg-indigo-100 text-indigo-800 text-xs font-semibold px-2 py-1 rounded capitalize">
            {lesson.level}
          </span>
          <span className="bg-gray-100 text-gray-600 text-xs font-semibold px-2 py-1 rounded capitalize">
            {lesson.topic}
          </span>
        </div>
        <p className="text-gray-700 text-lg">{lesson.description}</p>
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-6">Practice Problems</h2>
      
      {lesson.problems && lesson.problems.length > 0 ? (
        <div className="space-y-6">
          {lesson.problems.map((problem, index) => (
            <div key={problem.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-start gap-4">
                <div className="bg-indigo-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0 mt-1">
                  {index + 1}
                </div>
                <div className="w-full">
                  <div className="flex justify-between">
                    <h3 className="text-xl font-medium text-gray-900 mb-3">{problem.question}</h3>
                    <span className="text-xs text-gray-500 capitalize bg-gray-100 px-2 py-1 rounded h-fit">
                      {problem.difficulty}
                    </span>
                  </div>
                  
                  {problem.hint && !showHints[problem.id] && (
                    <div className="mb-4">
                      <button
                        type="button"
                        onClick={() => setShowHints((prev) => ({ ...prev, [problem.id]: true }))}
                        className="text-sm font-medium text-indigo-600 hover:text-indigo-800 hover:underline"
                      >
                        Show Hint
                      </button>
                    </div>
                  )}
                  {problem.hint && showHints[problem.id] && (
                    <div className="bg-yellow-50 text-yellow-800 p-3 rounded text-sm mb-4">
                      <strong>Hint:</strong> {problem.hint}
                    </div>
                  )}

                  <form onSubmit={(e) => handleSubmit(problem.id, e)} className="mt-4">
                    <div className="flex gap-3">
                      <input
                        type="text"
                        placeholder="Your answer..."
                        value={answers[problem.id] || ""}
                        onChange={(e) => handleAnswerChange(problem.id, e.target.value)}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                        disabled={submitting[problem.id] || feedbacks[problem.id]?.is_correct || gaveUp[problem.id]}
                      />
                      <button
                        type="submit"
                        disabled={!answers[problem.id] || submitting[problem.id] || feedbacks[problem.id]?.is_correct || gaveUp[problem.id]}
                        className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                      >
                        {submitting[problem.id] ? "Checking..." : "Submit"}
                      </button>
                      <button
                        type="button"
                        onClick={() => setGaveUp(prev => ({ ...prev, [problem.id]: true }))}
                        disabled={feedbacks[problem.id]?.is_correct || gaveUp[problem.id]}
                        className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                      >
                        Give up
                      </button>
                    </div>
                  </form>

                  {gaveUp[problem.id] && (
                    <div className="mt-4 p-4 rounded-md bg-blue-50 text-blue-800 border border-blue-200">
                      <p className="font-medium text-lg">Correct Answer: {problem.answer}</p>
                      <div className="mt-2 text-sm pt-2 border-t border-blue-200">
                        <strong>Explanation:</strong> {problem.explanation || lesson.explanation || "No explanation provided for this problem."}
                      </div>
                    </div>
                  )}

                  {feedbacks[problem.id] && !gaveUp[problem.id] && (
                    <div className={`mt-4 p-4 rounded-md ${feedbacks[problem.id].is_correct ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
                      <p className="font-medium">{feedbacks[problem.id].feedback}</p>
                      {feedbacks[problem.id].is_correct && feedbacks[problem.id].explanation && (
                        <div className="mt-2 text-sm pt-2 border-t border-green-200">
                          <strong>Explanation:</strong> {feedbacks[problem.id].explanation}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-gray-500 bg-white p-6 rounded-lg border text-center">
          No practice problems available for this lesson.
        </div>
      )}
    </div>
  );
}
