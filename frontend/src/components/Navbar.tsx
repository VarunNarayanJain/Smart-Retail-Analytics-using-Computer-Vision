import React from 'react';

const Navbar: React.FC = () => {
  return (
    <nav className="fixed w-full z-50 transition-all duration-300 glass-panel border-b border-[var(--color-border-subtle)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex-shrink-0 flex items-center gap-2">
            <span className="text-xl font-bold font-display tracking-wider">RetailIQ</span>
            <div className="w-2 h-2 rounded-full bg-[var(--color-primary)] glow-text"></div>
          </div>
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-8">
              <a href="#features" className="hover:text-[var(--color-primary)] transition-colors text-sm font-medium">Features</a>
              <a href="#how-it-works" className="hover:text-[var(--color-primary)] transition-colors text-sm font-medium">How It Works</a>
              <a href="#dashboard" className="hover:text-[var(--color-primary)] transition-colors text-sm font-medium">Dashboard</a>
              <a href="#tech-stack" className="hover:text-[var(--color-primary)] transition-colors text-sm font-medium">Tech Stack</a>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </div>
            <span className="text-xs font-mono text-[var(--color-text-muted)] mt-0.5 border border-[#1E2240] px-2 py-1 rounded bg-[#0F1120]">LIVE System Active</span>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
