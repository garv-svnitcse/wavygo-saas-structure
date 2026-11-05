from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_dashboard_stats():
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()

    assert "total_vehicles" in data
    assert "available_vehicles" in data
    assert "rented_vehicles" in data
    assert "active_bookings" in data
    assert "total_revenue" in data
    assert "fleet_utilization" in data
    assert "revenue_trend" in data
    assert "recent_bookings" in data
    assert "rented_vehicles_list" in data

    assert isinstance(data["revenue_trend"], list)
    assert isinstance(data["recent_bookings"], list)
    assert isinstance(data["rented_vehicles_list"], list)


def test_get_dashboard_alias():
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_vehicles" in data

