"use client";
import React,{useEffect,useState} from 'react'

const Footer = () => {
    const [isVisible, setIsVisible] = useState(false);
      const [searchQuery, setSearchQuery] = useState('');
    
        useEffect(() => {
        setIsVisible(true);
      }, []);
    
      const scrollToDemo = () => {
        document.getElementById('demo-section')?.scrollIntoView({ 
          behavior: 'smooth' 
        });
      };
    
  return (
    <footer className="py-16 bg-gradient-to-r from-gray-900 to-gray-800 text-white">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className={`transition-all duration-1000 delay-900 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <h3 className="text-2xl font-bold mb-4">Contentstack Smart Search</h3>
            <p className="text-gray-400">Built for TechSurf 2025</p>
          </div>
        </div>
      </footer>
  )
}

export default Footer