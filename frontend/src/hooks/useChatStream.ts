import { useState, useCallback } from "react";
import { parseSSE } from "../lib/sse";
import { ChatMessage, SourceReference } from "../types";

export function useChatStream(sessionId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sources, setSources] = useState<SourceReference[]>([]);

  const append = (msg: ChatMessage) =>
    setMessages((prev) => [...prev, msg]);

  const sendMessage = useCallback(
    async (content: string) => {
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content
      };
      append(userMsg);

      const resp = await fetch(`/api/chat/message?session_id=${sessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content })
      });

      if (!resp.body) return;

      let assistantContent = "";
      for await (const chunk of parseSSE(resp.body)) {
        if (chunk === "[DONE]") break;
        if (chunk.startsWith("[SOURCES]")) {
          const meta = JSON.parse(chunk.slice(9));
          setSources(meta.sources ?? []);
          continue;
        }
        assistantContent += chunk;
        const msg: ChatMessage = {
          id: "assistant-" + Date.now(),
          role: "assistant",
          content: assistantContent
        };
        // replace last assistant message or push new
        setMessages((prev) => {
          const idx = prev.findIndex((m) => m.id === msg.id);
          if (idx >= 0) {
            const copy = [...prev];
            copy[idx] = msg;
            return copy;
          }
          return [...prev, msg];
        });
      }

      // persist conversation to backend handled already; fetch history again:
      fetch(`/api/chat/history?session_id=${sessionId}`)
        .then((r) => r.json())
        .then((data) => {
          const msgs = (data.messages ?? []).map((m: any) => ({
            id: crypto.randomUUID(),
            role: m.role,
            content: m.content
          }));
          setMessages(msgs);
        });
    },
    [sessionId]
  );

  const loadHistory = useCallback(() => {
    fetch(`/api/chat/history?session_id=${sessionId}`)
      .then((r) => r.json())
      .then((data) => {
        const msgs = (data.messages ?? []).map((m: any) => ({
          id: crypto.randomUUID(),
          role: m.role,
          content: m.content
        }));
        setMessages(msgs);
      });
  }, [sessionId]);

  return { messages, sendMessage, loadHistory, sources };
}
