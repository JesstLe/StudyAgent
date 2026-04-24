"use client";

import { useState, useRef, useEffect } from "react";
import { streamChat } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import type { Message } from "@/lib/api";

export default function ChatPage() {
  const [input, setInput] = useState("");
  const {
    activeConversationId,
    setActiveConversation,
    messages,
    setMessages,
    streamingText,
    appendStreamingToken,
    setStreamingText,
    isStreaming,
    setIsStreaming,
    addConversation,
    toggleSidebar,
  } = useAppStore();

  const bottomRef = useRef<HTMLDivElement>(null);
  const chatHistory = useRef<{ role: string; content: string }[]>([]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  async function handleSend() {
    const text = input.trim();
    if (!text || isStreaming) return;
    setInput("");
    setStreamingText("");
    setIsStreaming(true);

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages([...messages, userMsg]);
    chatHistory.current.push({ role: "user", content: text });

    try {
      let convId = activeConversationId;
      let fullText = "";

      for await (const event of streamChat(chatHistory.current, convId ?? undefined)) {
        if (event.type === "token" && event.content) {
          fullText += event.content;
          appendStreamingToken(event.content);
        }
        if (event.type === "done") {
          if (event.conversation_id && !convId) {
            convId = event.conversation_id;
            setActiveConversation(convId);
            addConversation({
              id: convId,
              title: text.slice(0, 50),
              session_type: "teaching",
              message_count: 2,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            });
          }
        }
      }

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: fullText,
        created_at: new Date().toISOString(),
      };
      setMessages([...messages, userMsg, assistantMsg]);
      chatHistory.current.push({ role: "assistant", content: fullText });
      setStreamingText("");
    } catch (err) {
      setMessages([
        ...messages,
        userMsg,
        { id: "err", role: "system", content: `Error: ${err}`, created_at: new Date().toISOString() },
      ]);
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border)]">
        <button onClick={toggleSidebar} className="text-[var(--muted)] hover:text-white p-1">
          ☰
        </button>
        <h2 className="text-sm font-medium">Chat</h2>
        <span className="text-xs text-[var(--muted)] ml-auto">
          {activeConversationId ? `Conv: ${activeConversationId.slice(0, 8)}` : "New Session"}
        </span>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 && !streamingText && (
          <div className="flex flex-col items-center justify-center h-full text-[var(--muted)] gap-3">
            <p className="text-2xl">🎓</p>
            <p className="text-lg">Ask about any CS concept</p>
            <p className="text-sm">e.g. &quot;What is a B-tree?&quot; or &quot;Explain virtual memory&quot;</p>
          </div>
        )}

        {messages.map((m) => (
          <div
            key={m.id}
            className={`max-w-3xl ${m.role === "user" ? "ml-auto" : "mr-auto"}`}
          >
            <div
              className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                m.role === "user"
                  ? "bg-[var(--accent)] text-white"
                  : m.role === "system"
                  ? "bg-red-900/30 text-red-300"
                  : "bg-[var(--card)] text-[var(--foreground)]"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}

        {streamingText && (
          <div className="max-w-3xl mr-auto">
            <div className="rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap bg-[var(--card)] streaming-cursor">
              {streamingText}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-[var(--border)] p-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="Ask about CS concepts..."
            disabled={isStreaming}
            className="flex-1 bg-[var(--card)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[var(--accent)] disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || !input.trim()}
            className="bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white px-6 py-3 rounded-xl text-sm font-medium disabled:opacity-50 transition-colors"
          >
            {isStreaming ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
