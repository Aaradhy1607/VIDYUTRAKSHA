import React from 'react';
import { 
  Zap, 
  CloudLightning, 
  CloudRain, 
  Wind, 
  Flame, 
  Thermometer, 
  Layers, 
  AlertOctagon,
  TrendingUp,
  ShieldCheck
} from 'lucide-react';
import { HazardPredictions, RiskAssessment, CAPAlert } from '../types';

interface ThreatSummaryPanelProps {
  predictions?: HazardPredictions;
  riskAssessment?: RiskAssessment;
  activeAlert?: CAPAlert;
  horizonMinutes: number;
}

export const ThreatSummaryPanel: React.FC<ThreatSummaryPanelProps> = ({
  predictions,
  riskAssessment,
  activeAlert,
  horizonMinutes
}) => {
  const hazards = [
    {
      id: 'lightning',
      name: 'Lightning Probability',
      icon: Zap,
      prob: predictions?.lightning.calibrated_probability ?? 0.88,
      p10: predictions?.lightning.p10 ?? 0.78,
      p90: predictions?.lightning.p90 ?? 0.94,
      color: 'from-amber-400 to-yellow-500',
      textColor: 'text-amber-400',
      borderColor: 'border-amber-500/40',
      badge: 'HIGH STRIKE FREQUENCY'
    },
    {
      id: 'storm',
      name: 'Thunderstorm Convection',
      icon: CloudLightning,
      prob: predictions?.thunderstorm.calibrated_probability ?? 0.94,
      p10: predictions?.thunderstorm.p10 ?? 0.86,
      p90: predictions?.thunderstorm.p90 ?? 0.98,
      color: 'from-indigo-400 to-purple-500',
      textColor: 'text-indigo-400',
      borderColor: 'border-indigo-500/40',
      badge: 'DEEP CONVECTIVE CORE'
    },
    {
      id: 'rain',
      name: 'Heavy Rain / Cloudburst',
      icon: CloudRain,
      prob: predictions?.heavy_rain.calibrated_probability ?? 0.78,
      p10: predictions?.heavy_rain.p10 ?? 0.68,
      p90: predictions?.heavy_rain.p90 ?? 0.86,
      color: 'from-sky-400 to-blue-500',
      textColor: 'text-sky-400',
      borderColor: 'border-sky-500/40',
      badge: 'HIGH VIL ACCUMULATION'
    },
    {
      id: 'wind',
      name: 'Severe Convective Wind',
      icon: Wind,
      prob: predictions?.severe_wind.calibrated_probability ?? 0.72,
      p10: predictions?.severe_wind.p10 ?? 0.60,
      p90: predictions?.severe_wind.p90 ?? 0.82,
      color: 'from-teal-400 to-emerald-500',
      textColor: 'text-teal-400',
      borderColor: 'border-teal-500/40',
      badge: 'SQUALL / GUST FRONT'
    }
  ];

  return (
    <div className="w-84 bg-[#0B0F19] border-r border-slate-800 flex flex-col h-full overflow-y-auto p-3 space-y-3 font-sans text-xs">
      {/* CAP Emergency Banner */}
      {activeAlert && (
        <div className={`p-2.5 rounded-lg border flex flex-col space-y-1.5 ${
          activeAlert.alert_tier === 'RED'
            ? 'bg-rose-950/40 border-rose-600/60 text-rose-200'
            : 'bg-amber-950/40 border-amber-600/60 text-amber-200'
        }`}>
          <div className="flex items-center justify-between">
            <span className="flex items-center space-x-1.5 font-bold font-mono tracking-wide text-[11px] text-rose-400">
              <AlertOctagon className="w-4 h-4 animate-bounce" />
              <span>CAP {activeAlert.alert_tier} ALERT</span>
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-900/80 border border-rose-700 font-mono">
              IMD / NDMA
            </span>
          </div>
          <p className="font-semibold text-xs leading-snug">{activeAlert.headline}</p>
          <div className="text-[10px] text-slate-300 flex justify-between font-mono pt-1 border-t border-rose-800/40">
            <span>Area: <strong>{activeAlert.areaDesc}</strong></span>
            <span>Risk: <strong>{activeAlert.risk_score}/100</strong></span>
          </div>
        </div>
      )}

      {/* Threat Summary Header */}
      <div className="flex items-center justify-between pb-1 border-b border-slate-800">
        <div className="flex items-center space-x-1.5">
          <Layers className="w-4 h-4 text-sky-400" />
          <h2 className="font-bold text-slate-200 uppercase tracking-wider text-[11px] font-mono">
            Multi-Hazard Nowcast (+{horizonMinutes}m)
          </h2>
        </div>
        <span className="text-[10px] text-slate-400 font-mono">
          Confidence: <strong className="text-emerald-400">{Math.round((predictions?.composite_confidence ?? 0.88) * 100)}%</strong>
        </span>
      </div>

      {/* Hazard Probability Gauges */}
      <div className="space-y-2.5">
        {hazards.map((h) => {
          const Icon = h.icon;
          const pct = Math.round(h.prob * 100);
          const p10Pct = Math.round(h.p10 * 100);
          const p90Pct = Math.round(h.p90 * 100);

          return (
            <div key={h.id} className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800/80 hover:border-slate-700 transition-all">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center space-x-1.5">
                  <Icon className={`w-3.5 h-3.5 ${h.textColor}`} />
                  <span className="font-medium text-slate-200">{h.name}</span>
                </div>
                <div className="text-right font-mono">
                  <span className={`font-extrabold text-sm ${h.textColor}`}>{pct}%</span>
                </div>
              </div>

              {/* Progress Bar with Conformal Interval Indicator */}
              <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden relative mb-1">
                <div 
                  className={`h-full bg-gradient-to-r ${h.color} transition-all duration-500`}
                  style={{ width: `${pct}%` }}
                />
              </div>

              {/* Conformal Uncertainty Interval */}
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span className="text-slate-500">P10-P90 Interval:</span>
                <span className="text-slate-300 font-semibold">{p10Pct}% – {p90Pct}%</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Atmospheric Instability Parameters */}
      <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800/80 space-y-2">
        <div className="flex items-center justify-between border-b border-slate-800 pb-1">
          <span className="flex items-center space-x-1 font-bold text-slate-300 text-[11px] font-mono">
            <Thermometer className="w-3.5 h-3.5 text-rose-400" />
            <span>SOUNDING THERMODYNAMICS</span>
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 font-mono font-bold">
            EXTREME
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">SBCAPE</div>
            <div className="font-bold text-amber-300">2,450 J/kg</div>
          </div>
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">CIN Barrier</div>
            <div className="font-bold text-slate-300">25 J/kg</div>
          </div>
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">Lifted Index</div>
            <div className="font-bold text-rose-400">-6.5 °C</div>
          </div>
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">0-6km Bulk Shear</div>
            <div className="font-bold text-sky-400">18.5 m/s</div>
          </div>
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">Total Totals</div>
            <div className="font-bold text-indigo-300">53.0 °C</div>
          </div>
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">PWAT (Moisture)</div>
            <div className="font-bold text-teal-300">54.0 mm</div>
          </div>
        </div>
      </div>

      {/* Active Sensor Modalities */}
      <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800/80 space-y-1.5">
        <div className="text-slate-400 font-bold font-mono text-[10px] uppercase">Active Fusion Streams</div>
        <div className="flex flex-wrap gap-1">
          {['IMD DWR', 'INSAT-3D IR', 'IITM Damini', 'NCMRWF GFS', 'AWS Surface'].map((mod) => (
            <span key={mod} className="flex items-center space-x-1 px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-[10px] font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>{mod}</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
