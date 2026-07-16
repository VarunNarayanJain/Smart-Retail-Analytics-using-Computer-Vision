import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="py-8 bg-[#07080F] border-t border-[var(--color-border-subtle)] relative overflow-hidden">
      {/* Top subtle glow line */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-[var(--color-primary)] to-transparent opacity-50"></div>
      
      <div className="max-w-7xl mx-auto px-4 text-center">
        <h4 className="text-xl font-display font-bold text-[var(--color-text-primary)] tracking-wide mb-2">
          RetailIQ
        </h4>
        <p className="text-sm text-[var(--color-text-muted)] font-mono">
          Built for research demonstration &middot; YOLOv8 + SORT &middot; Computer Vision
        </p>
      </div>
    </footer>
  );
};

export default Footer;
