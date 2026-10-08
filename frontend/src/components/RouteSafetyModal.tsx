import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  MapPin, 
  AlertTriangle, 
  Zap, 
  CloudRain, 
  Wind, 
  Clock, 
  ShieldCheck,
  Search,
  ArrowRight
} from 'lucide-react';
import { CorridorSafetyReport } from '../types';
import { api } from '../services/api';

export const RouteSafetyModal: React.FC = () => {
  const [corridors, setCorridors] = useState<Array<{ name: string; origin: string; dest: string; origin_coord: [number, number]; dest_coord: [number, number] }>>([
    {
      name: 'Delhi Airport (IGI) → Noida Sector 62',
      origin: 'Delhi Airport (IGI)',
      dest: 'Noida Sector 62',
      origin_coord: [28.5562, 77.1000],
      dest_coord: [28.6280, 77.3649]
    },
    {
      name: 'Bhubaneswar → Cuttack Highway Corridor',
      origin: 'Bhubaneswar (Khurda)',
      dest: 'Cuttack City',
      origin_coord: [20.2961, 85.8245],
      dest_coord: [20.4625, 85.8828]
    },
    {
      name: 'Delhi → Gurugram CyberCity Corridor',
      origin: 'Connaught Place (Delhi)',
      dest: 'CyberCity Gurugram',
      origin_coord: [28.6315, 77.2167],
      dest_coord: [28.4950, 77.0895]
    }
  ]);

  const [selectedCorridorIndex, setSelectedCorridorIndex] = useState<number>(0);
  const [report, setReport] = useState<CorridorSafetyReport | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchReport = async (idx: number) => {
    const c = corridors[idx];
    setLoading(true);
    try {
      const res = await api.evaluateCorridorSafety({
        origin: c.origin,
        origin_lat: c.origin_coord[0],
        origin_lon: c.origin_coord[1],
        destination: c.dest,
        dest_lat: c.dest_coord[0],
        dest_lon: c.dest_coord[1]
      });
      setReport(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport(0);
  }, []);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-[#080C14] text-slate-100 font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <Compass className="w-6 h-6 text-teal-400" />
            <h1 className="text-xl font-extrabold font-mono tracking-wide text-slate-100">
              TRANSIT CORRIDOR WEATHER HAZARD EXPOSURE
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time multi-hazard exposure assessment along transportation corridors without claiming false deterministic safety.
          </p>
        </div>
      </div>

      {/* Corridor Selector */}
      <div className="flex flex-wrap gap-2">
        {corridors.map((c, i) => (
          <button
            key={c.name}
            onClick={() => {
              setSelectedCorridorIndex(i);
              fetchReport(i);
            }}
            className={`px-4 py-2 rounded-lg font-mono text-xs font-semibold transition-all border ${
              selectedCorridorIndex === i
                ? 'bg-teal-500/20 border-teal-500/60 text-teal-300'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {c.name}
          </button>
        ))}
      </div>

      {/* Safety Summary Banner */}
      {report && (
        <div className={`p-4 rounded-xl border space-y-3 ${
          report.overall_hazard_exposure === 'SEVERE'
            ? 'bg-rose-950/40 border-rose-600/60 text-rose-200'
            : report.overall_hazard_exposure === 'HIGH'
            ? 'bg-amber-950/40 border-amber-600/60 text-amber-200'
            : 'bg-slate-900 border-slate-800 text-slate-200'
        }`}>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
            <div>
              <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">CORRIDOR HAZARD EXPOSURE</div>
              <h2 className="text-lg font-bold font-mono">{report.corridor_name} ({report.total_distance_km} km)</h2>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`px-3 py-1 rounded font-mono font-extrabold text-xs border ${
                report.overall_hazard_exposure === 'SEVERE'
                  ? 'bg-rose-500/30 border-rose-500 text-rose-300'
                  : 'bg-amber-500/30 border-amber-500 text-amber-300'
              }`}>
                {report.overall_hazard_exposure} EXPOSURE (Risk: {report.max_risk_score}/100)
              </span>
            </div>
          </div>

          <p className="text-xs font-medium leading-relaxed">{report.safe_travel_advisory}</p>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 border-t border-slate-800 font-mono text-xs">
            <div>
              <div className="text-slate-400 text-[10px]">Peak Lightning Risk</div>
              <div className="font-bold text-amber-400">{(report.lightning_strike_probability * 100).toFixed(0)}% Probability</div>
            </div>
            <div>
              <div className="text-slate-400 text-[10px]">Highest Hazard Section</div>
              <div className="font-bold text-rose-400">{report.highest_risk_section}</div>
            </div>
            <div>
              <div className="text-slate-400 text-[10px]">Estimated Weather Delay</div>
              <div className="font-bold text-sky-400">~{report.estimated_transit_delay_minutes} minutes</div>
            </div>
          </div>
        </div>
      )}

      {/* Waypoint Breakdown Table */}
      {report && (
        <div className="command-panel rounded-xl p-4 border border-slate-800 space-y-3">
          <h3 className="font-bold font-mono text-sm text-slate-200">WAYPOINT SEGMENT ANALYSIS</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/80">
                  <th className="p-3">Waypoint / Section</th>
                  <th className="p-3">Coordinates</th>
                  <th className="p-3">P(Lightning)</th>
                  <th className="p-3">P(Heavy Rain)</th>
                  <th className="p-3">P(Severe Wind)</th>
                  <th className="p-3">Risk Score</th>
                  <th className="p-3">Impact Window</th>
                  <th className="p-3">Alert Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {report.waypoints_analysis.map((w) => (
                  <tr key={w.waypoint_index} className="hover:bg-slate-900/60 transition-colors">
                    <td className="p-3 font-bold text-slate-200">{w.name}</td>
                    <td className="p-3 text-slate-400">{w.lat.toFixed(3)}°, {w.lon.toFixed(3)}°</td>
                    <td className="p-3 text-amber-400 font-bold">{(w.p_lightning * 100).toFixed(0)}%</td>
                    <td className="p-3 text-sky-400">{(w.p_heavy_rain * 100).toFixed(0)}%</td>
                    <td className="p-3 text-teal-400">{(w.p_severe_wind * 100).toFixed(0)}%</td>
                    <td className="p-3 font-bold text-slate-100">{w.risk_score}/100</td>
                    <td className="p-3 text-slate-300">{w.impact_window_minutes}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        w.alert_tier === 'RED'
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                          : w.alert_tier === 'YELLOW'
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                          : 'bg-slate-800 text-slate-400'
                      }`}>
                        {w.alert_tier}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
