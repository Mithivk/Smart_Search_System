import Hero from "./components/LandingHero";
import About from "./components/About";
import FlowDiagram from "./components/FlowDiagram";
import Footer from "./components/Footer";

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      <Hero />
      <About />
      <Footer/>
    </main>
  );
}
