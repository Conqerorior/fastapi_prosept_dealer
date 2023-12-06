from httpx import AsyncClient

from tests.conftest import async_client


async def test_admin(async_client: AsyncClient):

    response = await async_client.get('/admin')

    assert response.status_code == 307, 'Путь /admin недоступен'


async def test_admin_post(async_client: AsyncClient):

    response = await async_client.post('/admin')

    assert response.status_code == 307
