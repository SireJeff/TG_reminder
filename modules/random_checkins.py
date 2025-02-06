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

def send_random_checkin(bot, chat_id, user_id):
    """
    Sends a random check-in message to the user with inline options.
    
    Parameters:
        bot: The TeleBot instance.
        chat_id: The Telegram chat ID.
        user_id: The Telegram user ID.
    """
    markup = types.InlineKeyboardMarkup()
    btn_add_task = types.InlineKeyboardButton(text="Add Task", callback_data="random_add_task")
    btn_add_goal = types.InlineKeyboardButton(text="Add Goal", callback_data="random_add_goal")
    btn_add_reminder = types.InlineKeyboardButton(text="Add Reminder", callback_data="random_add_reminder")
    btn_add_countdown = types.InlineKeyboardButton(text="Add Countdown", callback_data="random_add_countdown")
    btn_ignore = types.InlineKeyboardButton(text="Ignore", callback_data="random_ignore")
    
    # Arrange buttons in rows.
    markup.row(btn_add_task, btn_add_goal)
    markup.row(btn_add_reminder, btn_add_countdown)
    markup.add(btn_ignore)
    
    message_text = "Hey! Anything new to add or update?"
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

    if data == "random_add_task":
        from modules.tasks import start_add_task
        start_add_task(bot, chat_id, user_id)
        bot.answer_callback_query(call.id, "Let's add a task!")
    elif data == "random_add_goal":
        from modules.goals import start_add_goal
        start_add_goal(bot, chat_id, user_id)
        bot.answer_callback_query(call.id, "Let's add a goal!")
    elif data == "random_add_reminder":
        from modules.reminders import start_add_reminder
        start_add_reminder(bot, chat_id, user_id)
        bot.answer_callback_query(call.id, "Let's add a reminder!")
    elif data == "random_add_countdown":
        from modules.countdowns import start_add_countdown
        start_add_countdown(bot, chat_id, user_id)
        bot.answer_callback_query(call.id, "Let's add a countdown!")
    elif data == "random_ignore":
        bot.answer_callback_query(call.id, "Okay, no action taken.")
    else:
        bot.answer_callback_query(call.id, "Unknown action.")

def schedule_daily_checkins(bot, user_id, chat_id, random_checkin_max):
    """
    Schedules random check-ins for a user throughout the day.
    
    This function should be called by the scheduling mechanism (e.g., APScheduler).
    For each check-in, a random time within the defined window (e.g., 8 AM to 9 PM)
    should be chosen, and a one-time job should call send_random_checkin() at that time.
    
    In this placeholder example, we immediately send the check-in messages.
    
    Parameters:
        bot: The TeleBot instance.
        user_id: The Telegram user ID.
        chat_id: The Telegram chat ID.
        random_checkin_max: The maximum number of check-ins per day.
    """
    # In a production environment, you would schedule these calls at random times.
    # Here, we simply send the check-in messages immediately for demonstration.
    for _ in range(random_checkin_max):
        send_random_checkin(bot, chat_id, user_id)
