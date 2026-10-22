import pytest
import pytest_asyncio
from black import parse_ast
from httpx import AsyncClient, ASGITransport
from main import app

@pytest_asyncio.fixture(scope="function")
async def client_no_db():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
@pytest.mark.parametrize("payload, expected_status", [
    ({"telegram_chat_id": "123", "text": "", "channel": "telegram"}, 422),
    ({"telegram_chat_id": "123", "text": "Hello", "channel": "sms"}, 422),
])
async def test_event_validation_errors(client_no_db, payload, expected_status):
    response = await client_no_db.post("/events/", json=payload)
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_create_event_success(client, test_user_chat_id):
    payload = {
        "telegram_chat_id": test_user_chat_id,
        "text": "Успешное тестовое уведомление",
        "channel": "telegram"
    }
    response = await client.post("/events/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert isinstance(data["id"], int)