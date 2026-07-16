import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Camera, Bot, BarChart3 } from 'lucide-react';

const steps = [
  {
    icon: Camera,
    title: "Camera Feed Ingestion",
    description: "Live RTSP/video frames captured from store cameras in real-time, providing immediate visual data to our processing units."
  },
  {
    icon: Bot,
    title: "YOLOv8 Detection & SORT Tracking",
    description: "Every customer is detected, assigned a unique track ID, and followed seamlessly across contiguous or disjoint camera frames."
  },
  {
    icon: BarChart3,
    title: "Analytics Engine",
    description: "Dwell time, footfall, heatmaps, and actionable alerts are generated strictly in real time based on complex movement data."
  }
];

const StepItem = ({ step, index }: { step: typeof steps[0], index: number }) => {
  const { ref, inView } = useInView({ triggerOnce: true, threshold: 0.4 });
  
  return (
    <div ref={ref} className="relative z-10 flex flex-col md:flex-row items-start gap-8 mb-20 last:mb-0 group">
      {/* Number Circle */}
      <motion.div 
        initial={{ scale: 0.5, opacity: 0, boxShadow: "none" }}
        animate={inView ? { 
          scale: 1, 
          opacity: 1,
          boxShadow: "0 0 20px rgba(124, 111, 224, 0.4), inset 0 0 20px rgba(124, 111, 224, 0.2)"
        } : { scale: 0.5, opacity: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="w-20 h-20 shrink-0 rounded-full bg-[var(--color-surface)] border-2 border-[var(--color-primary)] flex items-center justify-center relative z-20"
      >
         <span className="text-3xl font-display font-bold text-[var(--color-text-primary)]">
           {index + 1}
         </span>
         <div className="absolute -inset-4 bg-[var(--color-primary)] blur-[30px] rounded-full opacity-0 group-hover:opacity-20 transition-opacity duration-500"></div>
      </motion.div>

      {/* Content Card */}
      <motion.div 
        initial={{ opacity: 0, x: -30 }}
        animate={inView ? { opacity: 1, x: 0 } : { opacity: 0, x: -30 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="flex-1 glass-panel p-8 rounded-2xl glow-border"
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 rounded-lg bg-[#151829] border border-[var(--color-border-subtle)]">
             <step.icon className="w-6 h-6 text-[var(--color-secondary)]" />
          </div>
          <h3 className="text-2xl font-bold font-display text-[var(--color-text-primary)]">
            {step.title}
          </h3>
        </div>
        <p className="text-[var(--color-text-muted)] text-lg leading-relaxed">
          {step.description}
        </p>
      </motion.div>
    </div>
  );
};

const HowItWorks: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start center", "end center"]
  });

  const lineHeight = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);
  
  const { ref: headerRef, inView: headerInView } = useInView({ triggerOnce: true, threshold: 0.2 });

  return (
    <section id="how-it-works" className="py-24 relative overflow-hidden bg-[var(--color-base)]">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <motion.div 
           ref={headerRef}
           initial={{ opacity: 0, y: 30 }}
           animate={headerInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
           transition={{ duration: 0.6 }}
           className="text-center mb-24"
        >
            <h2 className="text-4xl md:text-5xl font-display font-bold text-[var(--color-text-primary)] relative inline-block">
               How It Works
               <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-24 h-1 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] rounded-full"></div>
            </h2>
        </motion.div>

        <div className="relative py-10" ref={containerRef}>
            {/* Animated Connecting Line */}
            <div className="absolute left-10 md:left-10 top-0 bottom-0 w-[2px] bg-[#1E2240] translate-x-[-1px] rounded overflow-hidden">
               <motion.div 
                 className="absolute top-0 left-0 right-0 w-full bg-gradient-to-b from-[var(--color-primary)] to-[var(--color-secondary)]"
                 style={{ height: lineHeight }}
               />
               {/* Glow on the line */}
               <motion.div 
                 className="absolute top-0 left-0 right-0 w-full bg-[var(--color-primary)] blur-[5px]"
                 style={{ height: lineHeight, opacity: 0.5 }}
               />
            </div>
            
            <div className="relative z-10 flex flex-col pt-10 pb-10">
                {steps.map((step, idx) => (
                    <StepItem key={idx} step={step} index={idx} />
                ))}
            </div>
        </div>

      </div>
    </section>
  );
};

export default HowItWorks;
