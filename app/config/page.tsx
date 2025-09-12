"use client";

import { useState, useEffect } from "react";

export default function ConfigPage() {
  const [form, setForm] = useState({
    apiKey: "",
    environment: "production",
    accessToken: "",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    // Get user ID from token or session
    const token = localStorage.getItem('token');
    if (token) {
      try {
        // Simple JWT decode to get user ID (you might want to use a proper JWT library)
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUserId(payload.userId);
        
        // Load user's existing config
        fetchUserConfig(payload.userId);
      } catch (error) {
        console.error("Error decoding token:", error);
      }
    }
  }, []);

  const fetchUserConfig = async (userId: string) => {
    try {
      const res = await fetch(`/api/config?userId=${userId}`, {
        headers: { 
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
      });

      if (res.ok) {
        const data = await res.json();
        if (data.config) {
          setForm({
            apiKey: data.config.apiKey || "",
            environment: data.config.environment || "production",
            accessToken: data.config.accessToken || "",
          });
        }
      }
    } catch (error) {
      console.error("Error fetching config:", error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userId) {
      setMessage({ text: "User not authenticated", type: "error" });
      return;
    }

    setLoading(true);
    setMessage({ text: "", type: "" });

    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ ...form, userId }),
      });

      const data = await res.json();
      
      if (!res.ok) {
        setMessage({ text: data.error || "Failed to save configuration", type: "error" });
      } else {
        setMessage({ text: "Configuration saved successfully! ✅", type: "success" });
      }
    } catch (error) {
      setMessage({ text: "Network error. Please try again.", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-white flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-md mb-4">
            <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">App Configuration</h1>
          <p className="text-gray-600">Configure your Contentstack credentials</p>
        </div>
        
        {/* Form */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* API Key */}
            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <input
                type="text"
                id="apiKey"
                name="apiKey"
                value={form.apiKey}
                onChange={handleChange}
                placeholder="Enter your API key"
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 text-gray-900 px-3 py-2"
                required
                disabled={loading}
              />
            </div>

            {/* Contentstack Environment */}
            <div>
              <label htmlFor="environment" className="block text-sm font-medium text-gray-700 mb-2">
                Contentstack Environment
              </label>
              <select
                id="environment"
                name="environment"
                value={form.environment}
                onChange={handleChange}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring focus:ring-purple-200 text-gray-900 px-3 py-2"
                disabled={loading}
              >
                <option value="production">Production</option>
                <option value="development">Development</option>
                <option value="staging">Staging</option>
                <option value="preview">Preview</option>
              </select>
            </div>

            {/* Contentstack Access Token */}
            <div>
              <label htmlFor="accessToken" className="block text-sm font-medium text-gray-700 mb-2">
                Contentstack Access Token
              </label>
              <input
                type="password"
                id="accessToken"
                name="accessToken"
                value={form.accessToken}
                onChange={handleChange}
                placeholder="Enter your access token"
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 text-gray-900 px-3 py-2"
                required
                disabled={loading}
              />
            </div>

            {/* Message Display */}
            {message.text && (
              <div className={`p-3 rounded-md text-center ${
                message.type === "success" 
                  ? "bg-green-100 text-green-800 border border-green-200" 
                  : "bg-red-100 text-red-800 border border-red-200"
              }`}>
                {message.text}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading || !userId}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2.5 px-4 rounded-md font-medium hover:opacity-90 transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Saving..." : "Save Settings"}
            </button>
          </form>
        </div>
        
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Your configuration is stored securely and privately</p>
        </div>
      </div>
    </main>
  );
}