import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';

interface MarketCardProps {
  data: any;
}

export default function MarketCard({ data }: MarketCardProps) {
  if (!data) return <div className="glass-card h-48 animate-pulse" />;

  const isWhale = data.indicators.whale_signal;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-card flex flex-col justify-between neon-border-cyan mb-4 ${isWhale ? 'border-amber-500/50 shadow-amber-500/20 shadow-lg' : ''}`}
    >
      {isWhale && (
        <div className="absolute top-0 left-0 w-full h-1 bg-amber-500 pulse-glow" />
      )}
      
      <div>
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10">
              <TrendingUp className="w-5 h-5 neon-text-cyan" />
            </div>
            <h2 className="text-xl font-bold uppercase tracking-tighter">{data.symbol}</h2>
          </div>
          <div className="stats-value text-2xl tracking-tighter font-mono">
            ${data.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-black/40 border border-white/5">
            <div className="label-caps mb-1 opacity-70">Z-Score</div>
            <div className={`stats-value text-xl ${Math.abs(data.indicators.vol_z_score) > 2.0 ? 'neon-text-orange' : 'text-cyan-400'}`}>
              {data.indicators.vol_z_score.toFixed(2)}σ
            </div>
          </div>

          <div className="p-4 rounded-xl bg-black/40 border border-white/5">
            <div className="label-caps mb-1 opacity-70">LS Ratio</div>
            <div className={`stats-value text-xl ${data.indicators.ls_ratio > 1.2 ? 'neon-text-cyan' : data.indicators.ls_ratio < 0.8 ? 'neon-text-rose' : 'text-purple-400'}`}>
              {data.indicators.ls_ratio.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 pt-3 border-t border-white/5 flex gap-4 text-[9px] text-slate-500 uppercase font-mono tracking-widest">
        <div className="flex items-center gap-1">
          <div className={`w-1 h-1 rounded-full ${data.safety.cache_mode === 'redis' ? 'bg-cyan-500' : 'bg-slate-500'}`} />
          {data.safety.cache_mode}
        </div>
        <div className="ml-auto flex items-center gap-1 text-cyan-500/50">
          <div className="w-1 h-1 rounded-full bg-cyan-500 animate-pulse" />
          LIVE
        </div>
      </div>
    </motion.div>
  );
}
