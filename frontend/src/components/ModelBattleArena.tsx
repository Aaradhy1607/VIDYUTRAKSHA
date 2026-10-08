import React, { useState, useEffect } from 'react';
import { 
  Swords, 
  Trophy, 
  Activity, 
  TrendingDown, 
  Clock, 
  CheckCircle2, 
  XCircle,
  HelpCircle
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { ModelBattleResult, HorizonSkillPoint } from '../types';
import { api } from '../services/api';

export const ModelBattleArena: React.FC = () => {
  const [leaderboard, setLeaderboard] = useState<ModelBattleResult[]>([]);
  const [leadTimeCurves, setLeadTimeCurves] = useState<Record<string, HorizonSkillPoint[]>>({});
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadArena() {
      try {
        const data = await api.getModelArena();
        setLeaderboard(data.leaderboard);
        setLeadTimeCurves(data.lead_time_skill_curves);
      } catch (err) {
        console.error('Failed to load Model Arena:', err);
      } finally {
        setLoading(false);
      }
    }
    loadArena();
  }, []);

  // Format data for Recharts
  const chartData = [15, 30, 60, 90, 120, 180].map((h) => {
    const point: any = { horizon: `+${h}m` };
    for (const [modelName, points] of Object.entries(leadTimeCurves)) {
      const match = points.find((p) => p.horizon_minutes === h);
      if (match) {
        point[modelName] = match.csi;
      }
    }
    return point;
  });

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-[#080C14] text-slate-100 font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <Swords className="w-6 h-6 text-sky-400" />
            <h1 className="text-xl font-extrabold font-mono tracking-wide text-slate-100">
              MODEL BATTLE ARENA & BENCHMARK
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Rigorous comparative verification of validated operational models on Indian severe convective events.
          </p>
        </div>
        <div className="mt-2 md:mt-0 px-3 py-1.5 rounded bg-sky-950/60 border border-sky-700/60 text-sky-300 font-mono text-xs">
          WMO Standard CSI / POD / FAR / ETS Metrics
        </div>
      </div>

      {/* Model Leaderboard Table */}
      <div className="command-panel rounded-xl p-4 border border-slate-800">
        <h2 className="text-sm font-bold font-mono text-slate-200 mb-3 flex items-center space-x-2">
          <Trophy className="w-4 h-4 text-amber-400" />
          <span>OPERATIONAL MODEL LEADERBOARD</span>
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/80">
                <th className="p-3">Rank</th>
                <th className="p-3">Model Architecture</th>
                <th className="p-3">CSI (+15m)</th>
                <th className="p-3">CSI (+30m)</th>
                <th className="p-3">CSI (+60m)</th>
                <th className="p-3">POD (Hit Rate)</th>
                <th className="p-3">FAR (False Alarms)</th>
                <th className="p-3">Brier Score</th>
                <th className="p-3">Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {leaderboard.map((m) => (
                <tr 
                  key={m.model_version}
                  className={`hover:bg-slate-900/60 transition-colors ${
                    m.operational_rank === 1 ? 'bg-sky-500/5' : ''
                  }`}
                >
                  <td className="p-3">
                    <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-bold text-xs ${
                      m.operational_rank === 1
                        ? 'bg-amber-400/20 text-amber-300 border border-amber-400/40'
                        : m.operational_rank === 2
                        ? 'bg-slate-700 text-slate-300'
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      #{m.operational_rank}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="font-bold text-slate-200">{m.model_name}</div>
                    <div className="text-[10px] text-slate-500">{m.model_type}</div>
                  </td>
                  <td className="p-3 font-bold text-emerald-400">{(m.csi_15min * 100).toFixed(1)}%</td>
                  <td className="p-3 font-bold text-sky-400">{(m.csi_30min * 100).toFixed(1)}%</td>
                  <td className="p-3 font-bold text-amber-400">{(m.csi_60min * 100).toFixed(1)}%</td>
                  <td className="p-3 text-slate-300">{(m.overall_pod * 100).toFixed(1)}%</td>
                  <td className="p-3 text-rose-400">{(m.overall_far * 100).toFixed(1)}%</td>
                  <td className="p-3 text-slate-300">{m.overall_brier.toFixed(3)}</td>
                  <td className="p-3 text-slate-400 font-semibold">{m.inference_latency_ms} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Lead Time Skill Degradation Chart */}
      <div className="command-panel rounded-xl p-4 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold font-mono text-slate-200 flex items-center space-x-2">
            <TrendingDown className="w-4 h-4 text-sky-400" />
            <span>LEAD-TIME SKILL DEGRADATION CURVE (CSI vs LEAD TIME)</span>
          </h2>
          <span className="text-slate-400 text-xs font-mono">
            Scientific Truth: Skill decays over time from +15m to +180m
          </span>
        </div>

        <div className="h-72 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis dataKey="horizon" stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 11 }} />
              <YAxis domain={[0, 1]} stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '11px', fontFamily: 'monospace' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
              <Line type="monotone" dataKey="Model D (Multi-Modal Fusion)" stroke="#38BDF8" strokeWidth={3} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="Model C (Spatiotemporal DL)" stroke="#A855F7" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="Model B (Tabular LightGBM)" stroke="#F59E0B" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="Model A (Persistence Baseline)" stroke="#64748B" strokeWidth={2} strokeDasharray="4 4" dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
