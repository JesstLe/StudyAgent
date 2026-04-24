"use client";

import { useEffect, useState } from "react";
import { History, CheckCircle2, AlertCircle, PlayCircle, Trophy } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { CardResponse, ReviewResult } from "@/lib/api";

const GRADE_CONFIG: Record<number, { label: string; color: string; bg: string; border: string }> = {
  1: { label: "Again", color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/20" },
  2: { label: "Hard", color: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/20" },
  3: { label: "Good", color: "text-green-400", bg: "bg-green-500/10", border: "border-green-500/20" },
  4: { label: "Easy", color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20" },
};

export default function ReviewPage() {
  const [cards, setCards] = useState<CardResponse[]>([]);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<CardResponse[]>("/reviews/due").then((data) => {
      setCards(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  async function handleGrade(grade: number) {
    const card = cards[index];
    if (!card) return;
    try {
      const res = await apiFetch<ReviewResult>("/reviews/submit", {
        method: "POST",
        body: JSON.stringify({ grade, concept_id: card.id, card_id: card.id }),
      });
      setResult(res);
    } catch { /* */ }
    setIndex((prev) => prev + 1);
    setFlipped(false);
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-[var(--muted)] gap-4 animate-pulse">
        <div className="w-12 h-12 border-4 border-[var(--accent)] border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-medium uppercase tracking-widest">正在准备复习内容...</p>
      </div>
    );
  }

  if (index >= cards.length) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center space-y-6">
        <div className="w-24 h-24 bg-[var(--card)] rounded-[2.5rem] flex items-center justify-center text-5xl shadow-2xl border border-[var(--border)] animate-bounce">
          <Trophy className="text-[var(--warning)]" size={48} />
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold tracking-tight">Daily Goal Reached!</h2>
          <p className="text-[var(--muted)] max-w-xs">
            You&apos;ve reviewed {index} cards today. Consistency is the key to mastery.
          </p>
        </div>
        <button 
          onClick={() => window.location.href = "/dashboard"}
          className="bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white px-8 py-3 rounded-2xl text-sm font-bold transition-all shadow-lg shadow-[var(--accent)]/20"
        >
          View Progress
        </button>
      </div>
    );
  }

  const card = cards[index];

  return (
    <div className="flex flex-col h-full bg-[var(--background)]">
      <header className="px-8 py-6 border-b border-[var(--border)] flex items-center justify-between bg-[var(--background)]/80 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <History size={20} className="text-[var(--accent)]" />
          <h2 className="text-xl font-bold tracking-tight">复习中</h2>
        </div>
        <div className="flex items-center gap-4">
          <div className="h-2 w-32 bg-[var(--border)] rounded-full overflow-hidden">
            <div 
              className="h-full bg-[var(--accent)] transition-all duration-500" 
              style={{ width: `${((index) / cards.length) * 100}%` }} 
            />
          </div>
          <span className="text-xs font-black text-[var(--muted)] tabular-nums uppercase">
            {index + 1} / {cards.length}
          </span>
        </div>
      </header>

      <div className="flex-1 flex items-center justify-center p-8">
        <div
          className={cn(
            "flip-card w-full max-w-2xl transition-all duration-500",
            flipped ? "flipped scale-100" : "scale-95"
          )}
          style={{ minHeight: 400 }}
        >
          <div className="flip-card-inner relative w-full h-full shadow-2xl">
            {/* Front */}
            <div className="flip-card-front absolute inset-0 bg-[var(--card)] rounded-[2.5rem] border border-[var(--border)] p-12 flex flex-col items-center justify-center text-center space-y-8">
              <div className="px-4 py-1.5 bg-black/40 rounded-full border border-[var(--border)] text-[10px] font-bold text-[var(--muted)] uppercase tracking-widest">
                {card.card_type} · {card.fsrs_state}
              </div>
              <p className="text-2xl md:text-3xl font-medium leading-tight max-w-lg">
                {card.front}
              </p>
              {!flipped && (
                <button
                  onClick={() => setFlipped(true)}
                  className="group flex items-center gap-3 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white px-10 py-4 rounded-[1.5rem] text-sm font-bold transition-all shadow-xl shadow-[var(--accent)]/25 active:scale-95"
                >
                  <PlayCircle size={20} className="group-hover:rotate-12 transition-transform" />
                  Show Answer
                </button>
              )}
            </div>

            {/* Back */}
            <div className="flip-card-back absolute inset-0 bg-[var(--card)] rounded-[2.5rem] border border-[var(--accent)]/30 p-12 flex flex-col items-center justify-center text-center space-y-10 shadow-2xl shadow-[var(--accent)]/5">
              <div className="space-y-4 flex-1 flex flex-col justify-center">
                <p className="text-sm font-bold text-[var(--accent)] uppercase tracking-[0.2em]">Solution</p>
                <p className="text-xl md:text-2xl font-medium leading-relaxed max-w-lg">
                  {card.back}
                </p>
              </div>
              
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full max-w-md">
                {[1, 2, 3, 4].map((g) => {
                  const conf = GRADE_CONFIG[g];
                  return (
                    <button
                      key={g}
                      onClick={() => handleGrade(g)}
                      className={cn(
                        "flex flex-col items-center gap-1 p-4 rounded-2xl border transition-all active:scale-90",
                        conf.bg,
                        conf.border,
                        "hover:scale-105 hover:bg-opacity-20"
                      )}
                    >
                      <span className={cn("text-sm font-black", conf.color)}>{conf.label}</span>
                      <span className="text-[9px] text-[var(--muted)] font-bold uppercase">Grade {g}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="px-8 py-4 border-t border-[var(--border)] bg-black/20 backdrop-blur-sm animate-in fade-in slide-in-from-bottom-2">
          <div className="max-w-2xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={14} className="text-[var(--success)]" />
              <p className="text-xs font-bold text-[var(--muted)] uppercase tracking-wider">
                上一张: <span className="text-white">{GRADE_CONFIG[result.grade]?.label}</span>
              </p>
            </div>
            <div className="flex items-center gap-2">
              <AlertCircle size={14} className="text-[var(--accent)]" />
              <p className="text-xs font-bold text-[var(--muted)] uppercase tracking-wider">
                下次复习: <span className="text-white">{result.scheduled_days} 天后</span>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
