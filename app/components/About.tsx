"use client";
import React, { useState, useEffect } from 'react';
import { Search, Zap, Globe, RefreshCw, ChevronRight, FileText } from 'lucide-react';


export default function About() {
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
<section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className={`transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
              Why teams love our search
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              {/* Feature 1 */}
              <div className="group bg-gradient-to-br from-blue-50 to-blue-100 p-8 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-2">
                <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Zap className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Contextual Search</h3>
                <p className="text-gray-700 text-lg leading-relaxed">
                  Go beyond keywords. Search by meaning, not just words. Find relevant content even when exact terms don't match.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="group bg-gradient-to-br from-purple-50 to-purple-100 p-8 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-2">
                <div className="w-16 h-16 bg-purple-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Globe className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Multilingual Support</h3>
                <p className="text-gray-700 text-lg leading-relaxed">
                  Find Hindi or Marathi entries even if you search in English. Break down language barriers effortlessly.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="group bg-gradient-to-br from-green-50 to-green-100 p-8 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-2">
                <div className="w-16 h-16 bg-green-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <RefreshCw className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Always Updated</h3>
                <p className="text-gray-700 text-lg leading-relaxed">
                  Entries sync automatically with your stack. No manual updates needed — search stays current.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

  );
}
