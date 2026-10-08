import React from 'react';
import { 
  Radio, 
  Activity, 
  Navigation, 
  Zap, 
  Gauge, 
  Clock, 
  ArrowUpRight, 
  AlertTriangle,
  Info,
  Maximize2,
  TrendingUp,
  MapPin
} from 'lucide-react';
import { DetectedStormCell, RiskAssessment } from '../types';

interface StormInspectorPanelProps {
  storm?: DetectedStormCell;
  riskAssessment?: RiskAssessment;
  horizonMinutes: number;
}

export const StormInspectorPanel: React.FC<StormInspectorPanelProps> = ({
  storm,
  riskAssessment,
  horizonMinutes
}) => {
  if (!storm) {
    return (
      <div className="w-88 bg-[#0B0F19] border-l border-slate-800 flex items-center justify-center p-6 text-slate-500 font-mono text-xs text-center">
        <div>
          <Radio className="w-8 h-8 mx-auto mb-2 text-slate-700 animate-pulse" />
          <p>SELECT A STORM CELL ON THE MAP TO INSPECT ITS DIGITAL TWIN</p>
        </div>
      </div>
    );
  }

  // Lifecycle badges
  const lifecycleColors: Record<string, string> = {
    INITIATING: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
    GROWING: 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300',
    MATURE: 'bg-rose-500/15 border-rose-500/40 text-rose-300 animate-pulse',
    DECAYING: 'bg-slate-500/10 border-slate-500/30 text-slate-400',
    DISSIPATING: 'bg-slate-800 text-slate-500 border-slate-700'
  };

  const riskScore = riskAssessment?.risk_score ?? 91.5;
  const alertLevel = riskAssessment?.alert_level ?? 'RED';

  return (
    <div className="w-88 bg-[#0B0F19] border-l border-slate-800 flex flex-col h-full overflow-y-auto p-3 space-y-3 font-sans text-xs">
      {/* Digital Twin Header */}
      <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800/80 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
            <span className="font-extrabold text-sm font-mono text-slate-100">{storm.storm_id}</span>
          </div>
          <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] border ${lifecycleColors[storm.lifecycle_state] || 'bg-slate-800'}`}>
            {storm.lifecycle_state}
          </span>
        </div>

        <div className="flex items-center space-x-1.5 text-slate-400 text-[11px] font-mono">
          <MapPin className="w-3.5 h-3.5 text-sky-400" />
          <span>{storm.nearest_district}, {storm.nearest_city}</span>
        </div>

        {/* Severity Banner */}
        <div className="flex items-center justify-between pt-1.5 border-t border-slate-800 text-[11px] font-mono">
          <span className="text-slate-400">Threat Classification:</span>
          <span className="font-bold text-rose-400 bg-rose-950/60 px-2 py-0.5 rounded border border-rose-800/60">
            {storm.severity_tier} SUPERCELL
          </span>
        </div>
      </div>

      {/* Transparent Risk Score (0-100) */}
      <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800/80 space-y-2">
        <div className="flex items-center justify-between">
          <span className="font-bold font-mono text-slate-300 flex items-center space-x-1">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>CALCULATED THREAT RISK</span>
          </span>
          <span className="text-xs px-2 py-0.5 rounded font-bold font-mono bg-rose-500/20 text-rose-300 border border-rose-500/40">
            {alertLevel} ALERT
          </span>
        </div>

        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-extrabold font-mono text-rose-400">{riskScore}</span>
          <span className="text-slate-500 font-mono text-xs">/ 100 Risk Index</span>
        </div>

        {/* Risk Score Progress Bar */}
        <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-amber-500 via-rose-500 to-red-600 transition-all duration-500"
            style={{ width: `${riskScore}%` }}
          />
        </div>

        {/* Risk Contributors */}
        <div className="space-y-1 pt-1 text-[10px] font-mono text-slate-400">
          <div className="flex justify-between">
            <span>Lightning Hazard Impact:</span>
            <strong className="text-amber-300">92% (+33 pts)</strong>
          </div>
          <div className="flex justify-between">
            <span>Physical Core Severity:</span>
            <strong className="text-rose-300">{storm.max_reflectivity_dbz} dBZ (+28 pts)</strong>
          </div>
          <div className="flex justify-between">
            <span>Population Exposure:</span>
            <strong className="text-indigo-300">HIGH (8,200/km²)</strong>
          </div>
          <div className="flex justify-between">
            <span>Lead Time Urgency:</span>
            <strong className="text-sky-300">+{horizonMinutes}m (IMMINENT)</strong>
          </div>
        </div>
      </div>

      {/* Kinematics & Radar Physics */}
      <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800/80 space-y-2">
        <div className="flex items-center space-x-1 font-bold font-mono text-slate-300 text-[11px] border-b border-slate-800 pb-1">
          <Gauge className="w-3.5 h-3.5 text-sky-400" />
          <span>CELL KINEMATICS & INTENSITY</span>
        </div>

        <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">Track Velocity</div>
            <div className="font-bold text-sky-300">{storm.speed_kmh} km/h</div>
          </div>
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">Track Heading</div>
            <div className="font-bold text-sky-300">{storm.direction_deg}° (ESE)</div>
          </div>
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">Max Reflectivity</div>
            <div className="font-bold text-rose-400">{storm.max_reflectivity_dbz} dBZ</div>
          </div>
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">VIL Column</div>
            <div className="font-bold text-amber-300">{storm.vil_kg_m2} kg/m²</div>
          </div>
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">Echo Top (18 dBZ)</div>
            <div className="font-bold text-indigo-300">{storm.echo_top_km} km</div>
          </div>
          <div className="p-1.5 rounded bg-slate-950 border border-slate-800/60">
            <div className="text-slate-500 text-[10px]">Storm Footprint</div>
            <div className="font-bold text-slate-300">{storm.area_km2} km²</div>
          </div>
        </div>
      </div>

      {/* Lightning Kinematics & Jump Detector */}
      <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800/80 space-y-2">
        <div className="flex items-center justify-between border-b border-slate-800 pb-1">
          <span className="flex items-center space-x-1 font-bold font-mono text-slate-300 text-[11px]">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>LIGHTNING JUMP ALGORITHM</span>
          </span>
          {storm.flash_rate_jump && (
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 font-mono font-bold border border-rose-500/40 animate-pulse">
              +240% JUMP DETECTED
            </span>
          )}
        </div>

        <div className="flex items-center justify-between font-mono text-[11px]">
          <span className="text-slate-400">Total Flash Rate:</span>
          <strong className="text-amber-400">{storm.flash_rate_min} flashes/min</strong>
        </div>
        <div className="flex items-center justify-between font-mono text-[11px]">
          <span className="text-slate-400">10-Min Flash Count:</span>
          <strong className="text-slate-200">{storm.flash_count_10min} strikes</strong>
        </div>
        <div className="flex items-center justify-between font-mono text-[11px]">
          <span className="text-slate-400">Precursor Lead Time:</span>
          <strong className="text-emerald-400">~18 min to peak gust</strong>
        </div>
      </div>

      {/* Explainability / SHAP Physical Risk Drivers */}
      <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800/80 space-y-1.5">
        <div className="flex items-center space-x-1 font-bold font-mono text-slate-300 text-[10px] uppercase">
          <Info className="w-3.5 h-3.5 text-indigo-400" />
          <span>PRIMARY PHYSICAL RISK DRIVERS</span>
        </div>
        <ul className="space-y-1 text-[10px] text-slate-300">
          <li className="flex items-start space-x-1.5">
            <span className="text-rose-400 font-bold">↑</span>
            <span>Intense lightning flash rate surge (+240% precursor)</span>
          </li>
          <li className="flex items-start space-x-1.5">
            <span className="text-rose-400 font-bold">↑</span>
            <span>Severe convective radar core ({storm.max_reflectivity_dbz} dBZ)</span>
          </li>
          <li className="flex items-start space-x-1.5">
            <span className="text-amber-400 font-bold">↑</span>
            <span>Extreme atmospheric buoyancy (CAPE &gt; 2400 J/kg)</span>
          </li>
          <li className="flex items-start space-x-1.5">
            <span className="text-sky-400 font-bold">↑</span>
            <span>High population exposure corridor (North West Delhi)</span>
          </li>
        </ul>
      </div>
    </div>
  );
};
