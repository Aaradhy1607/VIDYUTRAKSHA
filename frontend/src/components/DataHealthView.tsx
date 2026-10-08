import React, { useState, useEffect } from 'react';
import { 
  Database, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  Activity, 
  ShieldCheck,
  RefreshCw,
  Info
} from 'lucide-react';
import { DataSourceMetadata } from '../types';
import { api } from '../services/api';

export const DataHealthView: React.FC = () => {
  const [registry, setRegistry] = useState<Record<string, DataSourceMetadata>>({});
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getDataHealth();
        setRegistry(data.registry);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const sources = Object.values(registry);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-[#080C14] text-slate-100 font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <Database className="w-6 h-6 text-sky-400" />
            <h1 className="text-xl font-extrabold font-mono tracking-wide text-slate-100">
              DATA SOURCE REGISTRY & INGESTION HEALTH
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time telemetry, latencies, Quality Control (QC) validation, and fallback modes across Indian meteorological feeds.
          </p>
        </div>
        <div className="mt-2 md:mt-0 flex items-center space-x-2 text-xs font-mono">
          <span className="px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold">
            6/6 STREAMS SYNCHRONIZED
          </span>
        </div>
      </div>

      {/* Sources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sources.map((src) => {
          const isLive = src.status === 'LIVE';
          return (
            <div 
              key={src.source_id}
              className="command-panel rounded-xl p-4 border border-slate-800 flex flex-col justify-between space-y-3"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-sm font-mono text-slate-100">{src.name}</h3>
                    <div className="text-[11px] text-slate-400">{src.provider}</div>
                  </div>
                  <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] border ${
                    isLive 
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                      : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                  }`}>
                    ● {src.status}
                  </span>
                </div>

                <div className="mt-3 space-y-1.5 text-xs font-mono">
                  <div className="flex justify-between text-slate-400">
                    <span>Latency:</span>
                    <strong className="text-slate-200">{src.latency_minutes} min</strong>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Spatial Resolution:</span>
                    <strong className="text-slate-200">{src.spatial_resolution}</strong>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Temporal Frequency:</span>
                    <strong className="text-slate-200">{src.temporal_resolution}</strong>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>QC Pass Rate:</span>
                    <strong className="text-emerald-400">{(src.qc_pass_rate * 100).toFixed(1)}%</strong>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>24h Ingested Records:</span>
                    <strong className="text-sky-300">{src.records_ingested_last_24h}</strong>
                  </div>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-800/80 text-[11px] text-slate-300">
                  <div className="text-slate-500 text-[10px] font-mono uppercase mb-0.5">Key Variables:</div>
                  <div className="flex flex-wrap gap-1">
                    {src.variables.slice(0, 3).map((v) => (
                      <span key={v} className="px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300 text-[10px] font-mono">
                        {v}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800 text-[10px] font-mono text-slate-400">
                <span className="text-slate-500">Fallback Strategy:</span>{' '}
                <strong className="text-amber-300">{src.fallback_strategy}</strong>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
