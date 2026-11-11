from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/")

    assert response.status_code == 200


def test_invalid_dataset_evaluation():
    response = client.post(
        "/evaluation-runs",
        json={
            "dataset_id": 999999,
            "agent_version_id": 5,
            "max_test_cases": 1
        }
    )

    assert response.status_code == 404


def test_invalid_agent_version():
    response = client.post(
        "/evaluation-runs",
        json={
            "dataset_id": 1,
            "agent_version_id": 999999,
            "max_test_cases": 1
        }
    )

    assert response.status_code == 404


def test_invalid_comparison_runs():
    response = client.get(
        "/comparisons/runs/999998/999999"
    )

    assert response.status_code == 404