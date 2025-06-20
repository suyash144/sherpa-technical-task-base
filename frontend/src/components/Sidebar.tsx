import { Sheet, SheetContent, SheetTrigger } from "./ui/sheet";
import { ScrollArea } from "./ui/scroll-area";
import { Menu } from "lucide-react";
import { ReactNode } from "react";

interface SidebarProps {
  children: ReactNode;
  sessions?: Array<{id: string; title: string; lastMessage?: string}>;
  currentSessionId?: string;
  onSessionSelect?: (sessionId: string) => void;
}

export function Sidebar({ children, sessions = [], currentSessionId, onSessionSelect }: SidebarProps) {
  const sidebarContent = (
    <div className="h-full flex flex-col">
      {children}
      
      {/* Chat History Section */}
      <div className="mt-6 flex-1">
        <h3 className="font-semibold mb-2 text-sm text-gray-600">Chat History</h3>
        <ScrollArea className="flex-1">
          <div className="space-y-2">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => onSessionSelect?.(session.id)}
                className={`w-full text-left p-2 text-sm rounded hover:bg-gray-100 ${
                  currentSessionId === session.id ? 'bg-blue-50 border-l-2 border-blue-500' : ''
                }`}
              >
                <div className="font-medium truncate">{session.title}</div>
                {session.lastMessage && (
                  <div className="text-gray-500 text-xs truncate mt-1">
                    {session.lastMessage}
                  </div>
                )}
              </button>
            ))}
            {sessions.length === 0 && (
              <p className="text-gray-500 text-xs">No chat history yet</p>
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <div className="hidden md:flex w-64 bg-gray-50 border-r border-gray-200 p-4">
        {sidebarContent}
      </div>
      
      {/* Mobile Sidebar */}
      <Sheet>
        <SheetTrigger className="md:hidden p-2 fixed top-4 left-4 bg-white rounded-md shadow-md z-40">
          <Menu />
        </SheetTrigger>
        <SheetContent side="left" className="w-64">
          <div className="p-2 h-full">
            {sidebarContent}
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
