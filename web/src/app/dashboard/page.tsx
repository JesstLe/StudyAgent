"use client";

import { useEffect, useState } from "react";
import { 
  BarChart3, 
  Brain, 
  CheckCircle2, 
  Clock, 
  Layers, 
  Target, 
  Zap,
  TrendingUp,
  BookOpen
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";
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
    return (
      <div className="h-1.5 bg-[var(--border)] rounded-full overflow-hidden" style={{ width }}>
        <div 
          className="h-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-hover)] rounded-full transition-all duration-500" 
          style={{ width: `${pct * 100}%` }} 
        />
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-[var(--background)]">
      <header className="px-8 py-6 border-b border-[var(--border)] bg-[var(--background)]/80 backdrop-blur-md sticky top-0 z-10">
        <h2 className="text-xl font-bold tracking-tight">Learning Dashboard</h2>
        <p className="text-sm text-[var(--muted)]">Track your mastery and focus areas</p>
      </header>

      <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
        {/* Overview cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {overview ? (
            <>
              <StatCard 
                label="知识点总数" 
                value={overview.total_concepts} 
                icon={<BookOpen size={20} />} 
              />
              <StatCard 
                label="已掌握" 
                value={overview.mastered} 
                icon={<CheckCircle2 size={20} />} 
                color="text-[var(--success)]"
              />
              <StatCard 
                label="待复习" 
                value={overview.due_reviews} 
                icon={<Clock size={20} />} 
                color="text-[var(--warning)]"
              />
              <StatCard 
                label="平均掌握度" 
                value={`${(overview.avg_mastery * 100).toFixed(0)}%`} 
                icon={<TrendingUp size={20} />} 
              />
            </>
          ) : (
            Array(4).fill(0).map((_, i) => (
              <div key={i} className="h-24 bg-[var(--card)] rounded-2xl animate-pulse border border-[var(--border)]" />
            ))
          )}
        </div>

        {/* Mastery distribution */}
        {overview && overview.total_concepts > 0 && (
          <div className="bg-[var(--card)] rounded-2xl p-6 border border-[var(--border)] shadow-sm">
            <div className="flex items-center gap-2 mb-6">
              <Layers size={18} className="text-[var(--accent)]" />
              <h3 className="text-sm font-semibold uppercase tracking-wider">Mastery Distribution</h3>
            </div>
            <div className="flex gap-1.5 h-8 rounded-xl overflow-hidden p-1 bg-black/20">
              {overview.mastery_distribution.mastered > 0 && (
                <div
                  className="bg-[var(--success)] rounded-lg flex items-center justify-center text-[10px] font-bold text-black shadow-inner"
                  style={{ flex: overview.mastery_distribution.mastered }}
                >
                  {overview.mastery_distribution.mastered}
                </div>
              )}
              {overview.mastery_distribution.learning > 0 && (
                <div
                  className="bg-[var(--accent)] rounded-lg flex items-center justify-center text-[10px] font-bold text-white shadow-inner"
                  style={{ flex: overview.mastery_distribution.learning }}
                >
                  {overview.mastery_distribution.learning}
                </div>
              )}
              {overview.mastery_distribution.new > 0 && (
                <div
                  className="bg-[var(--border)] rounded-lg flex items-center justify-center text-[10px] font-bold text-[var(--muted)]"
                  style={{ flex: overview.mastery_distribution.new }}
                >
                  {overview.mastery_distribution.new}
                </div>
              )}
            </div>
            <div className="flex flex-wrap gap-6 mt-4 text-[11px] font-medium text-[var(--muted)]">
              <span className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--success)]" /> Mastered</span>
              <span className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--accent)]" /> Learning</span>
              <span className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--border)]" /> New</span>
            </div>
          </div>
        )}

        {/* Domain mastery */}
        {domains.length > 0 && (
          <div className="bg-[var(--card)] rounded-2xl p-6 border border-[var(--border)] shadow-sm">
            <div className="flex items-center gap-2 mb-6">
              <Target size={18} className="text-[var(--accent)]" />
              <h3 className="text-sm font-semibold uppercase tracking-wider">Domain Mastery</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-4">
              {domains.map((d) => (
                <div key={d.domain} className="group">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-sm font-medium group-hover:text-[var(--accent)] transition-colors">{d.domain}</span>
                    <span className="text-xs font-bold">{(d.avg_mastery * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1">
                      {masteryBar(d.avg_mastery, 100)}
                    </div>
                    <span className="text-[10px] text-[var(--muted)] uppercase tracking-tighter w-20 text-right">{d.concepts} concepts</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Weak areas */}
          {weakAreas.length > 0 && (
            <div className="bg-[var(--card)] rounded-2xl p-6 border border-[var(--border)] shadow-sm">
              <div className="flex items-center gap-2 mb-4 text-[var(--danger)]">
                <Zap size={18} />
                <h3 className="text-sm font-semibold uppercase tracking-wider">需要关注</h3>
              </div>
              <div className="space-y-3">
                {weakAreas.map((w) => (
                  <div key={w.concept_id} className="flex items-center gap-4 p-3 rounded-xl hover:bg-black/20 transition-colors border border-transparent hover:border-[var(--border)]">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{w.concept_name}</p>
                      <p className="text-[10px] text-[var(--muted)] uppercase tracking-wider mt-0.5">{w.domain}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      {masteryBar(w.mastery, 60)}
                      <span className="text-xs font-bold text-[var(--danger)] w-10 text-right">{(w.mastery * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <div className="bg-[var(--card)] rounded-2xl p-6 border border-[var(--border)] shadow-sm">
              <div className="flex items-center gap-2 mb-4 text-[var(--accent)]">
                <Brain size={18} />
                <h3 className="text-sm font-semibold uppercase tracking-wider">学习建议</h3>
              </div>
              <div className="space-y-3">
                {recommendations.map((r) => (
                  <div key={r.concept_id} className="p-4 rounded-xl bg-black/20 hover:bg-black/30 transition-all border border-[var(--border)] hover:border-[var(--accent)] group">
                    <div className="flex justify-between items-start mb-2">
                      <p className="text-sm font-semibold group-hover:text-[var(--accent)] transition-colors">{r.name}</p>
                      <span className="text-[10px] px-2 py-0.5 bg-[var(--border)] rounded-full text-[var(--muted)] font-bold uppercase tracking-tighter">
                        难度 {r.difficulty.toFixed(1)}
                      </span>
                    </div>
                    <p className="text-[10px] text-[var(--muted)] uppercase tracking-wider mb-2">{r.domain}</p>
                    {r.prerequisites.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {r.prerequisites.map(p => (
                          <span key={p} className="text-[9px] px-1.5 py-0.5 bg-black/40 rounded text-[var(--muted)]">
                            {p}
                          </span>
                        ))}
                      </div>
                    )}
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

function StatCard({ label, value, icon, color }: { label: string; value: string | number; icon?: React.ReactNode; color?: string }) {
  return (
    <div className="bg-[var(--card)] rounded-2xl p-6 border border-[var(--border)] shadow-sm hover:border-[var(--accent)] transition-all group">
      <div className="flex justify-between items-start">
        <p className="text-[10px] font-bold text-[var(--muted)] uppercase tracking-widest">{label}</p>
        <div className={cn("p-1.5 rounded-lg bg-black/20 group-hover:text-[var(--accent)] transition-colors", color)}>
          {icon}
        </div>
      </div>
      <p className={cn("text-3xl font-black mt-2 tracking-tight", color)}>
        {value}
      </p>
    </div>
  );
}
