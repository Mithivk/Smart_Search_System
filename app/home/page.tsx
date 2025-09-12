"use client";
import SearchBar from "../components/SearchBar";
import SearchResult from "../components/SearchResults";
import { useState } from "react";

export default function HomePage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  const handleSearch = async (query: string) => {
    setLoading(true);
    // Replace with real API call
    setTimeout(() => {
      setResults([
        { id: "1", title: "Sample Result", description: "This is a test description." },
      ]);
      setLoading(false);
    }, 1500);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 px-6 py-12">
      <div className="max-w-5xl mx-auto text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">
          Search Your Content
        </h1>
        <SearchBar onSearch={handleSearch} />
        <SearchResult results={results} loading={loading} />
      </div>
    </main>
  );
}
