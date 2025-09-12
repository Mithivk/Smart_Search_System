"use client";

import Skeleton from "./Skeleton";

interface ResultItem {
  id: string;
  title: string;
  description: string;
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

  return (
    <div className="mt-10 grid gap-6 md:grid-cols-2">
      {results.map((item) => (
        <div
          key={item.id}
          className="p-6 bg-white rounded-2xl shadow-md border border-gray-100 hover:shadow-lg transition"
        >
          <h3 className="text-xl font-semibold text-gray-900">{item.title}</h3>
          <p className="mt-2 text-gray-600">{item.description}</p>
        </div>
      ))}
    </div>
  );
}
