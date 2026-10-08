"""
Tests for FastAPI REST API Endpoints
"""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert "VIDYUTRAKSHA" in data["system"]


@pytest.mark.asyncio
async def test_data_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/data-health")
    assert response.status_code == 200
    data = response.json()
    assert "registry" in data
    assert "IMD_DWR_COMPOSITE" in data["registry"]


@pytest.mark.asyncio
async def test_storms_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/storms")
    assert response.status_code == 200
    data = response.json()
    assert data["active_storm_count"] >= 1
    assert len(data["storms"]) >= 1


@pytest.mark.asyncio
async def test_nowcast_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/nowcast?horizon=30")
    assert response.status_code == 200
    data = response.json()
    assert data["horizon_minutes"] == 30
    assert "predictions" in data
    assert "lightning" in data["predictions"]
    assert "risk_assessment" in data


@pytest.mark.asyncio
async def test_historical_replay_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/replay/DELHI_NORWESTER_20230523")
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == "DELHI_NORWESTER_20230523"
    assert len(data["frames"]) >= 4
