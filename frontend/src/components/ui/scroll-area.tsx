
import { ReactNode } from "react";

export function ScrollArea({
  className,
  children
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <div
      className={`overflow-y-auto scrollbar-thin scrollbar-thumb-rounded ${className}`}
    >
      {children}
    </div>
  );
}
