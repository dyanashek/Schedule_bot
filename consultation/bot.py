import os
import datetime

import django
import telebot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'consultation.settings')
django.setup()

from core.models import TGUser, TelegramText, Budget
from schedule.models.events import Event

import config
import keyboards
import functions
import utils


bot = telebot.TeleBot(config.TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    '''Handles start command.'''

    user_id = str(message.from_user.id)
    username = message.from_user.username
    if not username:
        username = None

    user, _ = TGUser.objects.get_or_create(user_id=user_id)
    user.username = username
    user.save()

    start_message = TelegramText.objects.get(slug='start_text').text
    
    bot.send_message(chat_id=user_id,
                         text=start_message,
                         reply_markup=keyboards.start_keyboard(),
                         parse_mode='Markdown',
                         )


@bot.message_handler(commands=['event'])
def start_message(message):
    functions.check_slots(datetime.date.today())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Handles queries from inline keyboards."""

    # getting message's and user's ids
    message_id = call.message.id
    chat_id = call.message.chat.id
    user_id = str(call.from_user.id)
    username = call.from_user.username

    user = TGUser.objects.get(user_id=user_id)
    if username:
        user.username = username
        user.save()

    call_data = call.data.split('_')
    query = call_data[0]

    if query == 'questionnaire':
        if not user.questionnaire_completed:
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass

            if user.curr_input is None or user.curr_input == 'name':
                user.curr_input = 'name'
                user.save()

                first_name = call.from_user.first_name
                reply_text, keyboard = functions.name_response(first_name)

                bot.send_message(chat_id=chat_id,
                                text=reply_text,
                                reply_markup=keyboard,
                                parse_mode='Markdown',
                                )

            elif user.curr_input == 'phone':
                phone_question = TelegramText.objects.get(slug='phone_question')
                bot.send_message(chat_id=chat_id,
                        text=phone_question.text,
                        parse_mode='Markdown',
                        reply_markup=keyboards.request_phone_keyboard(),
                        )
            
            elif user.curr_input == 'age':
                age_question = TelegramText.objects.get(slug='age_question')
                bot.send_message(chat_id=chat_id,
                        text=age_question.text,
                        parse_mode='Markdown',
                        )

            elif user.curr_input == 'height':
                height_question = TelegramText.objects.get(slug='height_question')
                bot.send_message(chat_id=chat_id,
                        text=height_question.text,
                        parse_mode='Markdown',
                        )
            
            elif user.curr_input == 'weight':
                weight_question = TelegramText.objects.get(slug='weight_question')
                bot.send_message(chat_id=chat_id,
                        text=weight_question.text,
                        parse_mode='Markdown',
                        )

            elif user.curr_input == 'budget':
                budget_question = TelegramText.objects.get(slug='budget_question')
                bot.send_message(chat_id=chat_id,
                        text=budget_question.text,
                        reply_markup=keyboards.budget_keyboard(),
                        parse_mode='Markdown',
                        )

        elif not user.consultation:
            reply_text = TelegramText.objects.get(slug='pick_date').text
            bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=reply_text,
                                parse_mode='Markdown',
                                )
        
            bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=keyboards.current_month_keyboard(),
                                            )

        else:
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass

            slot_time = user.consultation.start.strftime("%d.%m.%Y %H:%M")
            reserved_text = TelegramText.objects.get(slug='reserved').text
            reply_text = f'{reserved_text} *{slot_time}*'
            bot.send_message(chat_id=chat_id,
                                text=reply_text,
                                parse_mode='Markdown',
                                )

    elif query == 'enter':
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass
            
            name_question = TelegramText.objects.get(slug='name_question')

            bot.send_message(chat_id=chat_id,
                        text=name_question.text,
                        parse_mode='Markdown',
                        )

    elif query == 'cancel':
        user.curr_input = None
        user.save()
        cancel_message = TelegramText.objects.get(slug='cancel_input')
        bot.edit_message_text(message_id=message_id,
                            chat_id=chat_id,
                            text=cancel_message.text,
                            )    
    
    elif query == 'confirm':
        info_category = call_data[1]
        info = call_data[2]

        if info_category == 'name' and user.curr_input and user.curr_input == 'name':
            user.name = info
            user.curr_input = 'phone'
            user.save()

            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass
            
            phone_question = TelegramText.objects.get(slug='phone_question')
            bot.send_message(chat_id=chat_id,
                    text=phone_question.text,
                    parse_mode='Markdown',
                    reply_markup=keyboards.request_phone_keyboard(),
                    )

        else:
            outdated = TelegramText.objects.get(slug='outdated')
            bot.edit_message_text(message_id=message_id,
                                chat_id=chat_id,
                                text=outdated.text,
                                )  

    elif query == 'budget':
        budget_id = int(call_data[1])
        if user.curr_input and user.curr_input == 'budget':
            user.curr_input = None
            user.questionnaire_completed = True
            user.budget = Budget.objects.get(id=budget_id).amount
            user.save()

            reply_text = TelegramText.objects.get(slug='pick_date').text
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=reply_text,
                                  parse_mode='Markdown',
                                  )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=keyboards.current_month_keyboard(),
                                          )
        else:
            outdated = TelegramText.objects.get(slug='outdated')
            bot.edit_message_text(message_id=message_id,
                                chat_id=chat_id,
                                text=outdated.text,
                                ) 
    
    elif query == 'prev':
        bot.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=keyboards.current_month_keyboard(),
                                        )
    
    elif query == 'next':
        year = int(call_data[1])
        month = int(call_data[2])
         
        bot.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=keyboards.next_month_keyboard(year, month),
                                        )
    
    elif query == 'date':
        year = int(call_data[1])
        month = int(call_data[2])
        day = int(call_data[3])
        chosen_date = datetime.date(year=year, month=month, day=day)
        reply_text = TelegramText.objects.get(slug='pick_time').text
        bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=reply_text,
                                  parse_mode='Markdown',
                                  )
            
        bot.edit_message_reply_markup(chat_id=chat_id,
                                    message_id=message_id,
                                    reply_markup=keyboards.slots_keyboard(chosen_date),
                                    )
    
    elif query == 'slot':
        year = int(call_data[1])
        month = int(call_data[2])
        day = int(call_data[3])
        hour = int(call_data[4])
        minute = int(call_data[5])

        slot_time = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
        slot_time = slot_time.strftime("%d.%m.%Y %H:%M")

        confirm_text = TelegramText.objects.get(slug='confirm_slot').text
        reply_text = f'{confirm_text} *{slot_time}*?'

        bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=reply_text,
                                parse_mode='Markdown',
                                )
        
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=keyboards.confirm_slot_keyboard(year=year, month=month, day=day, hour=hour, minute=minute),
                                      )

    elif query == 'back':
        reply_text = TelegramText.objects.get(slug='pick_date').text
        bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=reply_text,
                                parse_mode='Markdown',
                                )
        
        bot.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=keyboards.current_month_keyboard(),
                                        )
    
    elif query == 'c':
        year = int(call_data[1])
        month = int(call_data[2])
        day = int(call_data[3])
        hour = int(call_data[4])
        minute = int(call_data[5])

        slot_time = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
        if functions.reserve_slot(user, slot_time):
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass
                
            slot_time = slot_time.strftime("%d.%m.%Y %H:%M")
            reserved_text = TelegramText.objects.get(slug='reserved').text
            reply_text = f'{reserved_text} *{slot_time}*'
            bot.send_message(chat_id=chat_id,
                                text=reply_text,
                                parse_mode='Markdown',
                                )

        else:
            reply_text = TelegramText.objects.get(slug='pick_date_again').text
            bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=reply_text,
                                    parse_mode='Markdown',
                                    )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=keyboards.current_month_keyboard(),
                                            )



@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    phone = message.contact.phone_number
    user_id = str(message.from_user.id)
    username = message.from_user.username
    chat_id = message.chat.id

    user = TGUser.objects.get(user_id=user_id)
    if username:
        user.username = username
        user.save()

    if user.curr_input and user.curr_input == 'phone':
        user.phone = phone
        user.curr_input = 'age'
        user.save()

        age_question = TelegramText.objects.get(slug='age_question')
        bot.send_message(chat_id=chat_id,
                        text=age_question.text,
                        reply_markup=telebot.types.ReplyKeyboardRemove(),
                        parse_mode='Markdown',
                        disable_notification=True,
                        )


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Handles message with type text."""
    user_id = str(message.from_user.id)
    username = message.from_user.username
    chat_id = message.chat.id
    input_info = message.text

    user = TGUser.objects.get(user_id=user_id)
    if username:
        user.username = username
        user.save()

    if user.curr_input and user.curr_input == 'name':
        user.name = utils.escape_markdown(input_info)
        user.curr_input = 'phone'
        user.save()

        phone_question = TelegramText.objects.get(slug='phone_question')
        bot.send_message(chat_id=chat_id,
                text=phone_question.text,
                parse_mode='Markdown',
                reply_markup=keyboards.request_phone_keyboard(),
                )

    elif user.curr_input and user.curr_input == 'phone':
        phone = utils.validate_phone(input_info)
        if phone:
            user.phone = phone
            user.curr_input = 'age'
            user.save()

            age_question = TelegramText.objects.get(slug='age_question')
            bot.send_message(chat_id=chat_id,
                            text=age_question.text,
                            reply_markup=telebot.types.ReplyKeyboardRemove(),
                            parse_mode='Markdown',
                            disable_notification=True,
                            )
        else:
            error = TelegramText.objects.get(slug='error')
            phone_question = TelegramText.objects.get(slug='phone_question')
            reply_text = error.text + '\n' + phone_question.text

            bot.send_message(chat_id=chat_id,
                text=reply_text,
                parse_mode='Markdown',
                reply_markup=keyboards.request_phone_keyboard(),
                )
    
    elif user.curr_input and user.curr_input == 'age':
        age = utils.validate_age(input_info)
        if age:
            user.age = age
            user.curr_input = 'height'
            user.save()

            height_question = TelegramText.objects.get(slug='height_question')
            bot.send_message(chat_id=chat_id,
                            text=height_question.text,
                            parse_mode='Markdown',
                            disable_notification=True,
                            )
        else:
            error = TelegramText.objects.get(slug='error')
            phone_question = TelegramText.objects.get(slug='age_question')
            reply_text = error.text + '\n' + phone_question.text

            bot.send_message(chat_id=chat_id,
                text=reply_text,
                parse_mode='Markdown',
                reply_markup=keyboards.request_phone_keyboard(),
                )

    elif user.curr_input and user.curr_input == 'height':
        height = utils.validate_height(input_info)
        if height:
            user.height = height
            user.curr_input = 'weight'
            user.save()
        
            weight_question = TelegramText.objects.get(slug='weight_question')
            bot.send_message(chat_id=chat_id,
                            text=weight_question.text,
                            parse_mode='Markdown',
                            disable_notification=True,
                            )
        else:
            error = TelegramText.objects.get(slug='error')
            height_question = TelegramText.objects.get(slug='height_question')
            reply_text = error.text + '\n' + height_question.text

            bot.send_message(chat_id=chat_id,
                            text=reply_text,
                            parse_mode='Markdown',
                            disable_notification=True,
                            )

    elif user.curr_input and user.curr_input == 'weight':
        weight = utils.validate_weight(input_info)
        if weight:
            user.weight = weight
            user.curr_input = 'budget'
            user.save()

            budget_question = TelegramText.objects.get(slug='budget_question')
            bot.send_message(chat_id=chat_id,
                            text=budget_question.text,
                            parse_mode='Markdown',
                            reply_markup=keyboards.budget_keyboard(),
                            disable_notification=True,
                            )
        else:
            error = TelegramText.objects.get(slug='error')
            weight_question = TelegramText.objects.get(slug='weight_question')
            reply_text = error.text + '\n' + weight_question.text

            bot.send_message(chat_id=chat_id,
                            text=reply_text,
                            parse_mode='Markdown',
                            disable_notification=True,
                            )

if __name__ == '__main__':
    bot.polling(timeout=80)
    # while True:
    #     try:
    #         bot.polling()
    #     except:
    #         pass