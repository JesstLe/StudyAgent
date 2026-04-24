const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...opts,
    headers: { "Content-Type": "application/json", ...opts?.headers },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export async function* streamChat(
  messages: { role: string; content: string }[],
  conversationId?: string,
  sessionType = "teaching",
): AsyncGenerator<{ type: string; content?: string; conversation_id?: string; extraction?: Record<string, number> }> {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, conversation_id: conversationId, session_type: sessionType }),
  });
  if (!res.ok || !res.body) throw new Error(`Stream failed: ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const lines = buf.split("\n");
    buf = lines.pop() || "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const raw = line.slice(6).trim();
      if (!raw) continue;
      try {
        const event = JSON.parse(raw);
        yield event;
        if (event.type === "done") {
          reader.cancel();
          return;
        }
      } catch { /* skip */ }
    }
  }
}

// Types
export interface Conversation {
  id: string;
  title: string | null;
  session_type: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: string;
  content: string;
  created_at: string;
}

export interface Concept {
  id: string;
  name: string;
  domain: string;
  description: string | null;
  difficulty: number;
  mastery_level: number | null;
}

export interface AnalyticsOverview {
  total_concepts: number;
  mastered: number;
  learning: number;
  new: number;
  avg_mastery: number;
  due_reviews: number;
  mastery_distribution: { mastered: number; learning: number; new: number };
}

export interface WeakArea {
  concept_id: string;
  concept_name: string;
  domain: string;
  mastery: number;
  assessments: number;
}

export interface Recommendation {
  concept_id: string;
  name: string;
  domain: string;
  difficulty: number;
  prerequisites: string[];
}

export interface DomainSummary {
  domain: string;
  concepts: number;
  avg_mastery: number;
}

export interface CardResponse {
  id: string;
  card_type: string;
  front: string;
  back: string | null;
  options: { label: string; text: string; is_correct: boolean }[] | null;
  difficulty: number;
  fsrs_state: string;
}

export interface ReviewResult {
  concept_id: string;
  grade: number;
  scheduled_days: number;
  next_review: string;
  retrievability: number;
}
