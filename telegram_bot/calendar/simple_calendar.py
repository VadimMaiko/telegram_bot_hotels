import calendar
from datetime import datetime, timedelta

from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

calendar_callback = CallbackData('simple_calendar', 'act', 'year', 'month', 'day')


class SimpleCalendar:

    async def start_calendar(
            self,
            year: int = datetime.now().year,
            month: int = datetime.now().month
    ) -> InlineKeyboardMarkup:
        """
        Создает встроенную клавиатуру с предоставленными годом и месяцем
        :param int year: Год для использования в календаре, если его нет, используется текущий год.
        :param int month: Месяц для использования в календаре, если его нет, используется текущий месяц.
        ::return: Возвращает объект разметки клавиатуры в строке с календарем.
        """
        inline_kb = InlineKeyboardMarkup(row_width=7)
        ignore_callback = calendar_callback.new("IGNORE", year, month, 0)
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            "<<",
            callback_data=calendar_callback.new("PREV-YEAR", year, month, 1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            f'{calendar.month_name[month]} {str(year)}',
            callback_data=ignore_callback
        ))
        inline_kb.insert(InlineKeyboardButton(
            ">>",
            callback_data=calendar_callback.new("NEXT-YEAR", year, month, 1)
        ))
        inline_kb.row()
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            inline_kb.insert(InlineKeyboardButton(day, callback_data=ignore_callback))

        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            inline_kb.row()
            for day in week:
                if (day == 0):
                    inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
                    continue
                inline_kb.insert(InlineKeyboardButton(
                    str(day), callback_data=calendar_callback.new("DAY", year, month, day)
                ))

        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            "<", callback_data=calendar_callback.new("PREV-MONTH", year, month, day)
        ))
        inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
        inline_kb.insert(InlineKeyboardButton(
            ">", callback_data=calendar_callback.new("NEXT-MONTH", year, month, day)
        ))

        return inline_kb

    async def process_selection(self, query: CallbackQuery, data: CallbackData) -> tuple:
        """
        Обработайте callback_query. Этот метод генерирует новый календарь, если переслать или
        нажата кнопка "назад". Этот метод должен вызываться внутри обработчика запроса обратного вызова.
        ::param query: callback_query, как предусмотрено обработчиком запроса обратного вызова
        :param data: callback_data, словарь, заданный calendar_callback
        :return: Возвращает кортеж (логическое значение,datetime), указывающий, выбрана ли дата
                    и верните дату, если это так.
        """
        return_data = (False, None)
        temp_date = datetime(int(data['year']), int(data['month']), 1)
        if data['act'] == "IGNORE":
            await query.answer(cache_time=60)
        if data['act'] == "DAY":
            await query.message.delete_reply_markup()
            return_data = True, datetime(int(data['year']), int(data['month']), int(data['day']))
        if data['act'] == "PREV-YEAR":
            prev_date = datetime(int(data['year']) - 1, int(data['month']), 1)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        if data['act'] == "NEXT-YEAR":
            next_date = datetime(int(data['year']) + 1, int(data['month']), 1)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        if data['act'] == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        if data['act'] == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        return return_data
