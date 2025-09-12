import { ArrowRight } from "lucide-react";

const steps = [
  { id: 1, title: "Content Creation", desc: "Entries are created in Contentstack." },
  { id: 2, title: "Webhook Trigger", desc: "Webhook pushes changes (create/update/delete)." },
  { id: 3, title: "Vector Embedding", desc: "Content is embedded using LLM + stored in Pinecone." },
  { id: 4, title: "Search Query", desc: "User searches in any language." },
  { id: 5, title: "Contextual Results", desc: "Relevant entries returned, across languages." },
];

export default function FlowDiagram() {
  return (
    <section className="py-16 bg-gray-50">
      <h2 className="text-3xl font-semibold text-center mb-10">How It Works</h2>
      <div className="flex flex-col md:flex-row items-center justify-center gap-6 max-w-5xl mx-auto">
        {steps.map((s, i) => (
          <div key={s.id} className="flex items-center gap-4">
            <div className="p-6 bg-white rounded-2xl shadow-md w-52 text-center">
              <h3 className="font-bold text-lg">{s.title}</h3>
              <p className="text-gray-600 text-sm mt-2">{s.desc}</p>
            </div>
            {i < steps.length - 1 && <ArrowRight className="hidden md:block text-gray-400" />}
          </div>
        ))}
      </div>
    </section>
  );
}
