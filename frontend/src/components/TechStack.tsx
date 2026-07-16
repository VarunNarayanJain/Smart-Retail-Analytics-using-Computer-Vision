import React from 'react';
import { motion } from 'framer-motion';

const stack = [
  "YOLOv8", "SORT Tracker", "Python", "OpenCV", "FastAPI", "PostgreSQL", "React", "Recharts", "Three.js", "Framer Motion"
];

const TechStack: React.FC = () => {
  return (
    <section id="tech-stack" className="py-24 relative overflow-hidden bg-[url('/bg-lines.svg')] bg-cover">
      <div className="max-w-4xl mx-auto px-4 text-center">
        
        <h2 className="text-3xl md:text-4xl font-display font-bold text-[var(--color-text-primary)] mb-12">
          Built on Cutting-Edge <br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)]">CV Infrastructure</span>
        </h2>

        <div className="flex flex-wrap justify-center gap-4">
          {stack.map((tech, index) => (
            <motion.div
              key={tech}
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              whileInView={{ opacity: 1, scale: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{
                duration: 0.4,
                delay: index * 0.05,
                type: "spring",
                stiffness: 100
              }}
              className="px-6 py-3 rounded-full bg-[#0F1120] border border-[var(--color-primary)] text-[var(--color-primary)] font-mono text-sm shadow-[0_0_10px_rgba(124,111,224,0.1)] hover:bg-[var(--color-primary)] hover:text-white hover:shadow-[0_0_20px_rgba(124,111,224,0.4)] transition-all cursor-default"
            >
              {tech}
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  );
};

export default TechStack;
