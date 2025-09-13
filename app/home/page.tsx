"use client";
import { useState } from "react";
import SearchBar from "../components/SearchBar";
import SearchResult from "../components/SearchResults";

export default function SearchPage() {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  return (
    <div className="min-h-screen bg-white p-6">
      <div className="max-w-4xl mx-auto">
        <SearchBar onResults={setResults} onLoading={setLoading} />
        <SearchResult results={results} loading={loading} />
      </div>
    </div>
  );
}
