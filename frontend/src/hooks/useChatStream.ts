import { useState, useCallback } from "react";
import { parseSSE } from "../lib/sse";
import { ChatMessage, SourceReference } from "../types";

export function useChatStream(sessionId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [isThinking, setIsThinking] = useState(false);

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

      // Show thinking state
      setIsThinking(true);

      const resp = await fetch(`/api/chat/message?session_id=${sessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content })
      });

      if (!resp.body) {
        setIsThinking(false);
        return;
      }

      const assistantId = "assistant-" + Date.now();
      let assistantSources: SourceReference[] = [];
      let firstToken = true;
      
      // Set streaming state
      setStreamingMessageId(assistantId);

      try {
        for await (const chunk of parseSSE(resp.body)) {
          if (chunk === "[DONE]") break;
          
          if (chunk.startsWith("[SOURCES]")) {
            const meta = JSON.parse(chunk.slice(9));
            assistantSources = meta.sources ?? [];
            continue;
          }

          // Hide thinking animation and create initial message on first token
          if (firstToken) {
            setIsThinking(false);
            const initialMsg: ChatMessage = {
              id: assistantId,
              role: "assistant",
              content: chunk,
              isStreaming: true
            };
            append(initialMsg);
            firstToken = false;
          } else {
            // Add each subsequent token to the message content
            setMessages((prev) => {
              const idx = prev.findIndex((m) => m.id === assistantId);
              if (idx >= 0) {
                const copy = [...prev];
                const currentMsg = copy[idx];
                copy[idx] = {
                  ...currentMsg,
                  content: currentMsg.content + chunk,
                  isStreaming: true
                };
                return copy;
              }
              return prev;
            });
          }

          // Small delay to make streaming visible even with fast tokens
          await new Promise(resolve => setTimeout(resolve, 60));
        }

        // Finalize the message with sources and remove streaming state
        setMessages((prev) => {
          const idx = prev.findIndex((m) => m.id === assistantId);
          if (idx >= 0) {
            const copy = [...prev];
            copy[idx] = {
              ...copy[idx],
              sources: assistantSources,
              isStreaming: false
            };
            return copy;
          }
          return prev;
        });

      } catch (error) {
        console.error("Streaming error:", error);
        setIsThinking(false);
        // Mark message as complete even on error
        setMessages((prev) => {
          const idx = prev.findIndex((m) => m.id === assistantId);
          if (idx >= 0) {
            const copy = [...prev];
            copy[idx] = {
              ...copy[idx],
              isStreaming: false
            };
            return copy;
          }
          return prev;
        });
      } finally {
        setStreamingMessageId(null);
        setIsThinking(false);
      }
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
          content: m.content,
          isStreaming: false
        }));
        setMessages(msgs);
      });
  }, [sessionId]);

  return { messages, sendMessage, loadHistory, streamingMessageId, isThinking };
}
