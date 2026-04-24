"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { Concept } from "@/lib/api";

export default function KnowledgePage() {
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const url = selectedDomain === "all" ? "/concepts" : `/concepts?domain=${selectedDomain}`;
    apiFetch<Concept[]>(url).then(setConcepts).catch(() => {}).finally(() => setLoading(false));
  }, [selectedDomain]);

  const domains = [...new Set(concepts.map((c) => c.domain))];

  const domainColors: Record<string, string> = {
    data_structures: "#3b82f6",
    algorithms: "#22c55e",
    os: "#f59e0b",
    networks: "#a855f7",
    programming_languages: "#ef4444",
  };

  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-4 border-b border-[var(--border)]">
        <h2 className="text-lg font-semibold">Knowledge Graph</h2>
        <p className="text-sm text-[var(--muted)]">{concepts.length} concepts</p>
      </header>

      {/* Domain filter */}
      <div className="px-6 py-3 border-b border-[var(--border)] flex gap-2 overflow-x-auto">
        <button
          onClick={() => setSelectedDomain("all")}
          className={`px-3 py-1 rounded-lg text-xs whitespace-nowrap transition-colors ${
            selectedDomain === "all"
              ? "bg-[var(--accent)] text-white"
              : "bg-[var(--card)] text-[var(--muted)] hover:bg-[var(--border)]"
          }`}
        >
          All
        </button>
        {domains.map((d) => (
          <button
            key={d}
            onClick={() => setSelectedDomain(d)}
            className={`px-3 py-1 rounded-lg text-xs whitespace-nowrap transition-colors ${
              selectedDomain === d
                ? "text-white"
                : "bg-[var(--card)] text-[var(--muted)] hover:bg-[var(--border)]"
            }`}
            style={selectedDomain === d ? { backgroundColor: domainColors[d] || "var(--accent)" } : {}}
          >
            {d}
          </button>
        ))}
      </div>

      {/* Concept grid */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <p className="text-center text-[var(--muted)] py-12">Loading...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {concepts.map((c) => (
              <div
                key={c.id}
                className="bg-[var(--card)] rounded-xl p-4 border border-[var(--border)] hover:border-[var(--accent)] transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-sm font-medium">{c.name}</h3>
                  <span
                    className="text-xs px-2 py-0.5 rounded-full"
                    style={{
                      backgroundColor: (domainColors[c.domain] || "#666") + "22",
                      color: domainColors[c.domain] || "#999",
                    }}
                  >
                    {c.domain}
                  </span>
                </div>
                {c.description && (
                  <p className="text-xs text-[var(--muted)] mt-2 line-clamp-2">{c.description}</p>
                )}
                <div className="flex items-center gap-3 mt-3">
                  <div className="flex-1">
                    <div className="h-1.5 bg-[var(--border)] rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${(c.difficulty || 0.5) * 100}%`,
                          backgroundColor: domainColors[c.domain] || "var(--accent)",
                        }}
                      />
                    </div>
                  </div>
                  <span className="text-xs text-[var(--muted)]">
                    diff {(c.difficulty * 100).toFixed(0)}%
                  </span>
                  {c.mastery_level != null && (
                    <span className="text-xs text-[var(--success)]">
                      {(c.mastery_level * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
