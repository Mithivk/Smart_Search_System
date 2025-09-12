"use client";
import { useRouter } from "next/navigation";
import React, { useState, useEffect } from 'react';
import { Search, Zap, Globe, RefreshCw, ChevronRight, FileText } from 'lucide-react';


export default function Hero() {
  const router = useRouter();
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
  <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="relative max-w-7xl mx-auto px-6 py-20 lg:py-32">
          <div className={`text-center transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <h1 className="text-5xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Search <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">smarter</span> across your<br />
              Contentstack entries
            </h1>
            <p className="text-xl lg:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
              Contextual, multilingual, always up-to-date — find what you need instantly.
            </p>
            <button 
              onClick={() => router.push("/signup")}
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 text-lg"
            >
              🚀 Get Started
              <ChevronRight className="ml-2 h-5 w-5" />
            </button>
          </div>
        </div>
      </section>

  );
}
