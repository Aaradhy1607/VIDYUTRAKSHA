import {
  DataSourceMetadata,
  DetectedStormCell,
  HazardPredictions,
  RiskAssessment,
  CAPAlert,
  ModelBattleResult,
  HorizonSkillPoint,
  ModelHealthReport,
  FeatureDriftReport,
  HistoricalEvent,
  CorridorSafetyReport
} from '../types';

const API_BASE = '/api/v1';

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to fetch health');
    return res.json();
  },

  async getDataHealth(): Promise<{ total_sources: number; active_live_sources: number; registry: Record<string, DataSourceMetadata> }> {
    const res = await fetch(`${API_BASE}/data-health`);
    if (!res.ok) throw new Error('Failed to fetch data health');
    return res.json();
  },

  async getStorms(): Promise<{ timestamp: string; active_storm_count: number; storms: DetectedStormCell[] }> {
    const res = await fetch(`${API_BASE}/storms`);
    if (!res.ok) throw new Error('Failed to fetch active storms');
    return res.json();
  },

  async getStormById(id: string) {
    const res = await fetch(`${API_BASE}/storms/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch storm ${id}`);
    return res.json();
  },

  async getNowcast(horizon: number = 15): Promise<{ horizon_minutes: number; initialization_time: string; predictions: HazardPredictions; risk_assessment: RiskAssessment }> {
    const res = await fetch(`${API_BASE}/nowcast?horizon=${horizon}`);
    if (!res.ok) throw new Error('Failed to fetch nowcast');
    return res.json();
  },

  async getAlerts(): Promise<{ active_alerts_count: number; alerts: CAPAlert[] }> {
    const res = await fetch(`${API_BASE}/alerts`);
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async getModelArena(): Promise<{ leaderboard: ModelBattleResult[]; lead_time_skill_curves: Record<string, HorizonSkillPoint[]> }> {
    const res = await fetch(`${API_BASE}/model-arena`);
    if (!res.ok) throw new Error('Failed to fetch model arena');
    return res.json();
  },

  async getModelHealth(): Promise<ModelHealthReport> {
    const res = await fetch(`${API_BASE}/model-health`);
    if (!res.ok) throw new Error('Failed to fetch model health');
    return res.json();
  },

  async getDrift(): Promise<{ drift_summary: string; reports: FeatureDriftReport[] }> {
    const res = await fetch(`${API_BASE}/drift`);
    if (!res.ok) throw new Error('Failed to fetch drift reports');
    return res.json();
  },

  async getHistoricalEvents(): Promise<{ events_count: number; events: HistoricalEvent[] }> {
    const res = await fetch(`${API_BASE}/historical-events`);
    if (!res.ok) throw new Error('Failed to fetch historical events');
    return res.json();
  },

  async getHistoricalReplay(eventId: string): Promise<HistoricalEvent> {
    const res = await fetch(`${API_BASE}/replay/${eventId}`);
    if (!res.ok) throw new Error(`Failed to fetch replay for ${eventId}`);
    return res.json();
  },

  async evaluateCorridorSafety(params: {
    origin: string;
    origin_lat: number;
    origin_lon: number;
    destination: string;
    dest_lat: number;
    dest_lon: number;
  }): Promise<CorridorSafetyReport> {
    const res = await fetch(`${API_BASE}/corridor-safety`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error('Failed to evaluate corridor safety');
    return res.json();
  },

  async getScientificAudit() {
    const res = await fetch(`${API_BASE}/scientific-audit`);
    if (!res.ok) throw new Error('Failed to fetch scientific audit');
    return res.json();
  }
};
