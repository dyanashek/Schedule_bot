import datetime

import telebot

import keyboards
import config
import settings

from django.db.models import Q
from core.models import TelegramText
from schedule.models.events import Event, Calendar


bot = telebot.TeleBot(config.TELEGRAM_TOKEN)


def name_response(first_name):
    """Generates a response, depends on first name."""

    if first_name is None:
        keyboard = None
        reply_text = TelegramText.objects.get(slug='name_question').text
    else:
        keyboard = keyboards.confirm_first_name_keyboard(first_name)
        reply_text = f'Ваше имя - *{first_name}*?'

    return reply_text, keyboard


def check_slots(slot_date):
    available_slots = []

    start_today = datetime.datetime.combine(slot_date, datetime.time.min)
    end_today = datetime.datetime.combine(slot_date, datetime.time.max)
    work_slots = Event.objects.filter(Q(calendar__slug='work-time') & Q(start__gte=start_today) & Q(end__lte=end_today)).order_by('start').all()
    if work_slots:
        consultation_slots = Event.objects.filter(Q(calendar__slug='consultations') & Q(start__gte=start_today) & Q(end__lte=end_today)).all()

        work_finish_time = work_slots.last().end
        start_time = work_slots.first().start
        end_time = start_time + datetime.timedelta(minutes=settings.DURATION)

        while end_time <= work_finish_time:
            if (work_slots.filter(Q(start__lte=start_time) & Q(end__gte=end_time)).exists() and
            not consultation_slots.filter(Q(Q(start__lt=end_time) & Q(end__gte=end_time)) | Q(Q(start__lte=start_time) & Q(end__gt=start_time))).exists()):
                available_slots.append(start_time)

            start_time += datetime.timedelta(minutes=settings.INTERVAL)
            end_time += datetime.timedelta(minutes=settings.INTERVAL)

    return available_slots


def reserve_slot(user, start_time):
    end_time = start_time + datetime.timedelta(minutes=settings.DURATION)
    if (Event.objects.filter(Q(calendar__slug='work-time') & Q(start__lte=start_time) & Q(end__gte=end_time)).exists() and
    not Event.objects.filter(Q(calendar__slug='consultations') & ((Q(start__lt=end_time) & Q(end__gte=end_time)) | (Q(start__lte=start_time) & Q(end__gt=start_time)))).exists()):
        description = ''
        if user.username:
            description += f'Ник tg: @{user.username}\n'
        description += f'Имя: {user.name}\n'
        description += f'Номер телефона: {user.phone}\n'
        description += f'Рост: {user.height} см.\n'
        description += f'Вес: {user.weight} кг.\n'
        description += f'Бюджет: {user.budget}'

        calendar = Calendar.objects.get(slug='consultations')
        event = Event(
            title = user.name,
            description = description,
            start = start_time,
            end = end_time,
            calendar = calendar,
        )
        event.save()
        user.consultation = event
        user.save()
        return True

    return False