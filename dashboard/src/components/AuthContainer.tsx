import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, ShieldCheck, ArrowRight, AlertTriangle } from 'lucide-react';
import Dashboard from './Dashboard';

const API_BASE = 'http://localhost:8000';

export default function AuthContainer() {
  const [token, setToken] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState<boolean | null>(null);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [backendDown, setBackendDown] = useState(false);

  useEffect(() => {
    setToken(localStorage.getItem('alpha_token'));
    checkInit();
  }, []);

  const checkInit = async () => {
    try {
      const res = await axios.get(`${API_BASE}/`);
      setIsInitialized(res.data.initialized);
      setBackendDown(false);
    } catch (err) {
      console.error("Error checking init:", err);
      setBackendDown(true);
    }
  };

  const handleAction = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const endpoint = isInitialized ? '/auth/login' : '/auth/init';

    try {
      const res = await axios.post(`${API_BASE}${endpoint}`, { password });
      if (isInitialized) {
        localStorage.setItem('alpha_token', res.data.access_token);
        setToken(res.data.access_token);
      } else {
        setIsInitialized(true);
        setPassword('');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error en la autenticación");
    } finally {
      setLoading(false);
    }
  };

  if (token) return <Dashboard />;

  if (backendDown) return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <div className="glass-card p-8 text-center border-rose-500/30">
        <AlertTriangle className="w-12 h-12 neon-text-rose mx-auto mb-4" />
        <h2 className="text-xl font-bold mb-2">Núcleo Offline</h2>
        <p className="text-slate-400 text-sm mb-6">El API del bot no responde en <code className="bg-white/5 px-2 py-1 rounded">localhost:8000</code>.</p>
        <button onClick={checkInit} className="text-cyan-500 hover:underline text-sm font-bold uppercase tracking-widest">Reintentar Conexión</button>
      </div>
    </div>
  );

  if (isInitialized === null) return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <div className="text-cyan-500 animate-pulse font-mono tracking-widest text-sm uppercase">
        Conectando con el Núcleo del Bot...
      </div>
    </div>
  );

  return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card w-full max-w-md p-8 text-center"
      >
        <div className="flex justify-center mb-6">
          <div className="p-4 rounded-full bg-cyan-500/10 border border-cyan-500/30">
            {isInitialized ? <Lock className="w-8 h-8 neon-text-cyan" /> : <ShieldCheck className="w-8 h-8 neon-text-orange" />}
          </div>
        </div>

        <h1 className="text-2xl font-bold mb-2">
          {isInitialized ? 'Mando de Control' : 'Configurar AlphaBot'}
        </h1>
        <p className="text-slate-400 mb-8">
          {isInitialized 
            ? 'Ingresa tu llave maestra para acceder' 
            : 'Solo tú puedes definir la contraseña inicial. Elige con sabiduría.'}
        </p>

        <form onSubmit={handleAction} className="space-y-4">
          <div className="relative">
            <input 
              type="password" 
              placeholder="Contraseña Maestra"
              className="w-full bg-slate-900/50 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-cyan-500 transition-colors"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <AnimatePresence>
            {error && (
              <motion.p 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-rose-500 text-sm"
              >
                {error}
              </motion.p>
            )}
          </AnimatePresence>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 rounded-xl transition-all flex items-center justify-center gap-2 group"
          >
            {loading ? 'Validando...' : (isInitialized ? 'Acceder' : 'Inicializar')}
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </form>

        <p className="mt-8 text-[10px] uppercase tracking-widest text-slate-500 font-mono">
          AlphaBot 93-50 SECURED SYSTEM
        </p>
      </motion.div>
    </div>
  );
}
