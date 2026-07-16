import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { useInView } from 'react-intersection-observer';

const footfallData = [
  { time: '09:00', count: 12 }, { time: '10:00', count: 45 }, { time: '11:00', count: 80 },
  { time: '12:00', count: 120 }, { time: '13:00', count: 150 }, { time: '14:00', count: 90 },
  { time: '15:00', count: 110 }, { time: '16:00', count: 130 }, { time: '17:00', count: 180 },
  { time: '18:00', count: 210 }, { time: '19:00', count: 170 }, { time: '20:00', count: 80 }
];

const dwellData = [
  { zone: 'Electronics', dwell: 12.5 },
  { zone: 'Apparel', dwell: 8.2 },
  { zone: 'Checkout', dwell: 3.5 },
  { zone: 'Entrance', dwell: 1.2 },
  { zone: 'Beverages', dwell: 5.1 },
];
const barColors = ['#7C6FE0', '#4F8EF7', '#A78BFA', '#60A5FA', '#3B82F6'];

// Simple heatmap grid
const HeatmapSVG = () => (
    <div className="w-full h-full p-4 grid grid-cols-5 grid-rows-4 gap-2">
        {Array.from({ length: 20 }).map((_, i) => {
            const intensity = Math.random();
            let color = "bg-[#151829]";
            if (intensity > 0.9) color = "bg-[var(--color-primary)] glow-border";
            else if (intensity > 0.6) color = "bg-[var(--color-secondary)] opacity-80";
            else if (intensity > 0.3) color = "bg-[#3B82F6] opacity-40";

            return (
               <div key={i} className={`rounded-md w-full h-full transition-all duration-1000 ${color}`}></div>
            );
        })}
    </div>
);

const DashboardPreview: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });

  // Parallax + Tilt
  const yParallax = useTransform(scrollYProgress, [0, 1], [100, -100]);
  const rotateX = useTransform(scrollYProgress, [0, 0.5, 1], [15, 0, -5]);
  const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.8, 1, 0.9]);
  
  const { ref: headerRef, inView: headerInView } = useInView({ triggerOnce: true, threshold: 0.2 });

  return (
    <section id="dashboard" className="py-24 relative overflow-hidden" ref={containerRef}>
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[var(--color-primary)]/5 via-[var(--color-base)] to-[var(--color-base)] z-0"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        <motion.div 
           ref={headerRef}
           initial={{ opacity: 0, y: 30 }}
           animate={headerInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
           transition={{ duration: 0.8 }}
           className="text-center mb-16"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <span className="relative flex h-4 w-4">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--color-secondary)] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-4 w-4 bg-[var(--color-secondary)]"></span>
            </span>
            <span className="text-sm font-mono text-[var(--color-secondary)] tracking-widest uppercase">Live Analytics Dashboard</span>
          </div>
          <h2 className="text-3xl md:text-5xl font-display font-bold text-[var(--color-text-primary)]">
            Command Center for <span className="glow-text">Physical Retail</span>
          </h2>
        </motion.div>

        {/* Dashboard Mockup Container */}
        <div className="perspective-1000 relative">
          <motion.div 
            style={{ 
              y: yParallax,
              rotateX: rotateX,
              scale: scale,
            }}
            className="w-full glass-panel border border-[var(--color-primary)]/30 rounded-2xl p-4 md:p-6 shadow-[0_20px_50px_rgba(124,111,224,0.2)]"
          >
            {/* Mockup Header */}
            <div className="flex border-b border-[var(--color-border-subtle)] pb-4 mb-6">
               <div className="flex gap-2">
                 <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                 <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                 <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
               </div>
            </div>

            {/* Dashboard grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
               {/* left column - KPI & bar chart */}
               <div className="lg:col-span-1 flex flex-col gap-6">
                 
                 <div className="grid grid-cols-2 gap-4">
                    <div className="bg-[#0F1120] p-4 rounded-xl border border-[var(--color-border-subtle)] hover:border-[var(--color-primary)] transition-colors">
                      <p className="text-xs text-[var(--color-text-muted)] font-mono mb-1">Visitors Today</p>
                      <p className="text-2xl font-bold font-display text-white">1,284</p>
                    </div>
                    <div className="bg-[#0F1120] p-4 rounded-xl border border-[var(--color-border-subtle)] hover:border-[var(--color-primary)] transition-colors">
                      <p className="text-xs text-[var(--color-text-muted)] font-mono mb-1">Avg Dwell</p>
                      <p className="text-2xl font-bold font-display text-white">4.2m</p>
                    </div>
                    <div className="bg-[#0F1120] p-4 rounded-xl border border-[var(--color-border-subtle)] hover:border-[var(--color-primary)] transition-colors">
                      <p className="text-xs text-[var(--color-text-muted)] font-mono mb-1">Conversion</p>
                      <p className="text-2xl font-bold font-display text-white">23%</p>
                    </div>
                    <div className="bg-[#0F1120] p-4 rounded-xl border border-[var(--color-border-subtle)] hover:border-[var(--color-primary)] transition-colors">
                      <p className="text-xs text-[var(--color-text-muted)] font-mono mb-1">Peak Zone</p>
                      <p className="text-xl font-bold font-display text-[var(--color-primary)]">Electronics</p>
                    </div>
                 </div>

                 <div className="bg-[#0F1120] p-4 rounded-xl border border-[var(--color-border-subtle)] flex-1 min-h-[250px]">
                    <h3 className="text-sm font-medium text-[var(--color-text-muted)] mb-4">Avg Dwell Time by Zone (mins)</h3>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={dwellData} layout="vertical" margin={{ top: 0, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#1E2240" />
                        <XAxis type="number" stroke="#6B7280" fontSize={12} />
                        <YAxis dataKey="zone" type="category" stroke="#6B7280" fontSize={12} width={70} />
                        <Tooltip cursor={{fill: '#151829'}} contentStyle={{ backgroundColor: '#07080F', borderColor: '#1E2240' }} />
                        <Bar dataKey="dwell" radius={[0, 4, 4, 0]}>
                           {dwellData.map((_entry, index) => (
                             <Cell key={`cell-${index}`} fill={barColors[index % barColors.length]} />
                           ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                 </div>

               </div>

               {/* middle/right column - Area chart & Heatmap */}
               <div className="lg:col-span-2 flex flex-col gap-6">
                 
                 <div className="bg-[#0F1120] p-5 rounded-xl border border-[var(--color-border-subtle)] h-[300px]">
                   <h3 className="text-sm font-medium text-[var(--color-text-muted)] mb-4">Hourly Footfall (Real-Time)</h3>
                   <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={footfallData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <defs>
                          <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#7C6FE0" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#7C6FE0" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <XAxis dataKey="time" stroke="#6B7280" fontSize={12} />
                        <YAxis stroke="#6B7280" fontSize={12} />
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1E2240" />
                        <Tooltip contentStyle={{ backgroundColor: '#07080F', borderColor: '#1E2240' }} />
                        <Area type="monotone" dataKey="count" stroke="#7C6FE0" fillOpacity={1} fill="url(#colorCount)" strokeWidth={3} />
                      </AreaChart>
                   </ResponsiveContainer>
                 </div>

                 <div className="bg-[#0F1120] p-4 rounded-xl border border-[var(--color-border-subtle)] flex-1 min-h-[250px] flex flex-col">
                   <h3 className="text-sm font-medium text-[var(--color-text-muted)] mb-2 flex justify-between">
                     <span>Floor Plan Heatmap</span>
                     <span className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--color-secondary)] animate-pulse"></span>Live</span>
                   </h3>
                   <div className="flex-1 rounded-lg border border-[var(--color-border-subtle)] overflow-hidden relative bg-[#07080F]">
                     {/* Overlay Grid lines */}
                     <div className="absolute inset-0 bg-[linear-gradient(to_right,#1E2240_1px,transparent_1px),linear-gradient(to_bottom,#1E2240_1px,transparent_1px)] bg-[size:2rem_2rem] opacity-20"></div>
                     <HeatmapSVG />
                   </div>
                 </div>

               </div>
            </div>

          </motion.div>
        </div>

      </div>
    </section>
  );
};

export default DashboardPreview;
