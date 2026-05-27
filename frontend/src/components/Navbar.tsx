import { Link, useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";

export function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("auth_token");
  const isAuthenticated = !!token;

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex-shrink-0 flex items-center">
            <Link to="/" className="text-xl font-bold text-indigo-600">
              MathApp
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center text-gray-700 hover:text-indigo-600 px-3 py-2"
                >
                  <LogOut className="h-5 w-5 mr-1" />
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md font-medium"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="bg-indigo-600 text-white hover:bg-indigo-700 px-4 py-2 rounded-md font-medium"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
