"use client";

import { useState, useRef, useEffect, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Send, Menu, Sparkles, MessageSquare, Terminal, Cpu, Copy, Check, Pencil, X } from "lucide-react";
import { apiFetch, streamChat } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { cn } from "@/lib/utils";
import { useTokenStream } from "@/lib/useTokenStream";
import type { Message, Conversation } from "@/lib/api";

const THINKING_STEPS = [
  "理解你的问题...",
  "分析知识背景...",
  "搜索历史痛点...",
  "组织教学框架...",
  "正在生成回答...",
];

function useThinkingText(isStreaming: boolean, hasContent: boolean) {
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (!isStreaming || hasContent) {
      setStep(0);
      return;
    }
    setStep(0);
    const interval = setInterval(() => {
      setStep((s) => (s < THINKING_STEPS.length - 1 ? s + 1 : s));
    }, 2000);
    return () => clearInterval(interval);
  }, [isStreaming, hasContent]);

  if (!isStreaming || hasContent) return null;
  return THINKING_STEPS[step];
}

const SUGGESTIONS = [
  { label: "What is B-tree?", icon: <Terminal size={14} /> },
  { label: "Explain virtual memory", icon: <Cpu size={14} /> },
  { label: "Why use Red-Black tree?", icon: <Sparkles size={14} /> },
];

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="p-1 rounded-md hover:bg-[var(--accent)]/10 text-[var(--muted)] hover:text-[var(--accent)] transition-colors"
      title="复制"
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
    </button>
  );
}

function MessageBubble({
  m,
  onEdit,
}: {
  m: Message;
  onEdit: (id: string, content: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(m.content);

  if (editing) {
    return (
      <div className="flex flex-col items-end w-full">
        <div className="max-w-[85%] w-full">
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            className="w-full bg-[var(--card)] border border-[var(--accent)] rounded-2xl px-4 py-3 text-sm text-[var(--foreground)] focus:outline-none resize-none min-h-[60px]"
            rows={3}
            autoFocus
          />
          <div className="flex items-center gap-2 mt-2 justify-end">
            <button
              onClick={() => setEditing(false)}
              className="flex items-center gap-1 px-3 py-1.5 text-xs text-[var(--muted)] hover:text-white rounded-lg hover:bg-[var(--card)] transition-colors"
            >
              <X size={12} />
              取消
            </button>
            <button
              onClick={() => {
                if (editText.trim() && editText.trim() !== m.content) {
                  onEdit(m.id, editText.trim());
                }
                setEditing(false);
              }}
              className="flex items-center gap-1 px-3 py-1.5 text-xs bg-[var(--accent)] text-white rounded-lg hover:bg-[var(--accent-hover)] transition-colors font-medium"
            >
              <Send size={12} />
              重新发送
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex flex-col group",
        m.role === "user" ? "items-end" : "items-start"
      )}
    >
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
          m.role === "user"
            ? "bg-[var(--accent)] text-white shadow-lg"
            : m.role === "system"
            ? "bg-red-900/20 text-red-300 border border-red-900/50"
            : "bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)]"
        )}
      >
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeKatex]}
            components={{
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || "");
                return !inline && match ? (
                  <SyntaxHighlighter
                    {...props}
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                  >
                    {String(children).replace(/\n$/, "")}
                  </SyntaxHighlighter>
                ) : (
                  <code {...props} className={className}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {m.content}
          </ReactMarkdown>
        </div>
      </div>
      <div className="flex items-center gap-1 mt-1 px-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <span className="text-[10px] text-[var(--muted)]">
          {new Date(m.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
        <CopyButton text={m.content} />
        {m.role === "user" && (
          <button
            onClick={() => {
              setEditText(m.content);
              setEditing(true);
            }}
            className="p-1 rounded-md hover:bg-[var(--accent)]/10 text-[var(--muted)] hover:text-[var(--accent)] transition-colors"
            title="编辑并重新发送"
          >
            <Pencil size={14} />
          </button>
        )}
      </div>
    </div>
  );
}

function ChatContent() {
  const [input, setInput] = useState("");
  const searchParams = useSearchParams();
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
    conversations,
    setConversations,
    addConversation,
    toggleSidebar,
  } = useAppStore();

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const chatHistory = useRef<{ role: string; content: string }[]>([]);
  const loadedConvId = useRef<string | null>(null);
  const thinkingText = useThinkingText(isStreaming, !!streamingText);
  const tokenStream = useTokenStream(appendStreamingToken, setStreamingText);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const userAtBottom = useRef(true);

  const checkBottom = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return;
    const threshold = 80;
    userAtBottom.current =
      el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
  }, []);

  useEffect(() => {
    if (userAtBottom.current) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, streamingText]);

  useEffect(() => {
    if (conversations.length === 0) {
      apiFetch<Conversation[]>("/conversations")
        .then(setConversations)
        .catch(() => {});
    }
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [input]);

  const loadConversation = useCallback(
    async (convId: string) => {
      if (convId === loadedConvId.current) return;
      loadedConvId.current = convId;
      setActiveConversation(convId);
      try {
        const msgs = await apiFetch<Message[]>(`/conversations/${convId}`);
        setMessages(msgs);
        chatHistory.current = msgs.map((m) => ({
          role: m.role,
          content: m.content,
        }));
      } catch {
        setMessages([]);
        chatHistory.current = [];
      }
    },
    [setActiveConversation, setMessages]
  );

  useEffect(() => {
    const convId = searchParams.get("conv");
    if (convId) {
      loadConversation(convId);
    } else if (loadedConvId.current) {
      loadedConvId.current = null;
      setActiveConversation(null);
      setMessages([]);
      chatHistory.current = [];
    }
  }, [searchParams, loadConversation, setActiveConversation, setMessages]);

  const lastAutoAsk = useRef<string | null>(null);
  useEffect(() => {
    const ask = searchParams.get("ask");
    if (ask && ask !== lastAutoAsk.current && !isStreaming) {
      lastAutoAsk.current = ask;
      handleSend(ask);
    }
  }, [searchParams]);

  async function handleSend(overrideText?: string) {
    const text = (overrideText || input).trim();
    if (!text || isStreaming) return;
    setInput("");
    setStreamingText("");
    setIsStreaming(true);
    tokenStream.reset();

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

      for await (const event of streamChat(
        chatHistory.current,
        convId ?? undefined
      )) {
        if (event.type === "token" && event.content) {
          tokenStream.push(event.content);
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

      const fullText = tokenStream.getFullText();
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: fullText,
        created_at: new Date().toISOString(),
      };
      setMessages([...messages, userMsg, assistantMsg]);
      chatHistory.current.push({ role: "assistant", content: fullText });
      tokenStream.reset();
    } catch (err) {
      setMessages([
        ...messages,
        userMsg,
        {
          id: "err",
          role: "system",
          content: `Error: ${err}`,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsStreaming(false);
    }
  }

  const handleEditMessage = useCallback(
    (messageId: string, newContent: string) => {
      const idx = messages.findIndex((m) => m.id === messageId);
      if (idx === -1) return;

      const keptMessages = messages.slice(0, idx);
      const keptHistory = chatHistory.current.slice(0, idx);

      setMessages(keptMessages);
      chatHistory.current = keptHistory;
      setInput(newContent);

      setTimeout(() => textareaRef.current?.focus(), 0);
    },
    [messages, setMessages]
  );

  return (
    <div className="flex flex-col h-full bg-[var(--background)]">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border)] bg-[var(--background)]/80 backdrop-blur-md sticky top-0 z-10">
        <button
          onClick={toggleSidebar}
          className="text-[var(--muted)] hover:text-white p-1.5 hover:bg-[var(--card)] rounded-lg transition-colors"
        >
          <Menu size={18} />
        </button>
        <div className="flex flex-col">
          <h2 className="text-sm font-semibold flex items-center gap-2">
            <MessageSquare size={14} className="text-[var(--accent)]" />
            CS Tutor
          </h2>
        </div>
      </header>

      {/* Messages */}
      <div
        ref={scrollContainerRef}
        onScroll={checkBottom}
        className="flex-1 overflow-y-auto px-4 py-6 space-y-6"
      >
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.length === 0 && !streamingText && (
            <div className="flex flex-col items-center justify-center py-20 text-center space-y-8">
              <div className="w-16 h-16 bg-[var(--card)] rounded-3xl flex items-center justify-center text-3xl shadow-xl border border-[var(--border)]">
                🎓
              </div>
              <div className="space-y-2">
                <h1 className="text-2xl font-bold">今天我能帮您什么？</h1>
                <p className="text-[var(--muted)] max-w-sm">
                  我是您的 CS
                  专属导师。您可以问我关于算法、操作系统、计算机组成原理等相关问题。
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-md px-4">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s.label}
                    onClick={() => handleSend(s.label)}
                    className="flex items-center gap-3 p-4 bg-[var(--card)] border border-[var(--border)] rounded-2xl text-left text-sm hover:border-[var(--accent)] hover:bg-[var(--accent)]/5 transition-all group"
                  >
                    <span className="text-[var(--muted)] group-hover:text-[var(--accent)]">
                      {s.icon}
                    </span>
                    <span className="font-medium">{s.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => (
            <MessageBubble key={m.id} m={m} onEdit={handleEditMessage} />
          ))}

          {streamingText && (
            <div className="flex flex-col items-start">
              <div className="max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed bg-[var(--card)] border border-[var(--border)] streaming-cursor">
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                    components={{
                      code({
                        node,
                        inline,
                        className,
                        children,
                        ...props
                      }: any) {
                        const match = /language-(\w+)/.exec(className || "");
                        return !inline && match ? (
                          <SyntaxHighlighter
                            {...props}
                            style={vscDarkPlus}
                            language={match[1]}
                            PreTag="div"
                          >
                            {String(children).replace(/\n$/, "")}
                          </SyntaxHighlighter>
                        ) : (
                          <code {...props} className={className}>
                            {children}
                          </code>
                        );
                      },
                    }}
                  >
                    {streamingText}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          )}

          {thinkingText && (
            <div className="flex items-start">
              <div className="flex items-center gap-3 rounded-2xl px-5 py-3 bg-[var(--card)] border border-[var(--border)]">
                <div className="relative w-4 h-4">
                  <div className="absolute inset-0 rounded-full border-2 border-[var(--accent)]/30" />
                  <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-[var(--accent)] animate-spin" />
                </div>
                <span
                  className="text-sm text-[var(--muted)] thinking-text"
                  key={thinkingText}
                >
                  {thinkingText}
                </span>
              </div>
            </div>
          )}
        </div>
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-gradient-to-t from-[var(--background)] to-transparent">
        <div className="max-w-3xl mx-auto relative group">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask anything..."
            disabled={isStreaming}
            className="w-full bg-[var(--card)] border border-[var(--border)] rounded-2xl pl-4 pr-12 py-3.5 text-sm focus:outline-none focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)]/30 disabled:opacity-50 transition-all resize-none shadow-xl"
          />
          <button
            onClick={() => handleSend()}
            disabled={isStreaming || !input.trim()}
            className="absolute right-2 bottom-2 h-9 px-4 flex items-center justify-center bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded-xl text-xs font-bold transition-all disabled:opacity-30 disabled:hover:bg-[var(--accent)]"
          >
            {isStreaming ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              "Send"
            )}
          </button>
        </div>
        <p className="text-[10px] text-[var(--muted)] text-center mt-2 uppercase tracking-tighter">
          StudyAgent can make mistakes. Check important info.
        </p>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-full text-[var(--muted)]">
          加载中...
        </div>
      }
    >
      <ChatContent />
    </Suspense>
  );
}
