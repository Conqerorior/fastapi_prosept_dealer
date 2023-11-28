from fastapi import APIRouter

admin_router = APIRouter()


@admin_router.get(path='/admin')
async def get_admin():
    pass
