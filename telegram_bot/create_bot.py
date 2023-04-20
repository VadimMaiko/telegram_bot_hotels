from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from settings import SiteSettings


site = SiteSettings()
storage = MemoryStorage()

bot = Bot(token=site.token_bot)
dp = Dispatcher(bot, storage=storage)


