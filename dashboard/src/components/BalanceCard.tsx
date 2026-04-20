import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Wallet, Landmark, ArrowUpRight, DollarSign } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function BalanceCard() {
  const [balance, setBalance] = useState<any>(null);

  useEffect(() => {
    const fetchBalance = async () => {
      try {
        const res = await axios.get(`${API_BASE}/balance`);
        setBalance(res.data);
      } catch (err) {
        console.error("Error fetching balance:", err);
      }
    };

    fetchBalance();
    const interval = setInterval(fetchBalance, 30000);
    return () => clearInterval(interval);
  }, []);

  if (!balance) return <div className="glass-card h-48 animate-pulse" />;

  const total = parseFloat(balance.total_usdt);
  const free = parseFloat(balance.free_usdt);
  const used = total - free;

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass-card h-full flex flex-col justify-between neon-border-cyan"
    >
      <div>
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-orange-500/10">
              <Wallet className="w-5 h-5 neon-text-orange" />
            </div>
            <h2 className="text-xl font-bold uppercase tracking-tighter">Balance</h2>
          </div>
          <div className="p-1 px-2.5 rounded border border-green-500/20 bg-green-500/10 text-[10px] text-green-400 font-bold uppercase tracking-widest shadow-[0_0_10px_rgba(34,197,94,0.2)]">
            Live Account
          </div>
        </div>

        <div className="mb-8">
          <div className="label-caps mb-1 flex items-center gap-1.5 opacity-70">
             Total Equity <Landmark className="w-3.5 h-3.5" />
          </div>
          <div className="text-4xl font-bold font-mono text-white tracking-tighter flex items-baseline gap-1">
            <span className="text-slate-500 text-2xl font-sans">$</span>
            {total.toLocaleString()}
          </div>
        </div>

        <div className="space-y-4">
          <div className="w-full bg-slate-800/50 h-2 rounded-full overflow-hidden border border-white/5">
            <div 
              className="bg-cyan-500 h-full shadow-[0_0_8px_rgba(34,211,238,0.5)]" 
              style={{ width: `${(used / (total || 1)) * 100}%` }}
            />
          </div>
          
          <div className="flex justify-between text-[11px] font-mono uppercase tracking-widest">
            <div className="text-slate-500">
              Libre: <span className="text-cyan-400 font-bold ml-1">${free.toLocaleString()}</span>
            </div>
            <div className="text-slate-500">
              En Orden: <span className="text-slate-300 font-bold ml-1">${used.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
