import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Clock, 
  TrendingDown, 
  Layers,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';

interface HorizonTimelineProps {
  selectedHorizon: number;
  onSelectHorizon: (horizon: number) => void;
  isReplay?: boolean;
}

export const HorizonTimeline: React.FC<HorizonTimelineProps> = ({
  selectedHorizon,
  onSelectHorizon,
  isReplay = false
}) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const horizons = [0, 15, 30, 60, 120, 180];

  const skillMap: Record<number, { skill: string; text: string; color: string }> = {
    0: { skill: '100%', text: 'Observed Truth (DWR/LMS)', color: 'text-emerald-400' },
    15: { skill: '95%', text: 'High Skill Optical Flow', color: 'text-emerald-400' },
    30: { skill: '85%', text: 'Strong Convective Extrapolation', color: 'text-sky-300' },
    60: { skill: '68%', text: 'Mesoscale Growth / Decay', color: 'text-amber-300' },
    120: { skill: '48%', text: 'NWP Fusion Blended', color: 'text-orange-400' },
    180: { skill: '32%', text: 'Synoptic Thermodynamic Prior', color: 'text-rose-400' }
  };

  // Automated playback cycle
  useEffect(() => {
    let interval: any;
    if (isPlaying) {
      interval = setInterval(() => {
        const currentIndex = horizons.indexOf(selectedHorizon);
        const nextIndex = (currentIndex + 1) % horizons.length;
        onSelectHorizon(horizons[nextIndex]);
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, selectedHorizon, horizons, onSelectHorizon]);

  return (
    <div className="bg-[#0B0F19] border-t border-slate-800 px-4 py-2 flex flex-col md:flex-row items-center justify-between space-y-2 md:space-y-0 text-xs font-mono">
      {/* Left: Playback Controls */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md font-bold transition-all ${
            isPlaying
              ? 'bg-rose-600 hover:bg-rose-500 text-white'
              : 'bg-sky-600 hover:bg-sky-500 text-white'
          }`}
        >
          {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
          <span>{isPlaying ? 'PAUSE STEPPER' : 'CYCLE HORIZONS'}</span>
        </button>

        <button
          onClick={() => onSelectHorizon(0)}
          className="p-1.5 rounded-md bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200"
          title="Reset to NOW"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>

        <span className="text-slate-400 pl-2 hidden sm:inline">
          TIMELINE: <strong className="text-slate-200">+{selectedHorizon} MIN NOWCAST</strong>
        </span>
      </div>

      {/* Center: Horizon Step Buttons */}
      <div className="flex items-center space-x-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800/80">
        {horizons.map((h) => {
          const isSelected = selectedHorizon === h;
          return (
            <button
              key={h}
              onClick={() => {
                setIsPlaying(false);
                onSelectHorizon(h);
              }}
              className={`px-3 py-1 rounded font-bold transition-all text-xs ${
                isSelected
                  ? 'bg-sky-500 text-slate-950 shadow-md scale-105'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              {h === 0 ? 'NOW' : `+${h}m`}
            </button>
          );
        })}
      </div>

      {/* Right: Operational Skill Transparency Indicator */}
      <div className="flex items-center space-x-2">
        <span className="text-slate-500 text-[11px] hidden lg:inline">Expected Model Skill:</span>
        <div className="flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-900 border border-slate-800">
          <TrendingDown className="w-3.5 h-3.5 text-slate-400" />
          <span className={`font-bold ${skillMap[selectedHorizon]?.color}`}>
            {skillMap[selectedHorizon]?.skill} CSI
          </span>
          <span className="text-slate-500 text-[10px] hidden xl:inline">
            ({skillMap[selectedHorizon]?.text})
          </span>
        </div>
      </div>
    </div>
  );
};
