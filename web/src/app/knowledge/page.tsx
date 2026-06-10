"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Network, Filter, Search, Tag, Cpu, Database, Globe, Code } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Concept } from "@/lib/api";

const DOMAIN_ICONS: Record<string, any> = {
  data_structures: Database,
  algorithms: Cpu,
  os: Globe,
  networks: Network,
  programming_languages: Code,
};

const DOMAIN_COLORS: Record<string, string> = {
  data_structures: "#3b82f6",
  algorithms: "#22c55e",
  os: "#f59e0b",
  networks: "#a855f7",
  programming_languages: "#ef4444",
};

const DOMAIN_NAMES: Record<string, string> = {
  data_structures: "数据结构",
  algorithms: "算法",
  os: "操作系统",
  networks: "计算机网络",
  programming_languages: "编程语言",
};

export default function KnowledgePage() {
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const url = selectedDomain === "all" ? "/concepts" : `/concepts?domain=${selectedDomain}`;
    apiFetch<Concept[]>(url).then(setConcepts).catch(() => {}).finally(() => setLoading(false));
  }, [selectedDomain]);

  const domains = [...new Set(concepts.map((c) => c.domain))];

  return (
    <div className="flex flex-col h-full bg-[var(--background)]">
      <header className="px-8 py-6 border-b border-[var(--border)] bg-[var(--background)]/80 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Network size={20} className="text-[var(--accent)]" />
            <h2 className="text-xl font-bold tracking-tight">Knowledge Space</h2>
          </div>
          <p className="text-xs font-bold text-[var(--muted)] uppercase tracking-widest">{concepts.length} concepts indexed</p>
        </div>
      </header>

      {/* Domain filter */}
      <div className="px-8 py-4 border-b border-[var(--border)] flex items-center gap-4 bg-black/10 overflow-hidden">
        <div className="flex items-center gap-2 text-[var(--muted)] shrink-0">
          <Filter size={14} />
          <span className="text-[10px] font-bold uppercase tracking-wider">Filter</span>
        </div>
        <div className="flex gap-2 overflow-x-auto pb-1 custom-scrollbar">
          <button
            onClick={() => setSelectedDomain("all")}
            className={cn(
              "px-4 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border",
              selectedDomain === "all"
                ? "bg-[var(--accent)] border-[var(--accent)] text-white shadow-lg shadow-[var(--accent)]/20"
                : "bg-[var(--card)] border-[var(--border)] text-[var(--muted)] hover:border-[var(--muted)]"
            )}
          >
            All Areas
          </button>
          {domains.map((d) => {
            const Icon = DOMAIN_ICONS[d] || Tag;
            return (
              <button
                key={d}
                onClick={() => setSelectedDomain(d)}
                className={cn(
                  "flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border",
                  selectedDomain === d
                    ? "text-white shadow-lg"
                    : "bg-[var(--card)] border-[var(--border)] text-[var(--muted)] hover:border-[var(--muted)]"
                )}
                style={selectedDomain === d ? { 
                  backgroundColor: DOMAIN_COLORS[d] || "var(--accent)",
                  borderColor: DOMAIN_COLORS[d] || "var(--accent)",
                  boxShadow: `0 10px 15px -3px ${(DOMAIN_COLORS[d] || "#3b82f6")}33`
                } : {}}
              >
                <Icon size={12} />
                <span className="capitalize">{d.replace("_", " ")}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Concept grid */}
      <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
        {loading ? (
          <div className="flex items-center justify-center h-64 animate-pulse">
            <div className="w-8 h-8 border-2 border-[var(--accent)] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {concepts.map((c) => {
              const Icon = DOMAIN_ICONS[c.domain] || Tag;
              const color = DOMAIN_COLORS[c.domain] || "var(--accent)";
              return (
                <div
                  key={c.id}
                  role="button"
                  tabIndex={0}
                  onClick={() => router.push(`/?ask=${encodeURIComponent(c.name)}`)}
                  onKeyDown={(e) => e.key === "Enter" && router.push(`/?ask=${encodeURIComponent(c.name)}`)}
                  className="group bg-[var(--card)] rounded-2xl p-5 border border-[var(--border)] hover:border-[var(--accent)]/50 transition-all hover:shadow-xl hover:shadow-[var(--accent)]/5 cursor-pointer"
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex flex-col gap-1">
                      <h3 className="text-sm font-bold group-hover:text-[var(--accent)] transition-colors">{c.name}</h3>
                      <div className="flex items-center gap-1.5">
                        <Icon size={10} style={{ color }} />
                        <span className="text-[9px] font-bold uppercase tracking-wider opacity-60" style={{ color }}>
                          {DOMAIN_NAMES[c.domain] || c.domain.replace("_", " ")}
                        </span>
                      </div>
                    </div>
                    {c.mastery_level != null && (
                      <div className="flex flex-col items-end">
                        <span className="text-[10px] font-black text-[var(--success)]">
                          {(c.mastery_level * 100).toFixed(0)}%
                        </span>
                        <span className="text-[8px] text-[var(--muted)] font-bold uppercase tracking-tighter">掌握度</span>
                      </div>
                    )}
                  </div>
                  {c.description && (
                    <p className="text-xs text-[var(--muted)] leading-relaxed line-clamp-2 mb-4">
                      {c.description}
                    </p>
                  )}
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-[9px] font-bold uppercase tracking-tighter text-[var(--muted)] opacity-60">
                      <span>难度</span>
                      <span>{(c.difficulty * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-1 bg-black/20 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{
                          width: `${(c.difficulty || 0.5) * 100}%`,
                          backgroundColor: color,
                        }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
