import React, { useState, useEffect } from 'react';
import MarketCard from './MarketCard';
import BalanceCard from './BalanceCard';
import { LogOut, Bot, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Dashboard() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    setToken(localStorage.getItem('alpha_token'));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('alpha_token');
    window.location.reload();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <header className="flex justify-between items-center mb-12">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-600 to-blue-800 flex items-center justify-center border border-cyan-400/30 shadow-lg shadow-cyan-500/20">
            <Bot className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">AlphaBot 93-50</h1>
            <div className="flex items-center gap-2 text-xs text-cyan-500/80 font-mono mt-1">
              <ShieldCheck className="w-3 h-3" />
              SYSTEM SECURED & ACTIVE
            </div>
          </div>
        </div>

        <button 
          onClick={handleLogout}
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors bg-white/5 px-4 py-2 rounded-lg border border-white/10"
        >
          <LogOut className="w-4 h-4" />
          <span className="text-sm font-semibold uppercase tracking-wider">Salir</span>
        </button>
      </header>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        <MarketCard />
        <BalanceCard />
        
        {/* Placeholder for future Strategy Control Card */}
        <div className="glass-card flex flex-col items-center justify-center text-center opacity-40 grayscale pointer-events-none">
          <div className="p-4 rounded-full bg-slate-800 mb-4">
            <Bot className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold">Strategy Engine</h3>
          <p className="text-sm text-slate-500">Próxima fase activa en casa</p>
        </div>
      </motion.div>

      <footer className="mt-20 pt-8 border-t border-white/5 text-center text-slate-600 text-[10px] uppercase font-mono tracking-widest">
        &copy; 2026 Alfabot Systems | Global Trading Intelligence
      </footer>
    </div>
  );
}
