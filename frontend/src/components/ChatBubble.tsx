import { ChatMessage } from "../types";
import { cn } from "../utils";
import { SourcesTable } from "./SourcesTable";
import { Markdown } from "../utils/markdown";

export function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  
  return (
    <div className={cn("max-w-prose my-4", isUser ? "self-end" : "self-start")}>
      <div
        className={cn(
          "rounded-xl px-4 py-2 break-words",
          isUser ? "bg-blue-600 text-white" : "bg-gray-200"
        )}
      >
        {isUser ? (
          <div className="whitespace-pre-wrap">{message.content}</div>
        ) : (
          <div className="prose prose-sm max-w-none">
            <Markdown content={message.content} />
          </div>
        )}
        {!isUser && message.isStreaming && (
          <span className="inline-block w-2 h-5 bg-gray-600 animate-pulse ml-1"></span>
        )}
      </div>
      {!isUser && message.sources && !message.isStreaming && (
        <SourcesTable sources={message.sources} />
      )}
    </div>
  );
}
