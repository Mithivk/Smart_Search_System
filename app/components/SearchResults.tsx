"use client";

import Skeleton from "./Skeleton";

interface ResultItem {
  id: string;
  score: number;
  metadata?: {
    title?: string;
    body?: string;
  };
}

interface SearchResultProps {
  results?: ResultItem[];
  loading?: boolean;
}

export default function SearchResult({ results = [], loading = false }: SearchResultProps) {
  if (loading) {
    return (
      <div className="mt-10 space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} />
        ))}
      </div>
    );
  }

  if (!results.length) {
    return (
      <p className="mt-10 text-center text-gray-500 text-lg">
        No results found. Try another search.
      </p>
    );
  }

  // Sort results by score (descending → higher score first)
  const sortedResults = [...results].sort((a, b) => b.score - a.score);

  return (
    <div className="mt-10 grid gap-6 md:grid-cols-2">
      {sortedResults.map((item, index) => (
        <div
          key={item.id}
          className="p-6 bg-white rounded-2xl shadow-md border border-black hover:shadow-lg transition"
        >
          <h3 className="text-xl font-semibold text-black">
            {index + 1}. {item.metadata?.title || "Untitled"}
          </h3>
          <p className="mt-2 text-gray-700 line-clamp-3">
            {item.metadata?.body || "No description available"}
          </p>
          <p className="mt-3 text-sm text-gray-500">🔢 Score: {item.score.toFixed(3)}</p>
        </div>
      ))}
    </div>
  );
}
