"""
modules/reminders.py

This module implements the Reminders functionality.
It allows users to add reminders and manage them.

Reminder Addition Flow:
1. The bot starts the conversation by asking:
   "What do you want to be reminded about?" (state: 'awaiting_title')
2. After the title is provided, the bot prompts for the trigger time:
   - Presents an inline keyboard with options:
       • "In 1 hour"
       • "In 2 hours"
       • "Tomorrow"
       • "Custom"
   (state: 'awaiting_time_option')
3. If a preset is selected, the next trigger time is computed automatically;
   if "Custom" is selected, the state changes to 'awaiting_custom_time' where the user must enter a date/time in the format "YYYY-MM-DD HH:MM".
   (The entered date is parsed using our date conversion module so that both Gregorian and Jalali formats are supported.)
4. Next, the bot asks for the repeat type:
   - Presents an inline keyboard with options:
       • "One-time"
       • "Every X hours"
       • "Every X days"
       • "Daily"
   (state: 'awaiting_repeat_choice')
5. For "Every X hours" or "Every X days", the state changes to 'awaiting_repeat_value' so the user can enter a number.
6. Finally, the reminder is saved into the database with the provided title, trigger time, and repeat settings.
7. Additional helper functions allow listing, updating, and deleting reminders.

All database operations use `get_db_connection()` from `database.py`.
"""

import sqlite3
from datetime import datetime, timedelta
from telebot import types
from database import get_db_connection
from modules.date_conversion import parse_date  # Supports both Gregorian and Jalali date inputs

# Global dictionary to track reminder conversation state per user.
# Structure: { user_id: { 'state': <state>, 'data': { ... } } }
reminders_states = {}

def start_add_reminder(bot, chat_id, user_id):
    """
    Initiates the add-reminder conversation.
    """
    reminders_states[user_id] = {
        'state': 'awaiting_title',
        'data': {}
    }
    bot.send_message(chat_id, "What do you want to be reminded about?")

def handle_reminder_callbacks(bot, call):
    """
    Handles callback queries for the reminder addition flow.
    """
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if user_id not in reminders_states:
        return  # Not in an active reminder conversation
    
    current_state = reminders_states[user_id]['state']
    data = reminders_states[user_id]['data']
    
    # Handle time preset selection when state is 'awaiting_time_option'
    if current_state == 'awaiting_time_option':
        if call.data == "rem_time_1hr":
            next_trigger_time = datetime.now() + timedelta(hours=1)
            data['next_trigger_time'] = next_trigger_time
            reminders_states[user_id]['state'] = 'awaiting_repeat_choice'
            bot.edit_message_text("Reminder time set to 1 hour from now.", chat_id, call.message.message_id)
            prompt_repeat_choice(bot, chat_id)
        elif call.data == "rem_time_2hrs":
            next_trigger_time = datetime.now() + timedelta(hours=2)
            data['next_trigger_time'] = next_trigger_time
            reminders_states[user_id]['state'] = 'awaiting_repeat_choice'
            bot.edit_message_text("Reminder time set to 2 hours from now.", chat_id, call.message.message_id)
            prompt_repeat_choice(bot, chat_id)
        elif call.data == "rem_time_tomorrow":
            next_trigger_time = datetime.now() + timedelta(days=1)
            data['next_trigger_time'] = next_trigger_time
            reminders_states[user_id]['state'] = 'awaiting_repeat_choice'
            bot.edit_message_text("Reminder time set to tomorrow.", chat_id, call.message.message_id)
            prompt_repeat_choice(bot, chat_id)
        elif call.data == "rem_time_custom":
            reminders_states[user_id]['state'] = 'awaiting_custom_time'
            bot.edit_message_text("Please enter the custom date and time in YYYY-MM-DD HH:MM format:", chat_id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "Unknown time option.")
    
    # Handle repeat type selection when state is 'awaiting_repeat_choice'
    elif current_state == 'awaiting_repeat_choice':
        if call.data == "rem_repeat_one_time":
            data['repeat_type'] = "one_time"
            data['repeat_value'] = None
            finalize_reminder(bot, chat_id, user_id)
            bot.answer_callback_query(call.id, "One-time reminder set.")
        elif call.data == "rem_repeat_every_hours":
            data['repeat_type'] = "every_x_hours"
            reminders_states[user_id]['state'] = 'awaiting_repeat_value'
            bot.edit_message_text("Please enter the number of hours for repetition:", chat_id, call.message.message_id)
        elif call.data == "rem_repeat_every_days":
            data['repeat_type'] = "every_x_days"
            reminders_states[user_id]['state'] = 'awaiting_repeat_value'
            bot.edit_message_text("Please enter the number of days for repetition:", chat_id, call.message.message_id)
        elif call.data == "rem_repeat_daily":
            data['repeat_type'] = "daily"
            data['repeat_value'] = None
            finalize_reminder(bot, chat_id, user_id)
            bot.answer_callback_query(call.id, "Daily reminder set.")
        else:
            bot.answer_callback_query(call.id, "Unknown repeat option.")
    else:
        bot.answer_callback_query(call.id, "No reminder action expected here.")

def prompt_time_options(bot, chat_id):
    """
    Sends an inline keyboard for time preset options.
    """
    markup = types.InlineKeyboardMarkup()
    btn_1hr = types.InlineKeyboardButton(text="In 1 hour", callback_data="rem_time_1hr")
    btn_2hrs = types.InlineKeyboardButton(text="In 2 hours", callback_data="rem_time_2hrs")
    btn_tomorrow = types.InlineKeyboardButton(text="Tomorrow", callback_data="rem_time_tomorrow")
    btn_custom = types.InlineKeyboardButton(text="Custom", callback_data="rem_time_custom")
    markup.row(btn_1hr, btn_2hrs)
    markup.row(btn_tomorrow, btn_custom)
    bot.send_message(chat_id, "When would you like the reminder to trigger?", reply_markup=markup)

def prompt_repeat_choice(bot, chat_id):
    """
    Sends an inline keyboard for repeat type options.
    """
    markup = types.InlineKeyboardMarkup()
    btn_one_time = types.InlineKeyboardButton(text="One-time", callback_data="rem_repeat_one_time")
    btn_every_hours = types.InlineKeyboardButton(text="Every X hours", callback_data="rem_repeat_every_hours")
    btn_every_days = types.InlineKeyboardButton(text="Every X days", callback_data="rem_repeat_every_days")
    btn_daily = types.InlineKeyboardButton(text="Daily", callback_data="rem_repeat_daily")
    markup.row(btn_one_time, btn_daily)
    markup.row(btn_every_hours, btn_every_days)
    bot.send_message(chat_id, "Should this reminder repeat? Choose an option:", reply_markup=markup)

def handle_reminder_messages(bot, message):
    """
    Handles text messages related to the add-reminder conversation.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id not in reminders_states:
        return  # Not in an active reminder conversation
    
    current_state = reminders_states[user_id]['state']
    data = reminders_states[user_id]['data']
    text = message.text.strip()

    if current_state == 'awaiting_title':
        # Save the reminder title and prompt for time options.
        data['title'] = text
        reminders_states[user_id]['state'] = 'awaiting_time_option'
        bot.send_message(chat_id, f"Reminder Title: {text}")
        prompt_time_options(bot, chat_id)
    
    elif current_state == 'awaiting_custom_time':
        # Expect custom time in "YYYY-MM-DD HH:MM" format.
        try:
            # Use parse_date to support both Gregorian and Jalali date inputs.
            custom_time = parse_date(text)
            data['next_trigger_time'] = custom_time
            reminders_states[user_id]['state'] = 'awaiting_repeat_choice'
            bot.send_message(chat_id, f"Custom reminder time set to: {custom_time.strftime('%Y-%m-%d %H:%M')}")
            prompt_repeat_choice(bot, chat_id)
        except ValueError:
            bot.send_message(chat_id, "Invalid format or conversion error. Please enter the date and time as YYYY-MM-DD HH:MM")
    
    elif current_state == 'awaiting_repeat_value':
        # Expect a numeric value for repetition interval.
        if text.isdigit():
            value = int(text)
            data['repeat_value'] = value
            finalize_reminder(bot, chat_id, user_id)
        else:
            bot.send_message(chat_id, "Please enter a valid number for the repetition interval.")
    
    else:
        bot.send_message(chat_id, "Unexpected input. Please follow the instructions.")

def finalize_reminder(bot, chat_id, user_id):
    """
    Finalizes the reminder by saving it into the database and confirming to the user.
    """
    data = reminders_states[user_id]['data']
    title = data.get('title')
    next_trigger_time = data.get('next_trigger_time')
    repeat_type = data.get('repeat_type')
    repeat_value = data.get('repeat_value')
    
    # Save reminder in DB.
    save_reminder_in_db(user_id, title, next_trigger_time, repeat_type, repeat_value)
    bot.send_message(chat_id,
                     f"Reminder added:\nTitle: {title}\nNext Trigger: {next_trigger_time.strftime('%Y-%m-%d %H:%M')}\nRepeat: {repeat_type} {repeat_value if repeat_value else ''}")
    # Clear the conversation state.
    reminders_states.pop(user_id, None)

def save_reminder_in_db(user_id, title, next_trigger_time, repeat_type, repeat_value):
    """
    Saves the reminder in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO reminders (user_id, title, next_trigger_time, repeat_type, repeat_value, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, title, next_trigger_time, repeat_type, repeat_value, now))
    conn.commit()
    conn.close()

def list_reminders(user_id):
    """
    Retrieves a list of reminders for the given user.
    Returns a list of sqlite3.Row objects.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reminders WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    reminders = cursor.fetchall()
    conn.close()
    return reminders

def update_reminder(user_id, reminder_id, **kwargs):
    """
    Updates a reminder with given keyword arguments.
    kwargs can include title, next_trigger_time, repeat_type, repeat_value.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(reminder_id)
    values.append(user_id)
    sql = f"UPDATE reminders SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
    cursor.execute(sql, tuple(values))
    conn.commit()
    conn.close()

def delete_reminder(user_id, reminder_id):
    """
    Deletes a reminder from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
    conn.commit()
    conn.close()

# --------------------------------------------
# Integration / Revision Summary:
#
# 1. database.py (Chunk 1) provides the SQLite DB and tables.
# 2. bot.py (Chunks 2, 3, 4, 5) integrates onboarding, main menu, tasks, and goals.
# 3. modules/reminders.py (this chunk) implements:
#      - start_add_reminder(bot, chat_id, user_id): Initiates the reminder addition conversation.
#      - handle_reminder_callbacks(bot, call): Processes inline button callbacks for time and repeat choices.
#      - handle_reminder_messages(bot, message): Processes text messages during the reminder addition flow.
#      - finalize_reminder(bot, chat_id, user_id): Finalizes and saves the reminder.
#      - save_reminder_in_db(user_id, title, next_trigger_time, repeat_type, repeat_value): Inserts the reminder record.
#      - Helper functions: list_reminders, update_reminder, delete_reminder.
#
# Integration Points in bot.py:
#    - Import the reminders module:
#          from modules.reminders import start_add_reminder, handle_reminder_callbacks, handle_reminder_messages, reminders_states
#
#    - Register a callback handler for reminders:
#          @bot.callback_query_handler(func=lambda call: call.data.startswith("rem_"))
#          def callback_reminder_handler(call):
#              handle_reminder_callbacks(bot, call)
#
#    - Register a message handler for reminder conversations:
#          @bot.message_handler(func=lambda message: message.from_user.id in reminders_states)
#          def message_reminder_handler(message):
#              handle_reminder_messages(bot, message)
#
#    - When the user selects "Add Reminder" from the Main Menu, call:
#          start_add_reminder(bot, chat_id, user_id)
#
# This module maintains overall consistency with the project structure and end goal.
