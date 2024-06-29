import calendar
import datetime

from telebot import types

import config
import functions
from core.models import Budget

# inline клавиатура
def start_keyboard():

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Пройти опрос', callback_data = f'questionnaire'))

    return keyboard

def confirm_first_name_keyboard(first_name):
    """Generates keyboard with 'confirm name' and self input options."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data = f'confirm_name_{first_name}'))
    keyboard.add(types.InlineKeyboardButton('🖋 Ввести вручную', callback_data = f'enter_name'))
    keyboard.add(types.InlineKeyboardButton('❌ Отменить', callback_data = f'cancel'))
    return keyboard

def request_phone_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,)
    keyboard.add(types.KeyboardButton(text = 'Предоставить номер', request_contact=True,))

    return keyboard

def budget_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for budget in Budget.objects.all():
        keyboard.add(types.InlineKeyboardButton(budget.amount, callback_data = f'budget_{budget.id}'))
    return keyboard
      
def current_month_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=7)

    current_date = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%d %B %Y")
    keyboard.add(types.InlineKeyboardButton(current_date, callback_data = f'today'))

    week_day_buttons = []
    for week_day in ('Пн.', 'Вт.', 'Ср.', 'Чт.', 'Пт.', 'Сб.', 'Вс.',):
        week_day_buttons.append(types.InlineKeyboardButton(week_day, callback_data = f'nothing'))

    keyboard.add(*week_day_buttons)

    curr_year = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).year
    curr_month = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).month
    curr_day = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).day
    curr_hour = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).hour

    date_buttons = []
    for num, i in enumerate(calendar.Calendar().itermonthdates(year=curr_year, month=curr_month)):
        if i.month != curr_month:
            date_buttons.append(types.InlineKeyboardButton('...', callback_data = f'nothing'))
        else:
            date_day = i.day
            week_day = i.weekday()
            if date_day > curr_day + 1:
                if functions.check_slots(i):
                    date_buttons.append(types.InlineKeyboardButton(i.strftime("%d"), callback_data = f'date_{curr_year}_{curr_month}_{date_day}'))
                else:
                    date_buttons.append(types.InlineKeyboardButton('❌', callback_data = f'not-available'))
            else:
                date_buttons.append(types.InlineKeyboardButton('❌', callback_data = f'not-available'))

        if (num + 1) % 7 == 0:
            keyboard.add(*date_buttons)
            date_buttons = []
    
    next_month = curr_month + 1
    next_year = curr_year
    if next_month > 12:
        next_month -= 12
        next_year += 1
    
    next_month_text = datetime.date(year=next_year, month=next_month, day=1).strftime("%B")

    keyboard.add(types.InlineKeyboardButton(f'{next_month_text} »', callback_data = f'next_{next_year}_{next_month}'))

    return keyboard


def next_month_keyboard(year, month):
    keyboard = types.InlineKeyboardMarkup(row_width=7)

    current_date = datetime.date(year=year, month=month, day=1).strftime("%B")
    keyboard.add(types.InlineKeyboardButton(current_date, callback_data = f'today'))

    week_day_buttons = []
    for week_day in ('Пн.', 'Вт.', 'Ср.', 'Чт.', 'Пт.', 'Сб.', 'Вс.',):
        week_day_buttons.append(types.InlineKeyboardButton(week_day, callback_data = f'nothing'))

    keyboard.add(*week_day_buttons)

    curr_hour = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).hour
    curr_day = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).day
    last_month_day = (datetime.date(year=year, month=month, day=1) - datetime.timedelta(days=1)).day

    date_buttons = []
    for num, i in enumerate(calendar.Calendar().itermonthdates(year=year, month=month)):
        if i.month != month:
            date_buttons.append(types.InlineKeyboardButton('...', callback_data = f'nothing'))
        else:
            date_day = i.day
            week_day = i.weekday()

            if date_day == 1 and curr_day == last_month_day:
                date_buttons.append(types.InlineKeyboardButton('❌', callback_data = f'not-available'))
            else:
                if functions.check_slots(i):
                    date_buttons.append(types.InlineKeyboardButton(i.strftime("%d"), callback_data = f'date_{year}_{month}_{date_day}'))
                else:
                    date_buttons.append(types.InlineKeyboardButton('❌', callback_data = f'not-available'))

                
        if (num + 1) % 7 == 0:
            keyboard.add(*date_buttons)
            date_buttons = []
    
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
    
    prev_month_text = datetime.date(year=prev_year, month=prev_month, day=1).strftime("%B")

    keyboard.add(types.InlineKeyboardButton(f'« {prev_month_text}', callback_data = f'prev'))

    return keyboard


def slots_keyboard(slot_date):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(types.InlineKeyboardButton(slot_date.strftime("%d %B %Y"), callback_data = f'today'))

    available_slots = functions.check_slots(slot_date)
    slot_buttons = []
    for num, slot in enumerate(available_slots):
        year = slot.year
        month = slot.month
        day = slot.day
        hour = slot.hour
        minute = slot.minute
        slot_buttons.append(types.InlineKeyboardButton(slot.strftime("%H:%M"), callback_data = f'slot_{year}_{month}_{day}_{hour}_{minute}'))
   
        if (num + 1) % 3 == 0 or len(available_slots) == num + 1:
            keyboard.add(*slot_buttons)
            slot_buttons = []

    keyboard.add(types.InlineKeyboardButton('Назад', callback_data = f'back'))

    return keyboard


def confirm_slot_keyboard(year, month, day, hour, minute):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Подтвердить', callback_data = f'c_{year}_{month}_{day}_{hour}_{minute}'), types.InlineKeyboardButton('Назад', callback_data = f'back'))

    return keyboard