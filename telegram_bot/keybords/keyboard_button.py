from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

"""Создаем обычные кнопки для меню №1"""
b1 = types.KeyboardButton(text='/Начать_поиск')
b2 = types.KeyboardButton(text='/История_запросов')
b3 = types.KeyboardButton(text='/Отмена_всех_действий')
b4 = types.KeyboardButton(text='/Помощь')


"""Создаем обычные кнопки для меню №2"""
kb_command = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_command.add(b1).add(b2).add(b3).add(b4)

""""Создаем всплывающие кнопки - Inline Keyboard Button №1"""

kb_sort = InlineKeyboardMarkup(row_width=1)
kb_sort.add(InlineKeyboardButton(text='По возрастанию цены', callback_data='PRICE_LOW_TO_HIGH'))
kb_sort.add(InlineKeyboardButton(text='Лучшее предложение', callback_data='RECOMMENDED'))
kb_sort.add(InlineKeyboardButton(text='Расстояние от центра', callback_data='DISTANCE'))

""""Создаем всплывающие кнопки - Inline Keyboard Button №2"""
kb_eys_no = InlineKeyboardMarkup(row_width=1)
kb_eys_no.add(InlineKeyboardButton(text='Да', callback_data='да'))
kb_eys_no.add(InlineKeyboardButton(text='Нет', callback_data='нет'))

"""Функция генерирует InlineKeyboardButton с названиями городов"""


def kb_city_func(city_list: dict) -> InlineKeyboardMarkup:
    kb_city = InlineKeyboardMarkup(row_width=1)
    for key, value in city_list.items():
        kb_city.add(InlineKeyboardButton(text=key, callback_data=value))
    kb_city.add(InlineKeyboardButton(text='*--* ИЗМЕНИТЬ ПОИСК *--*', callback_data='да'))
    return kb_city
