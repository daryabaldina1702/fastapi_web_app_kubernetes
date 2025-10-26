# import pytest
# from fastapi.testclient import TestClient
# from unittest.mock import patch, MagicMock
# import sys, os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from web_app.main import app, redis_client, qdrant, Item
# from web_app.wrapper import QdrantClientWrapper

# client = TestClient(app)


# def test_health_ok():
#     with patch.object(redis_client, "ping", return_value=True), \
#          patch.object(qdrant, "get_collections", return_value=[{"name": "items"}]):
#         response = client.get("/health")
#         assert response.status_code == 200
#         json_data = response.json()
#         assert json_data["status"] == "ok"
#         assert json_data["redis"] is True
#         assert json_data["qdrant"] is True


# def test_health_fail():
#     with patch.object(redis_client, "ping", side_effect=Exception("Redis down")), \
#          patch.object(qdrant, "get_collections", side_effect=Exception("Qdrant down")):
#         response = client.get("/health")
#         assert response.status_code == 500
#         json_data = response.json()
#         assert json_data["detail"]["redis"] is False
#         assert json_data["detail"]["qdrant"] is False


# def test_create_item():
#     test_item = {"id": "1", "text": "Hello", "vector": [0.1, 0.2]}

#     with patch.object(redis_client, "set") as mock_redis_set, \
#          patch.object(qdrant, "upsert_point") as mock_qdrant_upsert:
#         response = client.post("/items", json=test_item)
#         assert response.status_code == 200
#         assert response.json() == {"id": "1"}
#         mock_redis_set.assert_called_once_with("1", "Hello")
#         mock_qdrant_upsert.assert_called_once()


# def test_search():
#     dummy_result = {"result": ["item1", "item2"]}
#     with patch.object(qdrant, "search_by_vector", return_value=dummy_result) as mock_search:
#         response = client.get("/search?q=test")
#         assert response.status_code == 200
#         assert response.json() == dummy_result
#         mock_search.assert_called_once_with([0.1, 0.2])
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_app.main import app, redis_client, qdrant, Item

client = TestClient(app)


def test_health_ok():
    """Тест health, что доступны"""
    with patch("web_app.main.redis.Redis") as mock_redis, \
         patch("web_app.main.QdrantClientWrapper") as mock_qdrant_cls:
        # Настройка моков
        mock_redis.return_value.ping.return_value = True
        mock_qdrant = MagicMock()
        mock_qdrant.get_collections.return_value = [{"name": "items"}]
        mock_qdrant_cls.return_value = mock_qdrant

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["redis"] is True
        assert data["qdrant"] is True


def test_health_fail():
    """Тест health, что недоступны"""
    with patch("web_app.main.redis.Redis") as mock_redis, \
         patch("web_app.main.QdrantClientWrapper") as mock_qdrant_cls:
        mock_redis.return_value.ping.side_effect = Exception("Redis down")
        mock_qdrant_cls.return_value.get_collections.side_effect = Exception("Qdrant down")

        response = client.get("/health")
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["redis"] is False
        assert data["detail"]["qdrant"] is False


def test_create_item():
    test_item = {"id": "1", "text": "Hello", "vector": [0.1, 0.2]}

    mock_redis = MagicMock()
    mock_qdrant = MagicMock()

    with patch("web_app.main.redis_client", mock_redis), \
         patch("web_app.main.qdrant", mock_qdrant):
        response = client.post("/items", json=test_item)
        assert response.status_code == 200
        assert response.json() == {"id": "1"}

        mock_redis.set.assert_called_once_with("1", "Hello")
        mock_qdrant.upsert_point.assert_called_once_with("1", [0.1, 0.2], payload={"text": "Hello"})


def test_search():
    dummy_result = {"result": ["item1", "item2"]}

    with patch("web_app.main.qdrant", new=MagicMock()) as mock_qdrant:
        mock_qdrant.search_by_vector.return_value = dummy_result

        response = client.get("/search?q=test")
        assert response.status_code == 200
        assert response.json() == dummy_result
        mock_qdrant.search_by_vector.assert_called_once_with([0.1, 0.2])