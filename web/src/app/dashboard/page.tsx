"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { AnalyticsOverview, WeakArea, Recommendation, DomainSummary } from "@/lib/api";

export default function DashboardPage() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [weakAreas, setWeakAreas] = useState<WeakArea[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [domains, setDomains] = useState<DomainSummary[]>([]);

  useEffect(() => {
    const uid = "default";
    apiFetch<AnalyticsOverview>(`/analytics/${uid}/overview`).then(setOverview).catch(() => {});
    apiFetch<WeakArea[]>(`/analytics/${uid}/weak-areas?limit=8`).then(setWeakAreas).catch(() => {});
    apiFetch<Recommendation[]>(`/analytics/${uid}/recommendations`).then(setRecommendations).catch(() => {});
    apiFetch<DomainSummary[]>(`/analytics/${uid}/domains`).then(setDomains).catch(() => {});
  }, []);

  const masteryBar = (pct: number, width = 100) => {
    const filled = Math.round(width * pct);
    return (
      <div className="h-2 bg-[var(--border)] rounded-full overflow-hidden" style={{ width }}>
        <div className="h-full bg-[var(--accent)] rounded-full" style={{ width: filled }} />
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-4 border-b border-[var(--border)]">
        <h2 className="text-lg font-semibold">Dashboard</h2>
        <p className="text-sm text-[var(--muted)]">Your learning progress</p>
      </header>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Overview cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {overview ? (
            <>
              <StatCard label="Total Concepts" value={overview.total_concepts} />
              <StatCard label="Mastered" value={overview.mastered} color="var(--success)" />
              <StatCard label="Due Reviews" value={overview.due_reviews} color="var(--warning)" />
              <StatCard label="Avg Mastery" value={`${(overview.avg_mastery * 100).toFixed(0)}%`} />
            </>
          ) : (
            <p className="col-span-4 text-center text-[var(--muted)] py-8">Loading...</p>
          )}
        </div>

        {/* Mastery distribution */}
        {overview && overview.total_concepts > 0 && (
          <div className="bg-[var(--card)] rounded-xl p-5 border border-[var(--border)]">
            <h3 className="text-sm font-medium mb-4">Mastery Distribution</h3>
            <div className="flex gap-2 h-6 rounded-full overflow-hidden">
              {overview.mastery_distribution.mastered > 0 && (
                <div
                  className="bg-[var(--success)] flex items-center justify-center text-xs"
                  style={{
                    flex: overview.mastery_distribution.mastered,
                  }}
                >
                  {overview.mastery_distribution.mastered}
                </div>
              )}
              {overview.mastery_distribution.learning > 0 && (
                <div
                  className="bg-[var(--accent)] flex items-center justify-center text-xs"
                  style={{ flex: overview.mastery_distribution.learning }}
                >
                  {overview.mastery_distribution.learning}
                </div>
              )}
              {overview.mastery_distribution.new > 0 && (
                <div
                  className="bg-[var(--border)] flex items-center justify-center text-xs"
                  style={{ flex: overview.mastery_distribution.new }}
                >
                  {overview.mastery_distribution.new}
                </div>
              )}
            </div>
            <div className="flex gap-4 mt-2 text-xs text-[var(--muted)]">
              <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-[var(--success)] inline-block" /> Mastered</span>
              <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-[var(--accent)] inline-block" /> Learning</span>
              <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-[var(--border)] inline-block" /> New</span>
            </div>
          </div>
        )}

        {/* Domain mastery */}
        {domains.length > 0 && (
          <div className="bg-[var(--card)] rounded-xl p-5 border border-[var(--border)]">
            <h3 className="text-sm font-medium mb-4">Domain Mastery</h3>
            <div className="space-y-3">
              {domains.map((d) => (
                <div key={d.domain} className="flex items-center gap-3">
                  <span className="text-xs w-32 text-[var(--muted)] truncate">{d.domain}</span>
                  {masteryBar(d.avg_mastery, 200)}
                  <span className="text-xs w-12 text-right">{(d.avg_mastery * 100).toFixed(0)}%</span>
                  <span className="text-xs text-[var(--muted)]">{d.concepts} concepts</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-4">
          {/* Weak areas */}
          {weakAreas.length > 0 && (
            <div className="bg-[var(--card)] rounded-xl p-5 border border-[var(--border)]">
              <h3 className="text-sm font-medium mb-3">Weak Areas</h3>
              <div className="space-y-2">
                {weakAreas.map((w) => (
                  <div key={w.concept_id} className="flex items-center gap-2">
                    <span className="text-sm flex-1">{w.concept_name}</span>
                    <span className="text-xs text-[var(--muted)]">{w.domain}</span>
                    {masteryBar(w.mastery, 60)}
                    <span className="text-xs w-10 text-right">{(w.mastery * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <div className="bg-[var(--card)] rounded-xl p-5 border border-[var(--border)]">
              <h3 className="text-sm font-medium mb-3">Recommended Next</h3>
              <div className="space-y-2">
                {recommendations.map((r) => (
                  <div key={r.concept_id} className="p-2 rounded-lg hover:bg-[var(--border)] transition-colors">
                    <p className="text-sm font-medium">{r.name}</p>
                    <p className="text-xs text-[var(--muted)]">
                      {r.domain} · difficulty {r.difficulty.toFixed(1)}
                      {r.prerequisites.length > 0 && ` · prereqs: ${r.prerequisites.join(", ")}`}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="bg-[var(--card)] rounded-xl p-4 border border-[var(--border)]">
      <p className="text-xs text-[var(--muted)]">{label}</p>
      <p className="text-2xl font-bold mt-1" style={color ? { color } : undefined}>
        {value}
      </p>
    </div>
  );
}
