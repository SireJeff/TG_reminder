"""
modules/random_checkins.py

This module implements the Random Check-Ins functionality.
It sends random check-in messages to users based on their 'random_checkin_max' setting.
A check-in message is sent with an inline keyboard offering quick actions:
    - Add Task
    - Add Goal
    - Add Reminder
    - Add Countdown
    - Ignore

Integration:
  - A scheduler (e.g., APScheduler) should call schedule_daily_checkins() to schedule check-ins.
  - The check-in message is sent even if the user has no pending items.
"""

import random
from telebot import types

# A simple dictionary holding check-in labels for English (en) and Persian (fa).
CHECKIN_LABELS = {
    'en': {
        'prompt': "Hey! Anything new to add or update?",
        'add_task': "Add Task",
        'add_goal': "Add Goal",
        'add_reminder': "Add Reminder",
        'add_countdown': "Add Countdown",
        'ignore': "Ignore",
        'action_task': "Let's add a task!",
        'action_goal': "Let's add a goal!",
        'action_reminder': "Let's add a reminder!",
        'action_countdown': "Let's add a countdown!",
        'action_ignored': "Okay, no action taken."
    },
    'fa': {
        'prompt': "سلام! چیزی برای اضافه کردن یا به‌روزرسانی دارید؟",
        'add_task': "افزودن وظیفه",
        'add_goal': "افزودن هدف",
        'add_reminder': "افزودن یادآوری",
        'add_countdown': "افزودن شمارش معکوس",
        'ignore': "نادیده بگیر",
        'action_task': "بیا یک وظیفه اضافه کنیم!",
        'action_goal': "بیا یک هدف اضافه کنیم!",
        'action_reminder': "بیا یک یادآوری اضافه کنیم!",
        'action_countdown': "بیا یک شمارش معکوس اضافه کنیم!",
        'action_ignored': "باشه، کاری انجام نمی‌شود."
    }
}

def send_random_checkin(bot, chat_id, user_id, user_lang='en'):
    """
    Sends a random check-in message to the user with inline options, in the user's language.
    
    Parameters:
        bot (TeleBot): The TeleBot instance.
        chat_id (int): The Telegram chat ID.
        user_id (int): The Telegram user ID.
        user_lang (str): The user's language code ('en' or 'fa'), default 'en'.
    """
    labels = CHECKIN_LABELS.get(user_lang, CHECKIN_LABELS['en'])

    markup = types.InlineKeyboardMarkup()
    btn_add_task = types.InlineKeyboardButton(text=labels['add_task'], callback_data="random_add_task")
    btn_add_goal = types.InlineKeyboardButton(text=labels['add_goal'], callback_data="random_add_goal")
    btn_add_reminder = types.InlineKeyboardButton(text=labels['add_reminder'], callback_data="random_add_reminder")
    btn_add_countdown = types.InlineKeyboardButton(text=labels['add_countdown'], callback_data="random_add_countdown")
    btn_ignore = types.InlineKeyboardButton(text=labels['ignore'], callback_data="random_ignore")
    
    # Arrange buttons in rows.
    markup.row(btn_add_task, btn_add_goal)
    markup.row(btn_add_reminder, btn_add_countdown)
    markup.add(btn_ignore)
    
    message_text = labels['prompt']
    bot.send_message(chat_id, message_text, reply_markup=markup)

def handle_random_checkin_callback(bot, call):
    """
    Handles callback queries for random check-in actions.
    
    Parameters:
        bot: The TeleBot instance.
        call: The callback query from the check-in message.
    """
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data

    # Retrieve user_lang from user states or DB; fallback to 'en'
    # For demonstration, we do a quick fallback:
    from bot import user_states  # Example: If 'user_states' is accessible in 'bot.py'
    user_lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    labels = CHECKIN_LABELS.get(user_lang, CHECKIN_LABELS['en'])

    if data == "random_add_task":
        from modules.tasks import start_add_task
        start_add_task(bot, chat_id, user_id)
        bot.answer_callback_query(call.id, labels['action_task'])
    elif data == "random_add_goal":
        from modules.goals import start_add_goal
        start_add_goal(bot, chat_id, user_id)
        bot.answer_callback_query(call.id, labels['action_goal'])
    elif data == "random_add_reminder":
        from modules.reminders import start_add_reminder
        start_add_reminder(bot, chat_id, user_id)
        bot.answer_callback_query(call.id, labels['action_reminder'])
    elif data == "random_add_countdown":
        from modules.countdowns import start_add_countdown
        start_add_countdown(bot, chat_id, user_id)
        bot.answer_callback_query(call.id, labels['action_countdown'])
    elif data == "random_ignore":
        bot.answer_callback_query(call.id, labels['action_ignored'])
    else:
        bot.answer_callback_query(call.id, "Unknown action.")

def schedule_daily_checkins(bot, user_id, chat_id, random_checkin_max):
    """
    Schedules random check-ins for a user throughout the day.
    
    In a production environment, you would schedule these calls at random times.
    Here, we simply send the check-in messages immediately for demonstration.
    
    Parameters:
        bot: The TeleBot instance.
        user_id: The Telegram user ID.
        chat_id: The Telegram chat ID.
        random_checkin_max: The maximum number of check-ins per day.
    """
    # For demonstration, we instantly send random_checkin_max check-ins.
    # In real code, you'd use a scheduling library to send them at random times.
    from bot import user_states
    user_lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    
    for _ in range(random_checkin_max):
        send_random_checkin(bot, chat_id, user_id, user_lang)
