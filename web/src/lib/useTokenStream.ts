"use client";

import { useRef, useCallback } from "react";

const TICK_MS = 20;
const MAX_CATCHUP = 8;

export function useTokenStream(
  appendStreamingToken: (token: string) => void,
  setStreamingText: (text: string) => void,
) {
  const queue = useRef<string[]>([]);
  const fullText = useRef("");
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const flush = useCallback(() => {
    if (queue.current.length === 0) {
      timer.current = null;
      return;
    }
    const batch = queue.current.splice(0, MAX_CATCHUP);
    for (const t of batch) {
      fullText.current += t;
      appendStreamingToken(t);
    }
    timer.current = setTimeout(flush, queue.current.length > 0 ? TICK_MS : 0);
  }, [appendStreamingToken]);

  const push = useCallback(
    (token: string) => {
      queue.current.push(token);
      if (!timer.current) {
        flush();
      }
    },
    [flush],
  );

  const reset = useCallback(() => {
    if (timer.current) {
      clearTimeout(timer.current);
      timer.current = null;
    }
    queue.current = [];
    fullText.current = "";
    setStreamingText("");
  }, [setStreamingText]);

  const getFullText = useCallback(() => fullText.current, []);

  return { push, reset, getFullText };
}
