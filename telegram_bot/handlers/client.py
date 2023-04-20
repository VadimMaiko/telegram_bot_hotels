import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InputMediaPhoto
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from data_base import sqlite3_db as db
from site_api import tests_api
from telegram_bot import bot
from telegram_bot import kb_command, kb_city_func, kb_sort, kb_eys_no


class FSMUser(StatesGroup):
    city_name = State()
    call_back = State()
    date_in_callback = State()
    date_out_callback = State()
    price_min = State()
    price_max = State()
    sort_by = State()
    hotel_min_info = State()
    user_info = State()


"""
    Телеграм бот написанный через библиотеку aiogram.
    Бот работает поэтапно собирает информацию для дальнейшего запроса к API.
"""


async def cm_start(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        f'Приветствую Вас {message.from_user.first_name} я бот помощник\n '
        'Я помогу вам с поиском отеля!',
        reply_markup=kb_command
    )


async def command_stop(message: types.Message, state: FSMContext):
    cur_state = await state.get_state()
    if cur_state is None:
        return
    await state.finish()
    await message.reply('Бот остановлен! \n'
                        'Чтобы включить меня нажмите -> /start')


async def command_help(message: types.Message, state: FSMContext):
    cur_state = await state.get_state()
    if cur_state is None:
        return
    await state.finish()
    await message.reply('Показывает и объясняет функционал кнопок - /help ! \n'
                        'Запустить бота с самого начала - /start \n'
                        'Остановить работу бота - /stop  \n'
                        'Покажет Ваши запросы, не больше 10 - /history  \n')


async def comm_start(message: types.Message):
    await FSMUser.city_name.set()
    await message.answer('Укажите город или страну в котором будим искать отель')


async def city_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['city_name'] = message.text
            payload = {"q": data['city_name'], "locale": "ru_RU", "langid": "", "siteid": "300000001"}
            city_choice = tests_api.api_request('locations/v3/search', payload, 'GET')
            if len(city_choice) < 1:
                await FSMUser.city_name.set()
                await message.reply('По вашему запросу нет результатов! \n'
                                    'Укажите город или страну!')
            else:
                kb_city_inline = kb_city_func(city_choice)
                data['city_name'] = message.text
                await FSMUser.next()
                await message.answer("Вот что удалось найти по вашему запросу", reply_markup=kb_city_inline)
    except TypeError:
        await message.answer("Ошибка подключения, бот не может связаться с сервером! \n "
                             "Обратитесь к разработчику по qwery@mail.ru ")


async def call_back(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['city_id'] = callback.data
        if data['city_id'] == 'да':
            await FSMUser.city_name.set()
            await callback.message.answer('Укажите город или страну!')
        else:
            await FSMUser.next()
            await callback.message.answer('Выберите дату заселения:',
                                          reply_markup=await SimpleCalendar().start_calendar())


async def date_in_callback(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        selected, date = await SimpleCalendar().process_selection(callback, callback_data)
        if selected:
            data['date_in'] = date
            await callback.message.answer(
                f'Вы указали дату заселения: {date.strftime("%d/%m/%Y")}')
            await FSMUser.next()
            await callback.message.answer("Выберите дату выезда:", reply_markup=await SimpleCalendar().start_calendar())


async def date_out_callback(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        selected, date = await SimpleCalendar().process_selection(callback, callback_data)
        if selected:
            data['date_out'] = date
            await callback.message.answer(
                f'Вы указали дату выезда: {date.strftime("%d/%m/%Y")}')
            if data['date_out'] < data['date_in']:
                await FSMUser.date_in_callback.set()
                await callback.message.answer('Неверно указали даты! \n'
                                              'Дата выезда не может быть раньше даты заезда! \n'
                                              'Укажите корректно даты',
                                              reply_markup=await SimpleCalendar().start_calendar())
            else:
                await FSMUser.next()
                await callback.message.answer('Укажите желаемую минимальную сумму затрат в долларах за одни сутки. ')


async def price_min(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['price_min'] = message.text
            if data['price_min'].startswith('0'):
                await FSMUser.price_min.set()
                await message.reply('Неверный ввод! \n Укажите число без 0 в начале')
            elif data['price_min'].isalpha() or int(data['price_min']) <= 0:
                await FSMUser.price_min.set()
                await message.answer('Неверный ввод! \n Введите целое положительное число')
            else:
                await FSMUser.next()
                await message.answer('Укажите максимально приемлемую сумму затрат в долларах за одни сутки.')
    except ValueError:
        await FSMUser.price_min.set()
        await message.reply('По вашим параметрам невозможно выполнить поиск, укажите число без лишних символов ')


async def price_max(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['price_max'] = message.text
            if data['price_max'].startswith('0'):
                await FSMUser.price_max.set()
                await message.reply('Неверный ввод! \n Укажите число без 0 в начале')
            elif data['price_max'].isalpha() or int(data['price_max']) <= 0:
                await FSMUser.price_max.set()
                await message.answer('Неверный ввод! Введите целое положительное число')
            else:
                await FSMUser.next()
                await message.answer('Как отсортировать отели', reply_markup=kb_sort)
    except ValueError:
        await FSMUser.price_max.set()
        await message.reply('По вашим параметрам невозможно выполнить поиск, укажите число без лишних символов ')


async def sort_by(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['sort'] = callback.data
        await FSMUser.next()
        await callback.message.answer('Сколько показать отелей? максимум 10')


async def hotel_min_info(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['count'] = message.text
            if data['count'].startswith('0'):
                await FSMUser.hotel_min_info.set()
                await message.reply('Неверный ввод! \n Укажите число без 0 в начале')
            elif data['count'].isdigit():
                if 0 < int(data['count']) <= 10:
                    payload = {
                        "currency": "USD",
                        "eapid": 1,
                        "locale": "ru_RU",
                        "siteId": 300000001,
                        "destination": {"regionId": data['city_id']},
                        "checkInDate": {
                            "day": int(data['date_in'].day),
                            "month": int(data['date_in'].month),
                            "year": int(data['date_in'].year)
                        },
                        "checkOutDate": {
                            "day": int(data['date_out'].day),
                            "month": int(data['date_out'].month),
                            "year": int(data['date_out'].year)
                        },
                        "rooms": [
                            {
                                "adults": 2,
                                "children": [{"age": 5}, {"age": 7}]
                            }
                        ],
                        "resultsStartingIndex": 0,
                        "resultsSize": 200,
                        "sort": data['sort'],
                        "filters": {"price": {
                            "max": int(data['price_max']),
                            "min": int(data['price_min']),
                        }}
                    }
                    hotel_search_api = tests_api.api_request('properties/v2/list', payload, "POST", data['count'])
                    for i in range(int(data['count'])):
                        await message.answer(hotel_search_api[i][0])
                        group_elements = []
                        for element in hotel_search_api[i][1][0:5]:
                            group_elements.append(InputMediaPhoto(element))
                        await message.answer_media_group(group_elements)
                    await FSMUser.next()
                    await message.answer('Еще нужна помощь?', reply_markup=kb_eys_no)
                else:
                    await FSMUser.hotel_min_info.set()
                    await message.answer('Неверный ввод! Введите число от 1 до 10')
            else:
                await FSMUser.hotel_min_info.set()
                await message.answer('Неверный ввод! Введите целое положительное число')
    except IndexError:
        await message.answer('По вашему запросу нет информации /start')
        await state.finish()
    except TypeError:
        await message.answer('Ошибка при обработке запроса, измените вводимые данные \n /start')
        await state.finish()


async def user_info(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = callback.message.from_id
        eys_no = callback.data
        if eys_no == 'да':
            await callback.message.answer('Выберите действие', reply_markup=kb_command)
        elif eys_no == 'нет':
            await callback.message.answer('Бот закончил работу \n'
                                          'Что бы запустить бота нажмите /start')
    await db.sql_add(state)
    await state.finish()


async def commands_info(message: types.Message):
    await message.answer('Ваши 10 последних запросов')
    await db.sql_read(message)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands=['start'])
    dp.register_message_handler(comm_start, commands=['Начать_поиск'], state=None)
    dp.register_message_handler(command_stop, state='*', commands=['stop', 'Отмена_всех_действий'])
    dp.register_message_handler(command_stop, Text(equals='stop', ignore_case=True), state='*')
    dp.register_message_handler(command_help, state='*', commands=['help', 'Помощь'])
    dp.register_message_handler(command_help, Text(equals='help', ignore_case=True), state='*')
    dp.register_message_handler(city_name, state=FSMUser.city_name)
    dp.register_callback_query_handler(call_back, Text(startswith=''), state=FSMUser.call_back)
    dp.register_callback_query_handler(date_in_callback, simple_cal_callback.filter(), state=FSMUser.date_in_callback)
    dp.register_callback_query_handler(date_out_callback, simple_cal_callback.filter(), state=FSMUser.date_out_callback)
    dp.register_message_handler(price_min, state=FSMUser.price_min)
    dp.register_message_handler(price_max, state=FSMUser.price_max)
    dp.register_callback_query_handler(sort_by, state=FSMUser.sort_by)
    dp.register_message_handler(hotel_min_info, state=FSMUser.hotel_min_info)
    dp.register_callback_query_handler(user_info, state=FSMUser.user_info)
    dp.register_message_handler(commands_info, commands=['history', 'История_запросов'])
