from aiogram.utils import executor

from data_base import sqlite3_db
from telegram_bot import dp
from telegram_bot import client


async def on_startup(_):
    print('Бот вышел в онлайн')
    await sqlite3_db.sql_start()


client.register_handlers_client(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    on_startup()