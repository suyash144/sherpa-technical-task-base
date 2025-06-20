
export interface SourceReference {
  document_id: string;
  filename: string;
  page: number;
  relevance_score: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  sources?: SourceReference[];
}
