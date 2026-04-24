"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { useEffect } from "react";
import type { Conversation } from "@/lib/api";

const NAV = [
  { href: "/", label: "Chat", icon: "💬" },
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/review", label: "Review", icon: "🔄" },
  { href: "/knowledge", label: "Knowledge", icon: "🕸" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { conversations, setConversations, resetChat, sidebarOpen } = useAppStore();

  useEffect(() => {
    apiFetch<Conversation[]>("/conversations").then(setConversations).catch(() => {});
  }, [setConversations]);

  return (
    <aside
      className={`${
        sidebarOpen ? "w-64" : "w-0"
      } transition-all duration-200 bg-[var(--sidebar)] border-r border-[var(--border)] flex flex-col overflow-hidden shrink-0`}
    >
      <div className="p-4 border-b border-[var(--border)]">
        <h1 className="text-lg font-bold">StudyAgent</h1>
        <p className="text-xs text-[var(--muted)]">CS Learning Assistant</p>
      </div>

      <nav className="p-2 flex flex-col gap-1">
        {NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
              pathname === item.href
                ? "bg-[var(--accent)] text-white"
                : "hover:bg-[var(--card)] text-[var(--muted)]"
            }`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      <div className="border-t border-[var(--border)] p-2 mt-2">
        <button
          onClick={resetChat}
          className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-[var(--card)] text-[var(--muted)] transition-colors"
        >
          + New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        <p className="px-3 py-1 text-xs text-[var(--muted)] uppercase tracking-wider">Recent</p>
        {conversations.slice(0, 15).map((c) => (
          <Link
            key={c.id}
            href={`/?conv=${c.id}`}
            className="block px-3 py-2 text-sm rounded-lg hover:bg-[var(--card)] text-[var(--muted)] truncate transition-colors"
            title={c.title || "Untitled"}
          >
            {c.title || "Untitled"}
          </Link>
        ))}
      </div>
    </aside>
  );
}
