import { notFound } from "next/navigation";

// Dummy function – replace with real fetch from Contentstack
async function getEntry(uid: string) {
  // This should query Contentstack by UID
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/entries/${uid}`);
  if (!res.ok) return null;
  return res.json();
}

export default async function EntryPage({ params }: { params: { uid: string } }) {
  const entry = await getEntry(params.uid);

  if (!entry) {
    notFound();
  }

  return (
    <main className="p-10 space-y-6">
      <h1 className="text-3xl font-bold">{entry.title}</h1>
      <p className="text-gray-600">UID: {params.uid}</p>

      <div className="prose max-w-none">
        {entry.body ? (
          <div dangerouslySetInnerHTML={{ __html: entry.body }} />
        ) : (
          <p>No content available.</p>
        )}
      </div>
    </main>
  );
}
