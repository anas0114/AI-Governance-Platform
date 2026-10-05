from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
