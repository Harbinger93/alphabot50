import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Activity } from 'lucide-react';

interface MarketCardProps {
  data: any;
}

export default function MarketCard({ data }: MarketCardProps) {
  if (!data) return <div className="glass-card h-48 animate-pulse" />;

  const isWhale = data.indicators.whale_signal;

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.01 }}
      className={`glass-card flex flex-col justify-between neon-border-cyan mb-5 p-7 ${isWhale ? 'border-amber-500/50 shadow-amber-500/20 shadow-lg' : ''}`}
    >
      {isWhale && (
        <div className="absolute top-0 left-0 w-full h-1 bg-amber-500 pulse-glow" />
      )}
      
      <div>
        <div className="flex justify-between items-center mb-8 px-1">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/20">
              <Activity className="w-5 h-5 neon-text-cyan" />
            </div>
            <div>
              <h2 className="text-xl font-bold uppercase tracking-tighter leading-none">{data.symbol}</h2>
              <div className="text-[10px] text-slate-500 font-mono mt-1 tracking-widest uppercase">Live Flux</div>
            </div>
          </div>
          <div className="stats-value text-2xl tracking-tighter font-mono text-white">
            <span className="text-slate-600 text-sm font-sans mr-1">$</span>
            {data.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-5 mb-2">
          <div className="p-5 rounded-2xl bg-black/40 border border-white/5 shadow-inner">
            <div className="label-caps mb-2 opacity-50">Z-Score</div>
            <div className={`stats-value text-2xl font-mono ${Math.abs(data.indicators.vol_z_score) > 2.0 ? 'neon-text-orange' : 'text-cyan-400'}`}>
              {data.indicators.vol_z_score > 0 ? '+' : ''}{data.indicators.vol_z_score.toFixed(2)}σ
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-black/40 border border-white/5 shadow-inner">
            <div className="label-caps mb-2 opacity-50">L/S Ratio</div>
            <div className={`stats-value text-2xl font-mono ${data.indicators.ls_ratio > 1.2 ? 'neon-text-cyan' : data.indicators.ls_ratio < 0.8 ? 'neon-text-rose' : 'text-purple-400'}`}>
              {data.indicators.ls_ratio.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 pt-4 border-t border-white/5 flex justify-between items-center text-[10px] text-slate-500 uppercase font-mono tracking-widest px-1">
        <div className="flex items-center gap-2">
          <div className={`w-1.5 h-1.5 rounded-full ${data.safety.cache_mode === 'redis' ? 'bg-cyan-500 shadow-[0_0_8px_#22d3ee]' : 'bg-slate-500'}`} />
          <span>Nodes: {data.safety.cache_mode}</span>
        </div>
        <div className="flex items-center gap-2 text-cyan-500/60 font-bold">
          <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse" />
          ANALYZING
        </div>
      </div>
    </motion.div>
  );
}
