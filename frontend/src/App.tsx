import Navbar from './components/Navbar';
import Hero from './components/Hero';
import MetricsStrip from './components/MetricsStrip';
import HowItWorks from './components/HowItWorks';
import DashboardPreview from './components/DashboardPreview';
import Features from './components/Features';
import TechStack from './components/TechStack';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen bg-[var(--color-base)] text-[var(--color-text-primary)] selection:bg-[var(--color-primary)] selection:text-white flex flex-col relative w-full overflow-x-hidden">
      <Navbar />
      
      <main className="flex-1 w-full flex flex-col">
        {/* Background ambient light effects */}
        <div className="fixed top-0 left-0 w-full h-[500px] bg-[var(--color-primary)] opacity-[0.03] blur-[100px] pointer-events-none"></div>
        <div className="fixed bottom-0 right-0 w-[500px] h-[500px] bg-[var(--color-secondary)] opacity-[0.03] blur-[150px] pointer-events-none rounded-full"></div>

        <Hero />
        <MetricsStrip />
        <HowItWorks />
        <DashboardPreview />
        <Features />
        <TechStack />
      </main>

      <Footer />
    </div>
  );
}

export default App;
