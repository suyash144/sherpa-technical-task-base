
import * as React from "react";

interface SheetProps {
  children: React.ReactNode;
}

export function Sheet({ children }: SheetProps) {
  const [open, setOpen] = React.useState(false);
  return (
    <div className="relative">
      {React.Children.map(children, (child: any) =>
        React.cloneElement(child, { open, setOpen })
      )}
    </div>
  );
}

export function SheetTrigger({
  children,
  open,
  setOpen,
  className = ""
}: any) {
  return (
    <button
      className={className}
      onClick={() => setOpen(!open)}
    >
      {children}
    </button>
  );
}

export function SheetContent({
  children,
  open,
  setOpen,
  side = "left",
  className = ""
}: any) {
  return open ? (
    <div
      className={`fixed inset-0 bg-white shadow-xl z-50 w-64 p-4 ${className}`}
    >
      <button
        className="absolute top-2 right-2"
        onClick={() => setOpen(false)}
      >
        ×
      </button>
      {children}
    </div>
  ) : null;
}
