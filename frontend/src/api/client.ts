import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000", // Base URL of the FastAPI backend
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor to add auth token if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
