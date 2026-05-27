import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import apiClient from "../api/client";

export function Signup() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      // 1. Sign up the user
      await apiClient.post("/auth/signup", {
        email,
        username: email.split("@")[0], // Derive a basic username from email
        password,
      });

      // 2. Sign in to get token
      const response = await apiClient.post("/auth/signin", {
        username: email,
        password: password,
      });

      localStorage.setItem("auth_token", response.data.access_token);
      navigate("/");
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((e: any) => e.msg).join(", "));
      } else {
        setError(detail || "An error occurred during sign up. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-8 border border-gray-200 rounded-lg shadow-sm">
      <h2 className="text-2xl font-bold text-center mb-6">Sign Up</h2>
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {isLoading ? "Signing up..." : "Sign Up"}
        </button>
      </form>
      <div className="mt-4 text-center text-sm text-gray-600">
        Already have an account? <Link to="/login" className="text-indigo-600 hover:text-indigo-500">Login</Link>
      </div>
    </div>
  );
}
