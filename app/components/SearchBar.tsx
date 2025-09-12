"use client";
import { useState } from "react";
import { Search } from "lucide-react";

interface SearchBarProps {
  onSearch: (query: string) => void;
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
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
