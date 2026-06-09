import React from 'react';
import { Zap } from 'lucide-react';

export function Navbar() {
  return (
    <nav className="border-b border-white/5 bg-[#090a0f]/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        
        {/* Left Side: Glowing Logo (Your Portfolio Style) */}
        <div className="flex items-center gap-2 cursor-pointer group">
          <div className="p-1.5 rounded-lg bg-accent-violet/10 text-accent-violet group-hover:bg-accent-violet/20 transition-all duration-300">
            <Zap className="w-5 h-5 fill-accent-violet/20" />
          </div>
          <span className="font-bold text-lg bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent group-hover:from-accent-violet group-hover:to-accent-pink transition-all duration-500">
            E-Com AI Platform
          </span>
        </div>

        {/* Right Side: Simple Active Navlinks */}
        <div className="flex items-center gap-8">
          <a href="#" className="text-sm font-medium text-white transition-all duration-300 hover:text-accent-violet">
            Dashboard
          </a>
          <a href="#" className="text-sm font-medium text-gray-400 transition-all duration-300 hover:text-accent-violet">
            Saved Audits
          </a>
          <a 
            href="http://127.0.0.1:8000/docs" 
            target="_blank" 
            rel="noreferrer" 
            className="text-sm font-medium text-gray-400 transition-all duration-300 hover:text-accent-violet"
          >
            API Docs 🔗
          </a>
        </div>

      </div>
    </nav>
  );
}