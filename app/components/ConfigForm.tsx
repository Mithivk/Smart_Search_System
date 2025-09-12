"use client";

import { useState } from "react";

export default function ConfigPage() {
  const [form, setForm] = useState({
    apiKey: "",
    webhookUrl: "",
    accessToken: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Submitted config:", form);
    // TODO: Send to backend
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-xl p-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center">
          Configuration Settings
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* API Key */}
          <div>
            <label
              htmlFor="apiKey"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              API Key
            </label>
            <input
              type="text"
              id="apiKey"
              name="apiKey"
              value={form.apiKey}
              onChange={handleChange}
              placeholder="Enter your API key"
              className="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 text-gray-900 px-4 py-2"
            />
          </div>

          {/* Contentstack Environment */}
          <div>
            <label
              htmlFor="webhookUrl"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Contentstack Environment
            </label>
            <input
              type="text"
              id="webhookUrl"
              name="webhookUrl"
              value={form.webhookUrl}
              onChange={handleChange}
              placeholder="production"
              className="w-full rounded-lg border-gray-300 shadow-sm focus:border-purple-500 focus:ring focus:ring-purple-200 text-gray-900 px-4 py-2"
            />
          </div>

          {/* Contentstack Access Token */}
          <div>
            <label
              htmlFor="accessToken"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Contentstack Access Token
            </label>
            <input
              type="password"
              id="accessToken"
              name="accessToken"
              value={form.accessToken}
              onChange={handleChange}
              placeholder="Enter your Contentstack access token"
              className="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 text-gray-900 px-4 py-2"
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-6 rounded-xl font-semibold shadow-md hover:opacity-90 transition"
          >
            Save Settings
          </button>
        </form>
      </div>
    </main>
  );
}