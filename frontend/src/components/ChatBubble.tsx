
import { ChatMessage } from "../types";
import { cn } from "../utils";

export function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div
      className={cn(
        "max-w-prose rounded-xl px-4 py-2 my-1 whitespace-pre-wrap break-words",
        isUser ? "bg-blue-600 text-white self-end" : "bg-gray-200"
      )}
    >
      {message.content}
    </div>
  );
}
