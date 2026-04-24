"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { 
  MessageSquare, 
  LayoutDashboard, 
  History, 
  Network, 
  Plus, 
  Search,
  Settings,
  GraduationCap
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { useEffect, useMemo } from "react";
import { cn } from "@/lib/utils";
import type { Conversation } from "@/lib/api";

const NAV = [
  { href: "/", label: "对话", icon: MessageSquare },
  { href: "/dashboard", label: "学习看板", icon: LayoutDashboard },
  { href: "/review", label: "复习", icon: History },
  { href: "/knowledge", label: "知识空间", icon: Network },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { conversations, setConversations, resetChat, sidebarOpen, activeConversationId } = useAppStore();

  useEffect(() => {
    apiFetch<Conversation[]>("/conversations").then(setConversations).catch(() => {});
  }, [setConversations]);

  const groupedConversations = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const groups: { [key: string]: Conversation[] } = {
      "今天": [],
      "更早": []
    };

    conversations.forEach(c => {
      const date = new Date(c.updated_at);
      if (date >= today) {
        groups["今天"].push(c);
      } else {
        groups["更早"].push(c);
      }
    });

    return groups;
  }, [conversations]);

  return (
    <aside
      className={cn(
        "bg-[var(--sidebar)] border-r border-[var(--border)] flex flex-col overflow-hidden shrink-0 transition-all duration-300 ease-in-out",
        sidebarOpen ? "w-72" : "w-0"
      )}
    >
      {/* Brand */}
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-[var(--accent)] rounded-lg flex items-center justify-center text-white shadow-lg">
          <GraduationCap size={20} />
        </div>
        <div className="flex flex-col">
          <h1 className="text-sm font-bold tracking-tight">StudyAgent</h1>
          <p className="text-[10px] text-[var(--muted)] font-medium uppercase">CS 专属导师</p>
        </div>
      </div>

      {/* Main Nav */}
      <nav className="px-3 space-y-1">
        {NAV.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all group",
                isActive
                  ? "bg-[var(--accent)] text-white shadow-md shadow-[var(--accent)]/20"
                  : "text-[var(--muted)] hover:text-white hover:bg-[var(--card)]"
              )}
            >
              <Icon size={18} className={cn("transition-transform group-hover:scale-110", isActive ? "text-white" : "text-[var(--muted)]")} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="px-4 mt-6">
        <button
          onClick={() => { resetChat(); router.push("/"); }}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-[var(--card)] border border-[var(--border)] rounded-2xl text-sm font-semibold hover:border-[var(--accent)] hover:bg-[var(--accent)]/5 transition-all shadow-sm group"
        >
          <Plus size={18} className="text-[var(--accent)] group-hover:rotate-90 transition-transform" />
          <span>新对话</span>
        </button>
      </div>

      {/* Recent Conversations */}
      <div className="flex-1 overflow-y-auto mt-6 px-3 custom-scrollbar">
        {Object.entries(groupedConversations).map(([group, items]) => (
          items.length > 0 && (
            <div key={group} className="mb-4">
              <p className="px-3 py-2 text-[10px] font-bold text-[var(--muted)] uppercase tracking-widest">{group}</p>
              <div className="space-y-0.5">
                {items.slice(0, 10).map((c) => (
                  <Link
                    key={c.id}
                    href={`/?conv=${c.id}`}
                    className={cn(
                      "block px-3 py-2 text-sm rounded-xl truncate transition-all",
                      activeConversationId === c.id
                        ? "bg-[var(--card)] text-white border-l-2 border-[var(--accent)]"
                        : "text-[var(--muted)] hover:text-white hover:bg-[var(--card)]"
                    )}
                    title={c.title || "Untitled"}
                  >
                    {c.title || "未命名"}
                  </Link>
                ))}
              </div>
            </div>
          )
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-[var(--border)]">
        <button className="flex items-center gap-3 w-full px-3 py-2 text-[var(--muted)] hover:text-white transition-colors text-sm font-medium rounded-xl hover:bg-[var(--card)]">
          <Settings size={18} />
          <span>设置</span>
        </button>
      </div>
    </aside>
  );
}
