import pytest


@pytest.mark.asyncio
async def test_check_endpoint(async_client):
    response = await async_client.get("/check")
    assert response.status_code == 200
    assert response.json()['db_server_alive'] is True
