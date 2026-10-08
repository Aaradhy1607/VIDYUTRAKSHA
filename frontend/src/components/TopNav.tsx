import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Activity, 
  Database, 
  Swords, 
  History, 
  Compass, 
  FileCode2, 
  Radio, 
  AlertTriangle,
  Clock,
  Cpu
} from 'lucide-react';
import { AlertTier } from '../types';

interface TopNavProps {
  currentView: string;
  onSelectView: (view: string) => void;
  isReplayMode: boolean;
  replayEventTitle?: string;
  onExitReplay?: () => void;
  activeAlertCount: number;
  highestAlertTier: AlertTier;
}

export const TopNav: React.FC<TopNavProps> = ({
  currentView,
  onSelectView,
  isReplayMode,
  replayEventTitle,
  onExitReplay,
  activeAlertCount,
  highestAlertTier
}) => {
  const [timeUtc, setTimeUtc] = useState<string>('');
  const [timeIst, setTimeIst] = useState<string>('');

  useEffect(() => {
    const updateClocks = () => {
      const now = new Date();
      setTimeUtc(now.toUTCString().slice(17, 25) + ' UTC');
      // Indian Standard Time (UTC+5:30)
      const istString = new Intl.DateTimeFormat('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }).format(now);
      setTimeIst(istString + ' IST');
    };
    updateClocks();
    const timer = setInterval(updateClocks, 1000);
    return () => clearInterval(timer);
  }, []);

  const navItems = [
    { id: 'command', label: 'Command Centre', icon: Radio },
    { id: 'arena', label: 'Model Battle Arena', icon: Swords },
    { id: 'replay', label: 'Historical Replay', icon: History },
    { id: 'corridor', label: 'Transit Corridors', icon: Compass },
    { id: 'data-health', label: 'Data Sources', icon: Database },
    { id: 'model-health', label: 'Model Health', icon: Cpu },
    { id: 'audit', label: 'Scientific Audit', icon: FileCode2 },
  ];

  return (
    <header className="bg-[#0B0F19] border-b border-slate-800 text-slate-100 sticky top-0 z-50">
      {/* Upper Status Ribbon */}
      <div className="px-4 py-2 flex items-center justify-between border-b border-slate-800/80 bg-slate-950/60 text-xs">
        {/* Left: Brand Identity */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-400/40 text-sky-400">
              <ShieldAlert className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full animate-ping" />
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-base tracking-wider bg-gradient-to-r from-sky-400 via-cyan-300 to-indigo-300 bg-clip-text text-transparent font-mono">
                  VIDYUTRAKSHA
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded bg-sky-950/80 border border-sky-700/60 text-sky-300">
                  SIH PS72
                </span>
              </div>
              <p className="text-[10px] text-slate-400 hidden md:block">
                National Multi-Modal Thunderstorm & Lightning Early Warning Platform
              </p>
            </div>
          </div>

          {/* Operational Status Tag */}
          <div className="hidden lg:flex items-center pl-4 border-l border-slate-800 space-x-2">
            {isReplayMode ? (
              <div className="flex items-center space-x-2 px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                <span className="font-mono font-semibold">HISTORICAL REPLAY MODE</span>
                {replayEventTitle && <span className="text-slate-400">({replayEventTitle})</span>}
                {onExitReplay && (
                  <button 
                    onClick={onExitReplay}
                    className="ml-2 px-1.5 py-0.5 bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold rounded text-[10px]"
                  >
                    EXIT
                  </button>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>OPERATIONAL LIVE</span>
              </div>
            )}
          </div>
        </div>

        {/* Right: Operational Telemetry Badges */}
        <div className="flex items-center space-x-4">
          {/* Active Alerts Badge */}
          <div className={`flex items-center space-x-1.5 px-2.5 py-1 rounded border font-mono ${
            highestAlertTier === 'RED' 
              ? 'bg-rose-500/15 border-rose-500/40 text-rose-300 animate-pulse'
              : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
          }`}>
            <AlertTriangle className="w-3.5 h-3.5" />
            <span className="font-bold">{activeAlertCount} ACTIVE {highestAlertTier} ALERTS</span>
          </div>

          {/* Data Health */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300 font-mono">
            <Database className="w-3.5 h-3.5 text-sky-400" />
            <span>INGESTION: <strong className="text-emerald-400">6/6 LIVE</strong></span>
          </div>

          {/* Model Health */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300 font-mono">
            <Activity className="w-3.5 h-3.5 text-indigo-400" />
            <span>MODEL: <strong className="text-sky-300">92/100</strong> (18ms)</span>
          </div>

          {/* Real-time Clock */}
          <div className="flex items-center space-x-2 px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300 font-mono">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>{timeIst}</span>
            <span className="text-slate-500 hidden md:inline">| {timeUtc}</span>
          </div>
        </div>
      </div>

      {/* Lower Navigation Tabs */}
      <nav className="px-4 flex items-center space-x-1 overflow-x-auto py-1.5 bg-slate-900/90">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectView(item.id)}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-150 whitespace-nowrap ${
                isActive
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-400/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </header>
  );
};
