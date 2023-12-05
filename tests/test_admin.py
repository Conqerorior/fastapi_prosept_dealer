from tests.conftest import async_client


async def test_admin(async_client):
    response = await async_client.get("/")

    assert response.status_code == 200
