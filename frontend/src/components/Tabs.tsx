import { ReactNode } from 'react';

interface TabProps {
  id: string;
  label: string;
  isActive: boolean;
  onClick: () => void;
}

export function Tab({ label, isActive, onClick }: TabProps) {
  return (
    <button
      type="button"
      className={`tab-button ${isActive ? 'active' : ''}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

interface TabPanelProps {
  children: ReactNode;
  isActive: boolean;
}

export function TabPanel({ children, isActive }: TabPanelProps) {
  if (!isActive) return null;

  return <div className="py-4">{children}</div>;
}

interface TabGroupProps {
  children: ReactNode;
}

export function TabGroup({ children }: TabGroupProps) {
  return (
    <div className="border-b border-gray-200">
      <nav className="flex gap-1" aria-label="Tabs">
        {children}
      </nav>
    </div>
  );
}
