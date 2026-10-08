import React, { useState, useEffect } from 'react';
import { 
  History, 
  Play, 
  Pause, 
  SkipForward, 
  SkipBack, 
  CheckCircle2, 
  AlertOctagon, 
  TrendingUp,
  RotateCcw,
  Zap,
  Radio,
  Gauge
} from 'lucide-react';
import { HistoricalEvent, ReplayFrame } from '../types';
import { api } from '../services/api';

interface ReplayControllerProps {
  onLoadEventInMap?: (event: HistoricalEvent, frameIndex: number) => void;
}

export const ReplayController: React.FC<ReplayControllerProps> = ({ onLoadEventInMap }) => {
  const [events, setEvents] = useState<HistoricalEvent[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string>('DELHI_NORWESTER_20230523');
  const [currentEvent, setCurrentEvent] = useState<HistoricalEvent | null>(null);
  const [currentFrameIndex, setCurrentFrameIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  useEffect(() => {
    async function fetchEvents() {
      try {
        const data = await api.getHistoricalEvents();
        setEvents(data.events);
        if (data.events.length > 0) {
          const detail = await api.getHistoricalReplay(data.events[0].event_id);
          setCurrentEvent(detail);
        }
      } catch (err) {
        console.error('Failed to load historical replay events:', err);
      }
    }
    fetchEvents();
  }, []);

  const handleSelectEvent = async (eventId: string) => {
    setSelectedEventId(eventId);
    setIsPlaying(false);
    setCurrentFrameIndex(0);
    try {
      const detail = await api.getHistoricalReplay(eventId);
      setCurrentEvent(detail);
      if (onLoadEventInMap && detail) {
        onLoadEventInMap(detail, 0);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Playback timer
  useEffect(() => {
    let interval: any;
    if (isPlaying && currentEvent && currentEvent.frames.length > 0) {
      interval = setInterval(() => {
        setCurrentFrameIndex((prev) => {
          const next = prev + 1;
          if (next >= currentEvent.frames.length) {
            setIsPlaying(false);
            return 0;
          }
          if (onLoadEventInMap) {
            onLoadEventInMap(currentEvent, next);
          }
          return next;
        });
      }, 4000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, currentEvent, onLoadEventInMap]);

  const frame: ReplayFrame | undefined = currentEvent?.frames[currentFrameIndex];

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-[#080C14] text-slate-100 font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <History className="w-6 h-6 text-amber-400" />
            <h1 className="text-xl font-extrabold font-mono tracking-wide text-slate-100">
              HISTORICAL REPLAY & VERIFICATION ENGINE
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Frame-by-frame scientific playback of severe convective events with side-by-side verification.
          </p>
        </div>
        <div className="mt-2 md:mt-0 px-3 py-1.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 font-mono text-xs font-bold">
          DEMO & VERIFICATION MODE
        </div>
      </div>

      {/* Event Selection Tabs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {events.map((ev) => {
          const isSelected = ev.event_id === selectedEventId;
          return (
            <div
              key={ev.event_id}
              onClick={() => handleSelectEvent(ev.event_id)}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                isSelected
                  ? 'bg-amber-500/10 border-amber-500/60 shadow-lg shadow-amber-500/5'
                  : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-sm text-slate-100 font-mono">{ev.title}</h3>
                  <div className="text-xs text-slate-400 mt-1">{ev.location} • {ev.date}</div>
                </div>
                <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-rose-500/20 border border-rose-500/40 text-rose-300">
                  {ev.alert_tier} ALERT
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-2 line-clamp-2">{ev.summary}</p>
              <div className="flex items-center space-x-4 mt-3 pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
                <span>Peak Reflectivity: <strong className="text-rose-400">{ev.peak_dbz} dBZ</strong></span>
                <span>Max Wind: <strong className="text-sky-300">{ev.peak_wind_gust_kmh} km/h</strong></span>
                <span>Warning Lead: <strong className="text-emerald-400">+{ev.evaluation_metrics.lead_time_warning_min}m</strong></span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Replay Control Bar & Frame Inspector */}
      {currentEvent && frame && (
        <div className="command-panel rounded-xl p-5 border border-slate-800 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-3">
              <span className="w-3 h-3 rounded-full bg-amber-400 animate-pulse" />
              <div>
                <span className="text-xs text-slate-400 font-mono">CURRENT PLAYBACK FRAME:</span>
                <h3 className="text-base font-bold font-mono text-slate-100">{frame.time_label}</h3>
              </div>
            </div>

            {/* Stepper Controls */}
            <div className="flex items-center space-x-2 mt-3 md:mt-0">
              <button
                onClick={() => {
                  const prev = Math.max(currentFrameIndex - 1, 0);
                  setCurrentFrameIndex(prev);
                  if (onLoadEventInMap) onLoadEventInMap(currentEvent, prev);
                }}
                disabled={currentFrameIndex === 0}
                className="p-2 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-30 text-slate-300"
              >
                <SkipBack className="w-4 h-4" />
              </button>

              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="flex items-center space-x-1.5 px-4 py-2 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold font-mono text-xs"
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                <span>{isPlaying ? 'PAUSE' : 'PLAY TIMELINE'}</span>
              </button>

              <button
                onClick={() => {
                  const next = Math.min(currentFrameIndex + 1, currentEvent.frames.length - 1);
                  setCurrentFrameIndex(next);
                  if (onLoadEventInMap) onLoadEventInMap(currentEvent, next);
                }}
                disabled={currentFrameIndex === currentEvent.frames.length - 1}
                className="p-2 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-30 text-slate-300"
              >
                <SkipForward className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Frame Telemetry Breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-xs">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div className="text-slate-500 text-[10px]">Storm Lifecycle State</div>
              <div className="font-bold text-base text-rose-400 mt-0.5">{frame.storm_state.lifecycle_state}</div>
              <div className="text-[10px] text-slate-400 mt-1">Reflectivity: {frame.storm_state.max_dbz} dBZ</div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div className="text-slate-500 text-[10px]">Lightning Flash Activity</div>
              <div className="font-bold text-base text-amber-300 mt-0.5">{frame.storm_state.flash_rate_min} flashes/min</div>
              <div className="text-[10px] text-slate-400 mt-1">Strikes: {frame.lightning_count} in frame</div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div className="text-slate-500 text-[10px]">Storm Kinematics</div>
              <div className="font-bold text-base text-sky-400 mt-0.5">{frame.storm_state.speed_kmh} km/h</div>
              <div className="text-[10px] text-slate-400 mt-1">Heading: {frame.storm_state.direction_deg}° (ESE)</div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div className="text-slate-500 text-[10px]">Warning Verification CSI</div>
              <div className="font-bold text-base text-emerald-400 mt-0.5">{(currentEvent.evaluation_metrics.csi_15min * 100).toFixed(1)}%</div>
              <div className="text-[10px] text-slate-400 mt-1">POD: {(currentEvent.evaluation_metrics.pod * 100).toFixed(1)}%</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
