import React from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Flame, Clock, Users, LineChart, Bell, Camera } from 'lucide-react';

const features = [
  {
    icon: Flame,
    title: "Real-Time Heatmaps",
    description: "See exactly where customers congregate, updated every second",
  },
  {
    icon: Clock,
    title: "Dwell Time Analysis",
    description: "Zone-level dwell tracking per unique track ID",
  },
  {
    icon: Users,
    title: "Crowd Detection",
    description: "Automated alerts when zone occupancy exceeds threshold",
  },
  {
    icon: LineChart,
    title: "Footfall Trends",
    description: "Hourly, daily, and weekly visitor patterns",
  },
  {
    icon: Bell,
    title: "Smart Alert System",
    description: "Configurable rules engine for overcrowding, idle zones, and anomalies",
  },
  {
    icon: Camera,
    title: "Multi-Camera Support",
    description: "Unified tracking across multiple store camera feeds",
  }
];

const FeatureCard = ({ feature, index }: { feature: typeof features[0], index: number }) => {
  const { ref, inView } = useInView({ triggerOnce: true, threshold: 0.1 });
  
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      className="glass-panel p-8 rounded-2xl flex flex-col glow-border group cursor-pointer"
    >
      <div className="w-14 h-14 rounded-xl bg-[var(--color-surface-elevated)] border border-[var(--color-border-subtle)] flex items-center justify-center mb-6 group-hover:bg-[#1E2240] transition-colors relative overflow-hidden">
        {/* Glow effect back */}
        <div className="absolute inset-0 bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-secondary)] opacity-10 group-hover:opacity-30 transition-opacity"></div>
        <feature.icon className="w-7 h-7 text-[var(--color-primary)] group-hover:text-white transition-colors glow-text z-10" />
      </div>
      
      <h3 className="text-xl font-bold font-display text-[var(--color-text-primary)] mb-3">
        {feature.title}
      </h3>
      <p className="text-[var(--color-text-muted)] leading-relaxed">
        {feature.description}
      </p>
    </motion.div>
  );
};

const Features: React.FC = () => {
  const { ref: headerRef, inView: headerInView } = useInView({ triggerOnce: true, threshold: 0.2 });

  return (
    <section id="features" className="py-24 relative z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <motion.div 
          ref={headerRef}
          initial={{ opacity: 0, y: 20 }}
          animate={headerInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-sm font-mono text-[var(--color-primary)] tracking-widest uppercase mb-3">Core Capabilities</h2>
          <h3 className="text-4xl md:text-5xl font-display font-bold text-[var(--color-text-primary)]">
            Everything you need to <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)]">understand shopper behavior</span>
          </h3>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <FeatureCard key={index} feature={feature} index={index} />
          ))}
        </div>

      </div>
    </section>
  );
};

export default Features;
