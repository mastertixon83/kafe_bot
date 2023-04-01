from loguru import logger

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from utils.db_api.sql import create_pool
from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = dp.loop.run_until_complete(create_pool())
logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="100 MB", compression="zip")

scheduler = AsyncIOScheduler()
