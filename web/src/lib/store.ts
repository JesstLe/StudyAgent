import { create } from "zustand";
import type { Conversation, Message } from "./api";

interface AppState {
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: Message[];
  streamingText: string;
  isStreaming: boolean;
  sidebarOpen: boolean;

  setConversations: (c: Conversation[]) => void;
  addConversation: (c: Conversation) => void;
  setActiveConversation: (id: string | null) => void;
  setMessages: (m: Message[]) => void;
  appendStreamingToken: (token: string) => void;
  setStreamingText: (text: string) => void;
  setIsStreaming: (v: boolean) => void;
  toggleSidebar: () => void;
  resetChat: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  conversations: [],
  activeConversationId: null,
  messages: [],
  streamingText: "",
  isStreaming: false,
  sidebarOpen: true,

  setConversations: (c) => set({ conversations: c }),
  addConversation: (c) => set((s) => ({ conversations: [c, ...s.conversations] })),
  setActiveConversation: (id) => set({ activeConversationId: id }),
  setMessages: (m) => set({ messages: m }),
  appendStreamingToken: (token) =>
    set((s) => ({ streamingText: s.streamingText + token })),
  setStreamingText: (text) => set({ streamingText: text }),
  setIsStreaming: (v) => set({ isStreaming: v }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  resetChat: () => set({ messages: [], streamingText: "", activeConversationId: null }),
}));
