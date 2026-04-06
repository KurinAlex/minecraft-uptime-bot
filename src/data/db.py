from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import Config
from data.models import Base


class Database:
    engine: AsyncEngine = create_async_engine(url=Config.database_url())
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine, class_=AsyncSession
    )

    @classmethod
    async def create_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
