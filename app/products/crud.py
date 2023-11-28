from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_all_data(db: AsyncSession, model):
    """Получение 18 объектов из выбранной модели.

    Пока тестирую вывод объектов, поэтому не стал
    получать сразу все данные.
    """

    result = await db.execute(select(model).limit(18))
    return result.scalars().all()


async def get_data_by_id(db: AsyncSession, model, id):
    """Получение объекта из выбранной модели по ID."""

    result = await db.execute(select(model).filter(model.id == id))
    return result.scalars().one_or_none()
