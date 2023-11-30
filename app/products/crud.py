from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_all_data(db: AsyncSession, model):
    """Получение всех объектов из выбранной модели."""

    result = await db.execute(select(model))
    return result.scalars().all()


async def get_data_by_id(db: AsyncSession, model, id):
    """Получение объекта из выбранной модели по ID."""

    result = await db.execute(select(model).filter(model.id == id))
    return result.scalars().one_or_none()
