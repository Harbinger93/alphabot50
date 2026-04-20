import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { TrendingUp, Activity, Shield, Zap } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function MarketCard() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${API_BASE}/market-status`);
        setData(res.data);
      } catch (err) {
        console.error("Error fetching market data:", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div className="glass-card h-48 animate-pulse" />;

  const isWhale = data.indicators.whale_signal;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={`glass-card relative overflow-hidden ${isWhale ? 'border-amber-500/50 shadow-amber-500/20 shadow-lg' : ''}`}
    >
      {isWhale && (
        <div className="absolute top-0 left-0 w-full h-1 bg-amber-500 pulse-glow" />
      )}
      
      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10">
            <TrendingUp className="w-5 h-5 neon-text-cyan" />
          </div>
          <h2 className="text-lg font-semibold uppercase tracking-wider">{data.symbol}</h2>
        </div>
        <div className="text-2xl font-mono font-bold">
          ${data.price.toLocaleString()}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs text-slate-400 uppercase">
            <Activity className="w-3 h-3" />
            Z-Score Vol
          </div>
          <div className={`text-xl font-bold ${data.indicators.vol_z_score > 2.0 ? 'neon-text-orange' : ''}`}>
            {data.indicators.vol_z_score.toFixed(2)}σ
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs text-slate-400 uppercase">
            <Zap className="w-3 h-3" />
            LS Ratio
          </div>
          <div className={`text-xl font-bold ${data.indicators.ls_ratio > 1.2 ? 'neon-text-cyan' : data.indicators.ls_ratio < 0.8 ? 'neon-text-rose' : ''}`}>
            {data.indicators.ls_ratio.toFixed(2)}
          </div>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-white/5 flex justify-between items-center text-[10px] text-slate-500 uppercase font-mono">
        <div className="flex gap-3">
          <span className="flex items-center gap-1">
            <div className={`w-1.5 h-1.5 rounded-full ${data.safety.cache_mode === 'redis' ? 'bg-cyan-500' : 'bg-slate-500'}`} />
            {data.safety.cache_mode}
          </span>
          <span className="flex items-center gap-1">
            <div className={`w-1.5 h-1.5 rounded-full ${data.safety.persistence_mode === 'postgresql' ? 'bg-cyan-500' : 'bg-orange-500'}`} />
            {data.safety.persistence_mode.replace('_', ' ')}
          </span>
        </div>
        <span>Ready to trade</span>
      </div>
    </motion.div>
  );
}
