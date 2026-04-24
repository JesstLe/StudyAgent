"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { CardResponse, ReviewResult } from "@/lib/api";

const GRADE_LABELS: Record<number, { label: string; color: string }> = {
  1: { label: "Again", color: "var(--danger)" },
  2: { label: "Hard", color: "var(--warning)" },
  3: { label: "Good", color: "var(--success)" },
  4: { label: "Easy", color: "var(--accent)" },
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
      <div className="flex items-center justify-center h-full text-[var(--muted)]">
        Loading review cards...
      </div>
    );
  }

  if (index >= cards.length) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <p className="text-4xl">🎉</p>
        <h2 className="text-xl font-semibold">All caught up!</h2>
        <p className="text-[var(--muted)]">Reviewed {index} card{index !== 1 ? "s" : ""}. No more due.</p>
      </div>
    );
  }

  const card = cards[index];

  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-4 border-b border-[var(--border)] flex items-center justify-between">
        <h2 className="text-lg font-semibold">Review</h2>
        <span className="text-sm text-[var(--muted)]">
          {index + 1} / {cards.length}
        </span>
      </header>

      <div className="flex-1 flex items-center justify-center p-6">
        <div
          className={`flip-card w-full max-w-lg ${flipped ? "flipped" : ""}`}
          style={{ minHeight: 280 }}
        >
          <div className="flip-card-inner relative w-full" style={{ minHeight: 280 }}>
            {/* Front */}
            <div className="flip-card-front absolute inset-0 bg-[var(--card)] rounded-2xl border border-[var(--border)] p-8 flex flex-col items-center justify-center">
              <p className="text-xs text-[var(--muted)] mb-4 uppercase tracking-wider">
                {card.card_type} · {card.fsrs_state}
              </p>
              <p className="text-xl text-center leading-relaxed">{card.front}</p>
              {!flipped && (
                <button
                  onClick={() => setFlipped(true)}
                  className="mt-8 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white px-6 py-2 rounded-xl text-sm transition-colors"
                >
                  Show Answer
                </button>
              )}
            </div>

            {/* Back */}
            <div className="flip-card-back absolute inset-0 bg-[var(--card)] rounded-2xl border border-[var(--border)] p-8 flex flex-col items-center justify-center">
              {card.back && (
                <p className="text-lg text-center leading-relaxed mb-6">{card.back}</p>
              )}
              <div className="flex gap-3">
                {[1, 2, 3, 4].map((g) => (
                  <button
                    key={g}
                    onClick={() => handleGrade(g)}
                    className="px-4 py-2 rounded-xl text-sm font-medium border transition-colors"
                    style={{
                      borderColor: GRADE_LABELS[g].color,
                      color: GRADE_LABELS[g].color,
                    }}
                  >
                    {GRADE_LABELS[g].label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="px-6 py-3 border-t border-[var(--border)] text-center text-sm text-[var(--muted)]">
          Last: Grade {GRADE_LABELS[result.grade]?.label} · Next review in {result.scheduled_days} day{result.scheduled_days !== 1 ? "s" : ""}
        </div>
      )}
    </div>
  );
}
