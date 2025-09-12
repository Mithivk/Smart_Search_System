"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Eye, EyeOff, Mail, Lock, Loader2 } from "lucide-react";

export default function AuthForm({ type }: { type: "signin" | "signup" }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const res = await fetch(`/api/auth/${type}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setMessage(data.error || "Something went wrong");
      } else {
        setMessage(type === "signup" ? "Account created ✅" : "Signed in ✅");
        if (data.token) {
          localStorage.setItem("token", data.token);
          
          // Use setTimeout to ensure state updates complete before redirect
          setTimeout(() => {
            if (type === "signup") {
              router.push("/config");
            } else {
              // For signin, redirect to dashboard or home page
              router.push("/config");
            }
          }, 100);
        }
      }
    } catch (error) {
      setMessage("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-white rounded-xl shadow-lg p-8 space-y-6 border border-gray-200"
      >
        <h2 className="text-2xl font-bold text-gray-900 text-center">
          {type === "signup" ? "Create Your Account" : "Sign In to Your Account"}
        </h2>

        <div className="space-y-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail className="h-5 w-5 text-gray-500" />
            </div>
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
              required
              disabled={loading}
            />
          </div>

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock className="h-5 w-5 text-gray-500" />
            </div>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-10 pr-12 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent"
              required
              disabled={loading}
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5 text-gray-600 hover:text-gray-800" />
              ) : (
                <Eye className="h-5 w-5 text-gray-600 hover:text-gray-800" />
              )}
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg hover:opacity-90 transition-opacity flex items-center justify-center font-medium"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin mr-2 h-5 w-5" />
              {type === "signup" ? "Creating Account..." : "Signing In..."}
            </>
          ) : (
            type === "signup" ? "Create Account" : "Sign In"
          )}
        </button>

        {message && (
          <div className={`p-3 rounded-lg text-center ${
            message.includes("✅") 
              ? "bg-green-100 text-green-800 border border-green-300" 
              : "bg-red-100 text-red-800 border border-red-300"
          }`}>
            {message}
            {message.includes("✅") && (
              <p className="text-sm mt-1">
                Redirecting{type === "signup" ? " to configuration" : ""}...
              </p>
            )}
          </div>
        )}

        <div className="text-center text-sm text-gray-700 pt-4 border-t border-gray-200">
          {type === "signup" 
            ? "Already have an account? " 
            : "Don't have an account? "
          }
          <a 
            href={type === "signup" ? "/signin" : "/signup"} 
            className="text-purple-700 hover:text-purple-900 font-medium transition-colors"
          >
            {type === "signup" ? "Sign in" : "Sign up"}
          </a>
        </div>
      </form>
    </div>
  );
}