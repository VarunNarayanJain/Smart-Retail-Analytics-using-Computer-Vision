import React, { useEffect, useState } from 'react';
import { motion, useAnimation } from 'framer-motion';
import { useInView } from 'react-intersection-observer';

interface MetricCardProps {
  finalValue: string;
  label: string;
  delay: number;
}

const MetricCard: React.FC<MetricCardProps> = ({ finalValue, label, delay }) => {
  const { ref, inView } = useInView({ triggerOnce: true, threshold: 0.5 });
  const controls = useAnimation();
  const [displayValue, setDisplayValue] = useState("0");
  
  // Extract number, prefix, and suffix
  const numMatch = finalValue.match(/[\d.]+/);
  const targetNumber = numMatch ? parseFloat(numMatch[0]) : 0;
  const prefix = finalValue.substring(0, finalValue.indexOf(numMatch ? numMatch[0] : finalValue)) || "";
  const suffix = finalValue.substring(finalValue.indexOf(numMatch ? numMatch[0] : "") + (numMatch ? numMatch[0].length : 0)) || "";

  useEffect(() => {
    if (inView) {
      controls.start("visible");
      
      let startTimestamp: number | null = null;
      const duration = 2000; // 2 seconds

      const step = (timestamp: number) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        
        // Easing function (easeOutExpo)
        const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        
        const currentNumber = targetNumber * easeProgress;
        
        // Format based on whether it is a float or int
        const formattedNumber = targetNumber % 1 === 0 
           ? Math.floor(currentNumber).toString() 
           : currentNumber.toFixed(1);

        setDisplayValue(`${prefix}${formattedNumber}${suffix}`);

        if (progress < 1) {
          window.requestAnimationFrame(step);
        } else {
            setDisplayValue(finalValue);
        }
      };

      window.requestAnimationFrame(step);
    }
  }, [inView, controls, targetNumber, finalValue, prefix, suffix]);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={controls}
      variants={{
        visible: { opacity: 1, y: 0 }
      }}
      transition={{ duration: 0.6, delay }}
      className="glass-panel p-6 rounded-2xl relative overflow-hidden group hover:-translate-y-1 transition-transform duration-300"
    >
      {/* Top glowing border */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-[var(--color-primary)] opacity-70 group-hover:opacity-100 group-hover:shadow-[0_0_15px_var(--color-primary)] transition-all duration-300"></div>
      
      <div className="flex flex-col items-center justify-center text-center">
        <h3 className="text-4xl md:text-5xl font-display font-bold text-[var(--color-text-primary)] mb-2 tracking-tight">
          {displayValue}
        </h3>
        <p className="text-sm font-medium text-[var(--color-text-muted)] uppercase tracking-widest">
          {label}
        </p>
      </div>
    </motion.div>
  );
};

const MetricsStrip: React.FC = () => {
  const metrics = [
    { value: "94%", label: "Detection Accuracy" },
    { value: "<3ms", label: "Processing Latency" },
    { value: "12+", label: "Zone Types Tracked" },
    { value: "50K+", label: "Daily Detections Processed" },
  ];

  return (
    <section className="w-full py-16 md:py-24 relative z-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric, index) => (
            <MetricCard 
              key={index}
              finalValue={metric.value}
              label={metric.label}
              delay={index * 0.15}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default MetricsStrip;
