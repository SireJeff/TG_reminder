# modules/weekly_schedule.py

"""
This module implements the Weekly Schedule functionality.
It allows users to add recurring events that occur on a specific weekday at a specific time.
Users can add, list, update, and delete weekly events.
Each event includes:
  - A title (e.g., "Math Class")
  - A day of the week (e.g., Monday, Tuesday, etc.)
  - A time of day (HH:MM format)
  
Make sure to add a corresponding table in your database. For example:
  
CREATE TABLE IF NOT EXISTS weekly_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    day_of_week TEXT NOT NULL,  -- e.g., "Monday", "Tuesday", etc.
    time_of_day TEXT NOT NULL,  -- stored as "HH:MM"
    created_at DATETIME NOT NULL
);
"""

import sqlite3
from datetime import datetime
from telebot import types
from database import get_db_connection

# Bilingual messages for the weekly schedule module.
WEEKLY_MSG = {
    'en': {
        'enter_title': "Please enter the title of your weekly event:",
        'select_day': "Please select the day of the week:",
        'select_time': "Please enter the time for this event in HH:MM format (e.g., 09:30):",
        'event_added': "Weekly event added successfully!",
        'invalid_time': "Invalid time format. Please enter time as HH:MM.",
        'no_events': "No weekly events found."
    },
    'fa': {
        'enter_title': "لطفاً عنوان رویداد هفتگی خود را وارد کنید:",
        'select_day': "لطفاً روز هفته را انتخاب کنید:",
        'select_time': "لطفاً زمان این رویداد را به فرمت HH:MM وارد کنید (مثلاً 09:30):",
        'event_added': "رویداد هفتگی با موفقیت اضافه شد!",
        'invalid_time': "فرمت زمان نامعتبر است. لطفاً زمان را به صورت HH:MM وارد کنید.",
        'no_events': "هیچ رویداد هفتگی یافت نشد."
    }
}

# List of days for inline buttons.
DAYS_OF_WEEK = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
    ("Sunday", "Sunday")
]

# For Persian, you may localize these as needed.
DAYS_OF_WEEK_FA = [
    ("دوشنبه", "Monday"),
    ("سه‌شنبه", "Tuesday"),
    ("چهارشنبه", "Wednesday"),
    ("پنج‌شنبه", "Thursday"),
    ("جمعه", "Friday"),
    ("شنبه", "Saturday"),
    ("یکشنبه", "Sunday")
]

# Global dictionary to store weekly event conversation state per user.
weekly_states = {}

def start_add_weekly_event(bot, chat_id, user_id, user_lang='en'):
    """
    Initiates the add-weekly-event conversation.
    """
    weekly_states[user_id] = {
        'state': 'awaiting_title',
        'data': {}
    }
    bot.send_message(chat_id, WEEKLY_MSG[user_lang]['enter_title'])

def handle_weekly_event_messages(bot, message, user_lang='en'):
    """
    Handles text messages for the add-weekly-event conversation.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id not in weekly_states:
        return

    current_state = weekly_states[user_id]['state']
    data = weekly_states[user_id]['data']
    text = message.text.strip()

    if current_state == 'awaiting_title':
        data['title'] = text
        weekly_states[user_id]['state'] = 'awaiting_day'
        # Send an inline keyboard for day selection.
        markup = types.InlineKeyboardMarkup(row_width=3)
        if user_lang == 'fa':
            for day_fa, day_eng in DAYS_OF_WEEK_FA:
                btn = types.InlineKeyboardButton(text=day_fa, callback_data=f"week_day_{day_eng}")
                markup.add(btn)
        else:
            for day in DAYS_OF_WEEK:
                btn = types.InlineKeyboardButton(text=day[0], callback_data=f"week_day_{day[1]}")
                markup.add(btn)
        bot.send_message(chat_id, WEEKLY_MSG[user_lang]['select_day'], reply_markup=markup)
    elif current_state == 'awaiting_time':
        # Expect time in HH:MM format.
        try:
            # Validate the time format.
            datetime.strptime(text, "%H:%M")
            data['time_of_day'] = text
            # Save the event.
            save_weekly_event_in_db(user_id, data['title'], data['day_of_week'], text)
            bot.send_message(chat_id, WEEKLY_MSG[user_lang]['event_added'])
            weekly_states.pop(user_id, None)
        except ValueError:
            bot.send_message(chat_id, WEEKLY_MSG[user_lang]['invalid_time'])
    else:
        bot.send_message(chat_id, "Unexpected input. Please follow the instructions.")

def handle_weekly_event_callbacks(bot, call):
    """
    Handles callback queries for the weekly event creation flow.
    """
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if user_id not in weekly_states:
        return

    data = weekly_states[user_id]['data']
    current_state = weekly_states[user_id]['state']
    # Expect callback data like "week_day_Monday", etc.
    if current_state == 'awaiting_day' and call.data.startswith("week_day_"):
        day = call.data.split("week_day_")[1]
        data['day_of_week'] = day
        weekly_states[user_id]['state'] = 'awaiting_time'
        # Ask for the time of day.
        lang = get_user_lang(user_id)
        bot.send_message(chat_id, WEEKLY_MSG[lang]['select_time'])
        bot.answer_callback_query(call.id, f"Day set to {day}")
    else:
        bot.answer_callback_query(call.id, "Unknown weekly event action.")

def save_weekly_event_in_db(user_id, title, day_of_week, time_of_day):
    """
    Saves the weekly event in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO weekly_schedule (user_id, title, day_of_week, time_of_day, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, title, day_of_week, time_of_day, now))
    conn.commit()
    conn.close()

def list_weekly_events(user_id):
    """
    Retrieves a list of weekly events for the given user.
    Returns a list of sqlite3.Row objects.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weekly_schedule WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    events = cursor.fetchall()
    conn.close()
    return events

def update_weekly_event(user_id, event_id, **kwargs):
    """
    Updates a weekly event with the given keyword arguments.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(event_id)
    values.append(user_id)
    sql = f"UPDATE weekly_schedule SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
    cursor.execute(sql, tuple(values))
    conn.commit()
    conn.close()

def delete_weekly_event(user_id, event_id):
    """
    Deletes the specified weekly event from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM weekly_schedule WHERE id = ? AND user_id = ?", (event_id, user_id))
    conn.commit()
    conn.close()

def get_user_lang(user_id):
    """
    Helper function to retrieve the user's language from user_states.
    Fallback to English if not set.
    """
    from bot import user_states  # Assuming user_states is accessible from bot.py
    if user_id in user_states and 'language' in user_states[user_id]['data']:
        return user_states[user_id]['data']['language']
    return 'en'
