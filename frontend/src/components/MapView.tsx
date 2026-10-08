import React, { useState } from 'react';
import { 
  MapContainer, 
  TileLayer, 
  Polygon, 
  CircleMarker, 
  Popup, 
  Polyline, 
  Tooltip 
} from 'react-leaflet';
import { 
  Layers, 
  Eye, 
  EyeOff, 
  Zap, 
  Radar as RadarIcon, 
  Radio, 
  Maximize2,
  Compass
} from 'lucide-react';
import { DetectedStormCell } from '../types';

interface MapViewProps {
  activeStorms: DetectedStormCell[];
  selectedStormId: string;
  onSelectStorm: (stormId: string) => void;
  horizonMinutes: number;
  lightningStrikes?: Array<{ lat: number; lon: number; polarity: string; ka: number }>;
}

export const MapView: React.FC<MapViewProps> = ({
  activeStorms,
  selectedStormId,
  onSelectStorm,
  horizonMinutes,
  lightningStrikes = []
}) => {
  // Layer Toggles
  const [showRadar, setShowRadar] = useState(true);
  const [showLightning, setShowLightning] = useState(true);
  const [showStormCells, setShowStormCells] = useState(true);
  const [showCones, setShowCones] = useState(true);
  const [radarOpacity, setRadarOpacity] = useState(0.75);

  // Default center over Delhi NCR
  const centerPosition: [number, number] = [28.62, 77.15];

  // Colormap thresholds (dBZ)
  const dbzLevels = [
    { dbz: 20, color: '#22c55e', label: '20 dBZ (Light Rain)' },
    { dbz: 35, color: '#eab308', label: '35 dBZ (Convective)' },
    { dbz: 45, color: '#f97316', label: '45 dBZ (Severe Storm)' },
    { dbz: 55, color: '#ef4444', label: '55 dBZ (Hail / Downburst)' },
    { dbz: 65, color: '#d946ef', label: '65+ dBZ (Extreme Supercell)' }
  ];

  return (
    <div className="flex-1 relative h-full w-full bg-[#080C14] overflow-hidden flex flex-col">
      {/* Map Control Overlay Bar */}
      <div className="absolute top-3 left-3 z-[1000] flex items-center space-x-2 bg-slate-900/90 border border-slate-800 backdrop-blur-md px-3 py-1.5 rounded-lg text-xs font-mono shadow-xl">
        <span className="text-slate-400 font-bold flex items-center space-x-1">
          <Layers className="w-3.5 h-3.5 text-sky-400" />
          <span>LAYERS:</span>
        </span>

        {/* Radar Toggle */}
        <button
          onClick={() => setShowRadar(!showRadar)}
          className={`flex items-center space-x-1 px-2 py-1 rounded transition-all ${
            showRadar ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40' : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <RadarIcon className="w-3 h-3" />
          <span>Doppler DWR</span>
        </button>

        {/* Lightning Toggle */}
        <button
          onClick={() => setShowLightning(!showLightning)}
          className={`flex items-center space-x-1 px-2 py-1 rounded transition-all ${
            showLightning ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <Zap className="w-3 h-3" />
          <span>LMS Lightning</span>
        </button>

        {/* Storm Cells Toggle */}
        <button
          onClick={() => setShowStormCells(!showStormCells)}
          className={`flex items-center space-x-1 px-2 py-1 rounded transition-all ${
            showStormCells ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40' : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <Radio className="w-3 h-3" />
          <span>Storm Cells</span>
        </button>

        {/* Forecast Cones Toggle */}
        <button
          onClick={() => setShowCones(!showCones)}
          className={`flex items-center space-x-1 px-2 py-1 rounded transition-all ${
            showCones ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          <Compass className="w-3 h-3" />
          <span>+{horizonMinutes}m Forecast Cone</span>
        </button>
      </div>

      {/* Radar dBZ Scale Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-slate-900/90 border border-slate-800 backdrop-blur-md p-2.5 rounded-lg text-[10px] font-mono shadow-xl space-y-1.5">
        <div className="text-slate-400 font-bold uppercase tracking-wider flex items-center justify-between">
          <span>IMD Radar Reflectivity (dBZ)</span>
          <span className="text-slate-500">ZMax</span>
        </div>
        <div className="flex items-center space-x-1">
          {dbzLevels.map((lvl) => (
            <div key={lvl.dbz} className="flex flex-col items-center">
              <div 
                className="w-7 h-2.5 rounded-sm"
                style={{ backgroundColor: lvl.color }}
              />
              <span className="text-slate-400 text-[9px] mt-0.5">{lvl.dbz}</span>
            </div>
          ))}
        </div>
        <div className="flex items-center justify-between pt-1 border-t border-slate-800 text-[9px] text-slate-400">
          <span>Lightning: <strong className="text-amber-400">+ CG</strong> / <strong className="text-sky-400">- CG</strong></span>
          <span>Lead Time: <strong className="text-slate-200">+{horizonMinutes} min</strong></span>
        </div>
      </div>

      {/* Leaflet Map Container */}
      <MapContainer
        center={centerPosition}
        zoom={9}
        scrollWheelZoom={true}
        className="w-full h-full flex-1 z-0"
        attributionControl={false}
      >
        {/* Dark Tactical Basemap */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          maxZoom={19}
        />

        {/* Doppler Radar Simulated Layer Grid Patches */}
        {showRadar && (
          <>
            {/* Convective Core 55 dBZ */}
            <CircleMarker
              center={[28.68, 77.08]}
              radius={38}
              pathOptions={{
                color: '#ef4444',
                fillColor: '#ef4444',
                fillOpacity: 0.45 * radarOpacity,
                weight: 1
              }}
            />
            {/* Severe Fringe 45 dBZ */}
            <CircleMarker
              center={[28.68, 77.08]}
              radius={60}
              pathOptions={{
                color: '#f97316',
                fillColor: '#f97316',
                fillOpacity: 0.30 * radarOpacity,
                weight: 1
              }}
            />
            {/* Convective Initiation 35 dBZ */}
            <CircleMarker
              center={[28.68, 77.08]}
              radius={85}
              pathOptions={{
                color: '#eab308',
                fillColor: '#eab308',
                fillOpacity: 0.18 * radarOpacity,
                weight: 1
              }}
            />
          </>
        )}

        {/* Detected Storm Cells */}
        {showStormCells && activeStorms.map((cell) => {
          const isSelected = cell.storm_id === selectedStormId;
          const coords: [number, number][] = cell.geometry_geojson.coordinates[0].map(
            (pt) => [pt[1], pt[0]] as [number, number]
          );

          // Velocity motion vector endpoint
          const speedFactor = (cell.speed_kmh / 111.13) * 0.4;
          const rad = (cell.direction_deg * Math.PI) / 180;
          const targetLat = cell.centroid_lat + speedFactor * Math.cos(rad);
          const targetLon = cell.centroid_lon + speedFactor * Math.sin(rad);

          return (
            <React.Fragment key={cell.storm_id}>
              {/* Storm Cell Polygon */}
              <Polygon
                positions={coords}
                eventHandlers={{
                  click: () => onSelectStorm(cell.storm_id)
                }}
                pathOptions={{
                  color: isSelected ? '#38BDF8' : '#F43F5E',
                  weight: isSelected ? 3 : 2,
                  fillColor: isSelected ? '#0284C7' : '#E11D48',
                  fillOpacity: isSelected ? 0.35 : 0.20,
                  dashArray: isSelected ? '4, 4' : undefined
                }}
              >
                <Tooltip direction="top" offset={[0, -10]} opacity={0.9}>
                  <div className="font-mono text-xs p-1">
                    <strong className="text-sky-300">{cell.storm_id}</strong>
                    <div>Intensity: <strong>{cell.max_reflectivity_dbz} dBZ</strong></div>
                    <div>Lifecycle: <strong>{cell.lifecycle_state}</strong></div>
                    <div>Speed: <strong>{cell.speed_kmh} km/h ({cell.direction_deg}°)</strong></div>
                  </div>
                </Tooltip>
              </Polygon>

              {/* Storm Centroid Icon */}
              <CircleMarker
                center={[cell.centroid_lat, cell.centroid_lon]}
                radius={isSelected ? 7 : 5}
                eventHandlers={{
                  click: () => onSelectStorm(cell.storm_id)
                }}
                pathOptions={{
                  color: '#FFFFFF',
                  fillColor: isSelected ? '#38BDF8' : '#F43F5E',
                  fillOpacity: 1,
                  weight: 2
                }}
              />

              {/* Motion Vector Arrow */}
              <Polyline
                positions={[
                  [cell.centroid_lat, cell.centroid_lon],
                  [targetLat, targetLon]
                ]}
                pathOptions={{
                  color: '#38BDF8',
                  weight: 2.5,
                  dashArray: '3, 4'
                }}
              />

              {/* Multi-Horizon Forecast Cone */}
              {showCones && (
                <CircleMarker
                  center={[targetLat, targetLon]}
                  radius={24 + (horizonMinutes * 0.15)}
                  pathOptions={{
                    color: '#FB7185',
                    fillColor: '#FB7185',
                    fillOpacity: 0.15,
                    weight: 1.5,
                    dashArray: '5, 5'
                  }}
                >
                  <Tooltip direction="right">
                    <span className="font-mono text-[10px]">
                      +{horizonMinutes}m Projected Impact Zone
                    </span>
                  </Tooltip>
                </CircleMarker>
              )}
            </React.Fragment>
          );
        })}

        {/* Lightning Strikes */}
        {showLightning && (
          <>
            {/* Real-time lightning strikes */}
            {[
              { lat: 28.69, lon: 77.06, polarity: '-', ka: -48.2 },
              { lat: 28.72, lon: 77.09, polarity: '-', ka: -54.0 },
              { lat: 28.67, lon: 77.12, polarity: '+', ka: 72.5 },
              { lat: 28.65, lon: 77.03, polarity: '-', ka: -38.0 },
              { lat: 28.71, lon: 77.15, polarity: '-', ka: -61.4 },
              { lat: 28.63, lon: 77.18, polarity: '+', ka: 84.0 },
              { lat: 28.46, lon: 77.04, polarity: '-', ka: -32.5 },
              { lat: 28.44, lon: 77.01, polarity: '-', ka: -28.0 }
            ].map((strike, idx) => {
              const isPositive = strike.polarity === '+';
              return (
                <CircleMarker
                  key={`lms-${idx}`}
                  center={[strike.lat, strike.lon]}
                  radius={isPositive ? 5 : 4}
                  pathOptions={{
                    color: isPositive ? '#F59E0B' : '#38BDF8',
                    fillColor: isPositive ? '#FBBF24' : '#67E8F9',
                    fillOpacity: 0.9,
                    weight: 1.5
                  }}
                >
                  <Popup>
                    <div className="font-mono text-xs p-1">
                      <div className="font-bold text-amber-400">⚡ IITM Lightning LMS Event</div>
                      <div>Type: <strong>{isPositive ? 'Positive (+CG)' : 'Negative (-CG)'}</strong></div>
                      <div>Peak Current: <strong>{strike.ka} kA</strong></div>
                      <div>Lat/Lon: {strike.lat.toFixed(3)}°, {strike.lon.toFixed(3)}°</div>
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
          </>
        )}
      </MapContainer>
    </div>
  );
};
