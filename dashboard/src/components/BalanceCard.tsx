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
      className="glass-card"
    >
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-orange-500/10">
            <Wallet className="w-5 h-5 neon-text-orange" />
          </div>
          <h2 className="text-lg font-semibold uppercase tracking-wider">Balance</h2>
        </div>
        <div className="p-1 px-2 rounded-md bg-green-500/10 text-green-400 text-[10px] font-bold uppercase">
          Live Account
        </div>
      </div>

      <div className="mb-6">
        <div className="text-sm text-slate-400 uppercase mb-1 flex items-center gap-1">
           Total Equity <Landmark className="w-3 h-3" />
        </div>
        <div className="text-3xl font-bold flex items-baseline gap-1">
          <span className="text-slate-500 text-lg">$</span>
          {total.toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </div>
      </div>

      <div className="space-y-3">
        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div 
            className="bg-cyan-500 h-full" 
            style={{ width: `${(used / total) * 100}%` }}
          />
        </div>
        
        <div className="flex justify-between text-xs font-mono uppercase">
          <div className="text-slate-400">
            Libre: <span className="text-cyan-400">${free.toLocaleString()}</span>
          </div>
          <div className="text-slate-400">
            En Orden: <span className="text-slate-200">${used.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
