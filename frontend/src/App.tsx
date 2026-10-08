import React, { useState, useEffect } from 'react';
import { TopNav } from './components/TopNav';
import { ThreatSummaryPanel } from './components/ThreatSummaryPanel';
import { MapView } from './components/MapView';
import { StormInspectorPanel } from './components/StormInspectorPanel';
import { HorizonTimeline } from './components/HorizonTimeline';
import { ModelBattleArena } from './components/ModelBattleArena';
import { ReplayController } from './components/ReplayController';
import { DataHealthView } from './components/DataHealthView';
import { ModelHealthView } from './components/ModelHealthView';
import { RouteSafetyModal } from './components/RouteSafetyModal';
import { ScientificAuditModal } from './components/ScientificAuditModal';

import { 
  DetectedStormCell, 
  HazardPredictions, 
  RiskAssessment, 
  CAPAlert, 
  HistoricalEvent, 
  AlertTier 
} from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<string>('command');
  const [selectedHorizon, setSelectedHorizon] = useState<number>(15);
  const [activeStorms, setActiveStorms] = useState<DetectedStormCell[]>([]);
  const [selectedStormId, setSelectedStormId] = useState<string>('IN-DEL-042');
  const [selectedStorm, setSelectedStorm] = useState<DetectedStormCell | undefined>();
  const [predictions, setPredictions] = useState<HazardPredictions | undefined>();
  const [riskAssessment, setRiskAssessment] = useState<RiskAssessment | undefined>();
  const [activeAlerts, setActiveAlerts] = useState<CAPAlert[]>([]);
  
  // Replay Mode State
  const [isReplayMode, setIsReplayMode] = useState<boolean>(false);
  const [replayEventTitle, setReplayEventTitle] = useState<string>('');
  const [replayLightningStrikes, setReplayLightningStrikes] = useState<Array<{ lat: number; lon: number; polarity: string; ka: number }>>([]);

  // Fetch live nowcast and storm cells
  const fetchLiveState = async () => {
    try {
      const [stormsRes, nowcastRes, alertsRes] = await Promise.all([
        api.getStorms(),
        api.getNowcast(selectedHorizon),
        api.getAlerts()
      ]);

      setActiveStorms(stormsRes.storms);
      setPredictions(nowcastRes.predictions);
      setRiskAssessment(nowcastRes.risk_assessment);
      setActiveAlerts(alertsRes.alerts);

      const found = stormsRes.storms.find((s) => s.storm_id === selectedStormId) || stormsRes.storms[0];
      setSelectedStorm(found);
      if (found && found.storm_id !== selectedStormId) {
        setSelectedStormId(found.storm_id);
      }
    } catch (err) {
      console.error('Failed to fetch live state:', err);
    }
  };

  useEffect(() => {
    if (!isReplayMode) {
      fetchLiveState();
    }
  }, [selectedHorizon, isReplayMode]);

  // Load historical replay frame into map and inspector
  const handleLoadEventInMap = (event: HistoricalEvent, frameIndex: number) => {
    setIsReplayMode(true);
    setReplayEventTitle(event.title);
    const frame = event.frames[frameIndex];
    if (frame) {
      const replayCell: DetectedStormCell = {
        storm_id: frame.storm_state.storm_id,
        timestamp: frame.timestamp,
        centroid_lat: frame.storm_state.centroid_lat,
        centroid_lon: frame.storm_state.centroid_lon,
        area_km2: frame.storm_state.area_km2,
        perimeter_km: 78.0,
        max_reflectivity_dbz: frame.storm_state.max_dbz,
        mean_reflectivity_dbz: frame.storm_state.max_dbz * 0.75,
        vil_kg_m2: frame.storm_state.vil_kg_m2,
        echo_top_km: 14.5,
        eccentricity: 0.70,
        orientation_deg: 65.0,
        speed_kmh: frame.storm_state.speed_kmh,
        direction_deg: frame.storm_state.direction_deg,
        flash_rate_min: frame.storm_state.flash_rate_min,
        flash_count_10min: frame.lightning_count,
        flash_rate_jump: frame.storm_state.flash_rate_min >= 30,
        severity_tier: frame.storm_state.severity_tier,
        lifecycle_state: frame.storm_state.lifecycle_state,
        geometry_geojson: frame.storm_state.geometry,
        bounding_box: [frame.storm_state.centroid_lon - 0.2, frame.storm_state.centroid_lat - 0.1, frame.storm_state.centroid_lon + 0.2, frame.storm_state.centroid_lat + 0.1],
        nearest_district: event.location.split('(')[0].trim(),
        nearest_city: 'Target Sector'
      };

      setActiveStorms([replayCell]);
      setSelectedStorm(replayCell);
      setSelectedStormId(replayCell.storm_id);
      setReplayLightningStrikes(frame.lightning_strikes);
    }
  };

  const handleExitReplay = () => {
    setIsReplayMode(false);
    setReplayEventTitle('');
    setReplayLightningStrikes([]);
    fetchLiveState();
  };

  const highestTier: AlertTier = activeAlerts.length > 0 ? activeAlerts[0].alert_tier : 'GREEN';

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#080C14] text-slate-100">
      {/* Universal Top Navigation */}
      <TopNav
        currentView={currentView}
        onSelectView={setCurrentView}
        isReplayMode={isReplayMode}
        replayEventTitle={replayEventTitle}
        onExitReplay={handleExitReplay}
        activeAlertCount={activeAlerts.length}
        highestAlertTier={highestTier}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {currentView === 'command' && (
          <div className="flex-1 flex flex-col h-full w-full">
            {/* Operational Command Centre Workspace */}
            <div className="flex-1 flex overflow-hidden">
              {/* Left Panel: Multi-Hazard Summary & Sounding */}
              <ThreatSummaryPanel
                predictions={predictions}
                riskAssessment={riskAssessment}
                activeAlert={activeAlerts[0]}
                horizonMinutes={selectedHorizon}
              />

              {/* Center: Interactive Doppler Radar & LMS Map */}
              <MapView
                activeStorms={activeStorms}
                selectedStormId={selectedStormId}
                onSelectStorm={(id) => {
                  setSelectedStormId(id);
                  const s = activeStorms.find((c) => c.storm_id === id);
                  if (s) setSelectedStorm(s);
                }}
                horizonMinutes={selectedHorizon}
                lightningStrikes={replayLightningStrikes}
              />

              {/* Right Panel: Selected Storm Digital Twin */}
              <StormInspectorPanel
                storm={selectedStorm}
                riskAssessment={riskAssessment}
                horizonMinutes={selectedHorizon}
              />
            </div>

            {/* Bottom: Horizon Timeline Stepper */}
            <HorizonTimeline
              selectedHorizon={selectedHorizon}
              onSelectHorizon={setSelectedHorizon}
              isReplay={isReplayMode}
            />
          </div>
        )}

        {currentView === 'arena' && <ModelBattleArena />}
        {currentView === 'replay' && <ReplayController onLoadEventInMap={handleLoadEventInMap} />}
        {currentView === 'corridor' && <RouteSafetyModal />}
        {currentView === 'data-health' && <DataHealthView />}
        {currentView === 'model-health' && <ModelHealthView />}
        {currentView === 'audit' && <ScientificAuditModal />}
      </div>
    </div>
  );
};
