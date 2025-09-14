"use client";
import { useState } from "react";
import { Search } from "lucide-react";

interface SearchBarProps {
  onResults: (results: any[]) => void; // ✅ pass results to parent
  onLoading?: (loading: boolean) => void;
}

export default function SearchBar({ onResults, onLoading }: SearchBarProps) {
  const [query, setQuery] = useState("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      onLoading?.(true);

      const res = await fetch("https://a7eb14f3d131.ngrok-free.app/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query, top_k: 5 }),
      });

      if (!res.ok) throw new Error(`Search failed: ${res.statusText}`);

      const data = await res.json();
      console.log("🔍 Search results:", data);

      onResults(data.results || []); // ✅ send results to parent
    } catch (err) {
      console.error("❌ Error during search:", err);
      onResults([]);
    } finally {
      onLoading?.(false);
    }
  };

  return (
    <form
      onSubmit={handleSearch}
      className="flex items-center w-full max-w-2xl mx-auto mt-8 bg-white rounded-full shadow-md border border-gray-200 px-4 py-2"
    >
      <Search className="h-5 w-5 text-gray-400 mr-2" />
      <input
        type="text"
        placeholder="Search across your entries..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="flex-1 bg-transparent focus:outline-none text-gray-700 placeholder-gray-400"
      />
      <button
        type="submit"
        className="px-5 py-2 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium hover:shadow-md hover:scale-105 transition"
      >
        Search
      </button>
    </form>
  );
}
