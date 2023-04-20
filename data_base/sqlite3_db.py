import sqlite3 as sq

from telegram_bot import bot


async def sql_start():
    """
    Функция создает базу данных
            Функция добавляющая все полученные данные в базу данных
    """
    with sq.connect('data_base_user.db') as connection:
        global cur, conn
        conn = connection
        cur = connection.cursor()

        if conn:
            print('База данных подключилась!')
        conn.execute('CREATE TABLE IF NOT EXISTS table_user(city_name, city_id, date_in, date_out,'
                     'price_min, price_max, hotel_foto, sort, user_id)')


async def sql_add(state):
    async with state.proxy() as data:
        conn.execute('INSERT INTO table_user VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(data.values()))
        conn.commit()


async def sql_read(message):
    """
        Функция возвращающая ответ пользователю на запрос от пользователя /История_запросов
    """
    for column in cur.execute('SELECT * FROM table_user').fetchmany(10):
        await bot.send_message(message.from_user.id, f'Город: {column[0]}'
                                                     f'\nДата вылета: {column[2]}'
                                                     f'\nОбратный билет: {column[3]}'
                                                     f'\nКолл-во пассажиров:{column[4]}'
                                                     f'\nМинимальная цена: {column[5]}'
                                                     f'\nМаксимальная цена: {column[6]}')
