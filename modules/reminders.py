import sqlite3
from datetime import datetime, timedelta
from telebot import types
from database import get_db_connection
from modules.date_conversion import parse_date  # Supports both Gregorian and Jalali date inputs
from messages import MESSAGES

# New import from our flow helpers.
from flow_helpers import tracked_send_message, tracked_user_message, clear_flow_messages

# Import the messages dictionary from the main bot.


# Global dictionary to track reminder conversation state per user.
reminders_states = {}

def get_user_language(user_id):
    """
    Retrieves the user's language from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 'en'

def start_add_reminder(bot, chat_id, user_id):
    """
    Initiates the add-reminder conversation.
    """
    lang = get_user_language(user_id)
    reminders_states[user_id] = {'state': 'awaiting_title', 'data': {}}
    tracked_send_message(chat_id, user_id, MESSAGES[lang]['enter_reminder_title'])

def handle_reminder_callbacks(bot, call):
    """
    Handles callback queries for the reminder addition flow.
    """
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    lang = get_user_language(user_id)
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
            bot.edit_message_text(MESSAGES[lang]['reminder_time_set_1hr'], chat_id, call.message.message_id)
            prompt_repeat_choice(bot, chat_id, user_id)
        elif call.data == "rem_time_2hrs":
            next_trigger_time = datetime.now() + timedelta(hours=2)
            data['next_trigger_time'] = next_trigger_time
            reminders_states[user_id]['state'] = 'awaiting_repeat_choice'
            bot.edit_message_text(MESSAGES[lang]['reminder_time_set_2hrs'], chat_id, call.message.message_id)
            prompt_repeat_choice(bot, chat_id, user_id)
        elif call.data == "rem_time_tomorrow":
            next_trigger_time = datetime.now() + timedelta(days=1)
            data['next_trigger_time'] = next_trigger_time
            reminders_states[user_id]['state'] = 'awaiting_repeat_choice'
            bot.edit_message_text(MESSAGES[lang]['reminder_time_set_tomorrow'], chat_id, call.message.message_id)
            prompt_repeat_choice(bot, chat_id, user_id)
        elif call.data == "rem_time_custom":
            reminders_states[user_id]['state'] = 'awaiting_custom_time'
            bot.edit_message_text(MESSAGES[lang]['enter_custom_time'], chat_id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, MESSAGES[lang]['unknown_time_option'])
    # Handle repeat type selection when state is 'awaiting_repeat_choice'
    elif current_state == 'awaiting_repeat_choice':
        if call.data == "rem_repeat_one_time":
            data['repeat_type'] = "one_time"
            data['repeat_value'] = None
            finalize_reminder(bot, chat_id, user_id)
            bot.answer_callback_query(call.id, MESSAGES[lang]['one_time_set'])
        elif call.data == "rem_repeat_every_hours":
            data['repeat_type'] = "every_x_hours"
            reminders_states[user_id]['state'] = 'awaiting_repeat_value'
            bot.edit_message_text(MESSAGES[lang]['enter_repeat_hours'], chat_id, call.message.message_id)
        elif call.data == "rem_repeat_every_days":
            data['repeat_type'] = "every_x_days"
            reminders_states[user_id]['state'] = 'awaiting_repeat_value'
            bot.edit_message_text(MESSAGES[lang]['enter_repeat_days'], chat_id, call.message.message_id)
        elif call.data == "rem_repeat_daily":
            data['repeat_type'] = "daily"
            data['repeat_value'] = None
            finalize_reminder(bot, chat_id, user_id)
            bot.answer_callback_query(call.id, MESSAGES[lang]['daily_reminder_set'])
        else:
            bot.answer_callback_query(call.id, MESSAGES[lang]['unknown_repeat_option'])
    else:
        bot.answer_callback_query(call.id, MESSAGES[lang]['no_reminder_action'])

def prompt_time_options(bot, chat_id, user_id):
    """
    Sends an inline keyboard for time preset options.
    """
    lang = get_user_language(user_id)
    markup = types.InlineKeyboardMarkup()
    btn_1hr = types.InlineKeyboardButton(text=MESSAGES[lang]['in_1_hour'], callback_data="rem_time_1hr")
    btn_2hrs = types.InlineKeyboardButton(text=MESSAGES[lang]['in_2_hours'], callback_data="rem_time_2hrs")
    btn_tomorrow = types.InlineKeyboardButton(text=MESSAGES[lang]['tomorrow'], callback_data="rem_time_tomorrow")
    btn_custom = types.InlineKeyboardButton(text=MESSAGES[lang]['custom'], callback_data="rem_time_custom")
    markup.row(btn_1hr, btn_2hrs)
    markup.row(btn_tomorrow, btn_custom)
    tracked_send_message(chat_id, user_id, MESSAGES[lang]['prompt_reminder_time'], reply_markup=markup)

def prompt_repeat_choice(bot, chat_id, user_id):
    """
    Sends an inline keyboard for repeat type options.
    """
    lang = get_user_language(user_id)
    markup = types.InlineKeyboardMarkup()
    btn_one_time = types.InlineKeyboardButton(text=MESSAGES[lang]['one_time'], callback_data="rem_repeat_one_time")
    btn_every_hours = types.InlineKeyboardButton(text=MESSAGES[lang]['every_x_hours'], callback_data="rem_repeat_every_hours")
    btn_every_days = types.InlineKeyboardButton(text=MESSAGES[lang]['every_x_days'], callback_data="rem_repeat_every_days")
    btn_daily = types.InlineKeyboardButton(text=MESSAGES[lang]['daily'], callback_data="rem_repeat_daily")
    markup.row(btn_one_time, btn_daily)
    markup.row(btn_every_hours, btn_every_days)
    tracked_send_message(chat_id, user_id, MESSAGES[lang]['prompt_repeat_choice'], reply_markup=markup)

def handle_reminder_messages(bot, message):
    """
    Handles text messages related to the add-reminder conversation.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    lang = get_user_language(user_id)
    if user_id not in reminders_states:
        return  # Not in an active reminder conversation

    # Track user message for flow cleanup.
    tracked_user_message(message)
    current_state = reminders_states[user_id]['state']
    data = reminders_states[user_id]['data']
    text = message.text.strip()

    if current_state == 'awaiting_title':
        data['title'] = text
        reminders_states[user_id]['state'] = 'awaiting_time_option'
        tracked_send_message(chat_id, user_id, MESSAGES[lang]['reminder_title_set'].format(text))
        prompt_time_options(bot, chat_id, user_id)
    elif current_state == 'awaiting_custom_time':
        try:
            custom_time = parse_date(text)
            data['next_trigger_time'] = custom_time
            reminders_states[user_id]['state'] = 'awaiting_repeat_choice'
            tracked_send_message(chat_id, user_id, MESSAGES[lang]['custom_time_set'].format(custom_time.strftime('%Y-%m-%d %H:%M')))
            prompt_repeat_choice(bot, chat_id, user_id)
        except ValueError as e:
            bot.send_message(chat_id, MESSAGES[lang]['invalid_date_format'].format(e))
    elif current_state == 'awaiting_repeat_value':
        if text.isdigit():
            value = int(text)
            data['repeat_value'] = value
            finalize_reminder(bot, chat_id, user_id)
        else:
            bot.send_message(chat_id, MESSAGES[lang]['invalid_repeat_interval'])
    else:
        bot.send_message(chat_id, MESSAGES[lang]['unexpected_input'])
        
def finalize_reminder(bot, chat_id, user_id):
    """
    Finalizes the reminder by saving it into the database and confirming to the user.
    Then clears all extra flow messages.
    """
    lang = get_user_language(user_id)
    data = reminders_states[user_id]['data']
    title = data.get('title')
    next_trigger_time = data.get('next_trigger_time')
    repeat_type = data.get('repeat_type')
    repeat_value = data.get('repeat_value')
    
    # Save reminder in DB.
    save_reminder_in_db(user_id, title, next_trigger_time, repeat_type, repeat_value)
    bot.send_message(chat_id,
                     MESSAGES[lang]['reminder_added'].format(
                         title=title,
                         next_trigger=next_trigger_time.strftime('%Y-%m-%d %H:%M'),
                         repeat=repeat_type,
                         value=repeat_value if repeat_value else ""
                     ))
    reminders_states.pop(user_id, None)
    clear_flow_messages(chat_id, user_id)

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
