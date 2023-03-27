# TODO: Подключение к БД
import asyncio
import asyncpg
from loader import logger

from data.config import host, PG_PASS, PG_USER, DB_NAME

async def create_db():
    with (open("utils/db_api/create_db.sql", "r")) as file:
        create_db_command = file.read()

    logger.info("Connecting to database...")
    conn: asyncpg.Connection = await asyncpg.connect(user=PG_USER,
                                                     password=PG_PASS,
                                                     database=DB_NAME,
                                                     host=host)
    try:
        await conn.execute(create_db_command)
    except asyncpg.exceptions.DuplicateTableError:
        pass
    await conn.close()
    logger.info("Table users created")


async def create_pool():
    return await asyncpg.create_pool(user=PG_USER,
                                     password=PG_PASS,
                                     database=DB_NAME,
                                     host=host)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())
