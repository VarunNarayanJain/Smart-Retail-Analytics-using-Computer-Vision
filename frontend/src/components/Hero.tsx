import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

const ParticleNetwork = () => {
  const pointsRef = useRef<THREE.Points>(null);
  
  const particleCount = 50;
  const positions = useMemo(() => {
    const pos = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
        // Random positions over the floor
      pos[i * 3] = (Math.random() - 0.5) * 20; // x
      pos[i * 3 + 1] = Math.random() * 5 + 0.5; // y
      pos[i * 3 + 2] = (Math.random() - 0.5) * 20; // z
    }
    return pos;
  }, [particleCount]);

  useFrame((_state, delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += delta * 0.05;
    }
  });

  return (
    <group ref={pointsRef}>
      <Points positions={positions}>
        <PointMaterial transparent color="#4F8EF7" size={0.1} sizeAttenuation={true} depthWrite={false} />
      </Points>
    </group>
  );
};

const GridFloor = () => {
    return (
        <gridHelper args={[50, 50, "#7C6FE0", "#1E2240"]} position={[0, -2, 0]} />
    );
}

const HeroScene = () => {
  return (
    <Canvas camera={{ position: [0, 5, 15], fov: 60 }}>
      {/* Background dark color is handled by css, or we can use color */}
      <ambientLight intensity={0.5} />
      <ParticleNetwork />
      <GridFloor />
      {/* Add a subtle fog to blend the grid into the distance */}
      <fog attach="fog" args={['#07080F', 5, 30]} />
    </Canvas>
  );
};

const Hero: React.FC = () => {
  return (
    <section className="relative w-full h-screen flex flex-col justify-center items-center overflow-hidden">
      {/* 3D Background */}
      <div className="absolute inset-0 z-0 opacity-60">
          <HeroScene />
      </div>

      {/* Dark Overlay Gradient */}
      <div className="absolute inset-0 z-10 bg-gradient-to-b from-[#07080F]/50 via-transparent to-[#07080F]"></div>

      {/* Content */}
      <div className="relative z-20 max-w-5xl mx-auto px-4 text-center mt-16">
        <motion.h1 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-5xl md:text-7xl font-bold font-display tracking-tight text-[var(--color-text-primary)] mb-6"
        >
          Intelligent Retail. <br/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] glow-text">Real-Time Vision.</span>
        </motion.h1>

        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-lg md:text-xl text-[var(--color-text-muted)] max-w-3xl mx-auto mb-10 leading-relaxed"
        >
          Powered by YOLOv8 + SORT tracking. Detect, track, and analyze every customer interaction in your store — live.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <button className="px-8 py-3 rounded-full bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] text-white font-medium hover:scale-105 transition-transform shadow-[0_0_20px_rgba(124,111,224,0.4)]">
            View Dashboard
          </button>
          <button className="px-8 py-3 rounded-full border border-[var(--color-border-subtle)] hover:bg-[var(--color-surface)] hover:border-[var(--color-primary)] text-[var(--color-text-primary)] transition-all glass-panel">
            Read Paper
          </button>
        </motion.div>
      </div>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 1 }}
        className="absolute bottom-10 z-20 animate-bounce"
      >
        <ChevronDown className="w-8 h-8 text-[var(--color-primary)] opacity-70" />
      </motion.div>
    </section>
  );
};

export default Hero;
