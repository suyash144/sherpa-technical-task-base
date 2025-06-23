import { useEffect, useRef, useState } from "react";
import { ChatBubble } from "../components/ChatBubble";
import { Sidebar } from "../components/Sidebar";
import { useChatStream } from "../hooks/useChatStream";
import { cn } from "../utils";
import { Link } from "react-router-dom";

export default function ChatPage() {
  const [sessionId, setSessionId] = useState(() => {
    const param = new URLSearchParams(window.location.search).get("session");
    return param || crypto.randomUUID();
  });
  const { messages, sendMessage, loadHistory, isThinking } = useChatStream(sessionId);
  const [input, setInput] = useState("");
  const [sessions, setSessions] = useState<Array<{id: string; title: string; lastMessage?: string}>>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadHistory();
    loadSessions();
  }, [loadHistory]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/chat/sessions');
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const handleSend = () => {
    if (input.trim().length === 0) return;
    sendMessage(input);
    setInput("");
  };

  const handleSessionSelect = (newSessionId: string) => {
    setSessionId(newSessionId);
    window.history.pushState({}, '', `?session=${newSessionId}`);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar 
        sessions={sessions}
        currentSessionId={sessionId}
        onSessionSelect={handleSessionSelect}
      >
        <h2 className="font-semibold mb-4">RAG Chat</h2>
        <nav className="flex flex-col gap-2">
          <Link to="/" className="px-3 py-2 rounded bg-blue-100 text-blue-700 font-medium">
            Chat
          </Link>
          <Link to="/upload" className="px-3 py-2 rounded hover:bg-gray-100 text-gray-700">
            Upload Documents
          </Link>
        </nav>
      </Sidebar>

      <main className="flex flex-col flex-1">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4 md:pl-4 pl-16">
          <h1 className="text-xl font-semibold text-gray-800">Chat Session</h1>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-white">
          <div className="max-w-4xl mx-auto p-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <p className="text-lg mb-2">Welcome to RAG Chat!</p>
                <p>Start a conversation by typing a message below.</p>
              </div>
            ) : (
              messages.map((m) => (
                <ChatBubble key={m.id} message={m} />
              ))
            )}
            {isThinking && (
              <div className="max-w-prose my-4">
                <div className="bg-gray-200 rounded-xl px-4 py-2">
                  <div className="flex items-center space-x-1">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-gray-500 text-sm ml-2">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="max-w-4xl mx-auto flex gap-3">
            <textarea
              className={cn(
                "flex-1 border border-gray-300 rounded-lg p-3 resize-none",
                "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                "placeholder-gray-400"
              )}
              rows={3}
              placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              onClick={handleSend}
              disabled={input.trim().length === 0}
            >
              Send
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
