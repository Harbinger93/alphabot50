import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MarketCard from './MarketCard';
import BalanceCard from './BalanceCard';
import { LogOut, Bot, ShieldCheck, Play, Square, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

const API_BASE = 'http://localhost:8000';

export default function Dashboard() {
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activePos, setActivePos] = useState<any>(null);
  const [health, setHealth] = useState<'ok' | 'error' | 'loading'>('loading');

  useEffect(() => {
    const fetchStatus = async () => {
        try {
          const res = await axios.get(`${API_BASE}/bot/status`);
          setRunning(res.data.running);
          setActivePos(res.data.active_position);
        } catch (err) {
          console.error("Error fetching bot status:", err);
        }
    };

    const fetchHealth = async () => {
        try {
          const res = await axios.get(`${API_BASE}/health`);
          setHealth(res.data.status);
        } catch (err) {
          setHealth('error');
          console.error("Health check failed:", err);
        }
    };

    fetchStatus();
    fetchHealth();
    const statusInterval = setInterval(fetchStatus, 5000);
    const healthInterval = setInterval(fetchHealth, 10000);
    return () => {
      clearInterval(statusInterval);
      clearInterval(healthInterval);
    };
  }, []);

  const toggleBot = async () => {
    setLoading(true);
    try {
      if (running) {
        await axios.post(`${API_BASE}/bot/stop`);
        setRunning(false);
      } else {
        await axios.post(`${API_BASE}/bot/start`);
        setRunning(true);
      }
    } catch (err) {
      console.error("Error toggling bot:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="scan-line"></div>
      
      <div className="max-w-7xl mx-auto px-6 py-8 relative z-10">
        <header className="flex justify-between items-end mb-12">
          <div className="flex items-center gap-6">
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-500 blur-xl opacity-20 animate-pulse"></div>
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-slate-900 to-black flex items-center justify-center border border-cyan-400/30 relative z-10">
                <Bot className="w-8 h-8 text-cyan-400" />
              </div>
            </div>
            <div>
              <div className="label-caps mb-1 opacity-60">Neural Network Active</div>
              <h1 className="text-3xl font-bold tracking-tighter flex items-center gap-3">
                ALPHABOT <span className="text-cyan-500 font-mono">93-50</span>
              </h1>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-8 font-mono text-[10px]">
             <div className="flex flex-col items-end">
                <span className="text-slate-500 uppercase tracking-widest">System Status</span>
                <span className={`${health === 'ok' ? 'text-green-400' : health === 'error' ? 'text-rose-500 animate-pulse' : 'text-slate-500'} font-bold uppercase transition-colors duration-500`}>
                  {health === 'ok' ? 'Operational' : health === 'error' ? 'Connection Error' : 'Synchronizing...'}
                </span>
             </div>
             <div className="h-8 w-px bg-white/10"></div>
             <div className="flex flex-col items-end">
                <span className="text-slate-500 uppercase tracking-widest">Protocol</span>
                <span className="text-cyan-400 font-bold uppercase">Alpha-Convergence</span>
             </div>
          </div>
        </header>

        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch"
        >
          {/* 1. ANALYSIS (Market) */}
          <div className="flex flex-col">
            <div className="label-caps mb-4 ml-1 flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full shadow-[0_0_8px_#22d3ee]"></div>
              Market Analysis
            </div>
            <div className="flex-1">
              <MarketCard />
            </div>
          </div>

          {/* 2. EXECUTION (Strategy Engine) */}
          <div className="flex flex-col">
             <div className="label-caps mb-4 ml-1 flex items-center gap-2 text-purple-400">
              <div className="w-1.5 h-1.5 bg-purple-500 rounded-full shadow-[0_0_8px_#a855f7]"></div>
              Execution Core
            </div>
            <div className="glass-card flex-1 flex flex-col justify-between neon-border-cyan">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-xl ${running ? 'bg-cyan-500/10' : 'bg-slate-800/40'}`}>
                    <Play className={`w-5 h-5 ${running ? 'neon-text-cyan' : 'text-slate-500'}`} />
                  </div>
                  <h2 className="text-xl font-bold uppercase tracking-tighter">Engine</h2>
                </div>
                {running && (
                  <div className="flex items-center gap-1.5 text-[9px] font-bold text-cyan-400 bg-cyan-400/10 px-2.5 py-1 rounded-full border border-cyan-400/20">
                    SENSORS_ACTIVE
                  </div>
                )}
              </div>

              <div className="space-y-5 mb-8">
                <div className="p-5 rounded-2xl bg-black/60 border border-white/5">
                  <div className="label-caps mb-2 opacity-50">Node Status</div>
                  <div className={`text-sm font-bold flex items-center gap-3 ${running ? 'neon-text-cyan' : 'text-slate-500'}`}>
                    {running ? (
                      <>
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                        </span>
                        Hunting Anomalies...
                      </>
                    ) : (
                      'System Idle'
                    )}
                  </div>
                </div>

                {activePos ? (
                  <div className="p-5 rounded-2xl bg-purple-500/10 border border-purple-500/30">
                    <div className="label-caps mb-2 text-purple-400">Active Position</div>
                    <div className="flex justify-between items-center">
                      <span className="text-xl font-bold font-mono text-white">{activePos.side}</span>
                      <span className="text-2xl font-bold font-mono neon-text-purple">{activePos.quantity} BTC</span>
                    </div>
                  </div>
                ) : (
                  <div className="p-5 rounded-2xl border border-white/5 border-dashed flex flex-col items-center justify-center py-8 opacity-40">
                    <div className="text-[10px] text-slate-500 font-mono">_WAITING_SIGNAL_</div>
                  </div>
                )}
              </div>

              <button 
                onClick={toggleBot}
                disabled={loading}
                className={`w-full py-5 rounded-2xl flex items-center justify-center gap-3 font-bold uppercase tracking-[0.25em] transition-all relative overflow-hidden group ${
                  running 
                    ? 'bg-rose-500/10 hover:bg-rose-500/20 text-rose-500 border border-rose-500/30' 
                    : 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-2xl shadow-cyan-500/30'
                }`}
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                  running ? <><Square className="w-4 h-4 fill-current" /> Stop Core</> : <><Play className="w-4 h-4 fill-current" /> Start Core</>
                )}
              </button>
            </div>
          </div>

          {/* 3. RESULTS (Balance) */}
          <div className="flex flex-col">
            <div className="label-caps mb-4 ml-1 flex items-center gap-2 text-rose-400">
              <div className="w-1.5 h-1.5 bg-rose-500 rounded-full shadow-[0_0_8px_#f43f5e]"></div>
              Capital Node
            </div>
            <div className="flex-1">
              <BalanceCard />
            </div>
          </div>
        </motion.div>

        <footer className="mt-16 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4 opacity-30 text-[9px] uppercase font-mono tracking-[0.3em]">
          <div>&copy; 2026 Alfabot Neural Systems</div>
          <div className="flex items-center gap-6">
            <span>Server: Frankfurt_Node_01</span>
            <span>Latency: 2ms</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
