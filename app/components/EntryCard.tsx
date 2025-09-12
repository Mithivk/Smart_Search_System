import Link from "next/link";

export default function EntryCard({ entry }: { entry: any }) {
  return (
    <div className="p-4 border rounded-lg shadow-sm hover:shadow-md transition">
      <h2 className="text-xl font-semibold">{entry.title}</h2>
      <p className="text-gray-500">Lang: {entry.locale}</p>
      <p className="line-clamp-2 text-gray-700">{entry.body}</p>
      <Link
        href={`/entries/${entry.uid}`}
        className="text-blue-600 hover:underline mt-2 block"
      >
        View details →
      </Link>
    </div>
  );
}
