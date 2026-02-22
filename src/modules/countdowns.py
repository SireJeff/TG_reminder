from datetime import datetime, timedelta
from telebot import types
from database import get_db_connection
from modules.date_conversion import parse_date  # Supports both Gregorian and Jalali dates

# New import:
from flow_helpers import tracked_send_message, tracked_user_message, clear_flow_messages
from messages import MESSAGES

# Global dictionary to track countdown conversation state per user.
countdowns_states = {}

def get_user_language(user_id):
    """Retrieves the user's language from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 'en'

def start_add_countdown(bot, chat_id, user_id):
    """
    Initiates the add-countdown conversation.
    """
    lang = get_user_language(user_id)
    countdowns_states[user_id] = {'state': 'awaiting_title', 'data': {}}
    tracked_send_message(chat_id, user_id, MESSAGES[lang]['enter_countdown_title'])

def handle_countdown_messages(bot, message):
    """
    Handles text messages related to the countdown addition flow.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    lang = get_user_language(user_id)
    if user_id not in countdowns_states:
        return  # Not in an active countdown conversation

    # Track the user message for cleanup.
    tracked_user_message(message)
    current_state = countdowns_states[user_id]['state']
    data = countdowns_states[user_id]['data']
    text = message.text.strip()

    if current_state == 'awaiting_title':
        data['title'] = text
        countdowns_states[user_id]['state'] = 'awaiting_datetime'
        tracked_send_message(chat_id, user_id, MESSAGES[lang]['enter_countdown_datetime'])
    elif current_state == 'awaiting_datetime':
        try:
            event_datetime = parse_date(text)
            data['event_datetime'] = event_datetime
            countdowns_states[user_id]['state'] = 'awaiting_notify_choice'
            prompt_notify_choice(bot, chat_id, user_id)
        except ValueError as e:
            tracked_send_message(chat_id, user_id, MESSAGES[lang]['invalid_countdown_datetime'].format(e))
    else:
        tracked_send_message(chat_id, user_id, MESSAGES[lang]['unexpected_input'])

def prompt_notify_choice(bot, chat_id, user_id):
    """
    Sends an inline keyboard for periodic alert options for the countdown.
    """
    lang = get_user_language(user_id)
    markup = types.InlineKeyboardMarkup()
    btn_none = types.InlineKeyboardButton(text=MESSAGES[lang]['no_alerts'], callback_data="countdown_notify_none")
    btn_daily = types.InlineKeyboardButton(text=MESSAGES[lang]['daily_alerts'], callback_data="countdown_notify_daily")
    btn_weekly = types.InlineKeyboardButton(text=MESSAGES[lang]['weekly_alerts'], callback_data="countdown_notify_weekly")
    markup.row(btn_none, btn_daily, btn_weekly)
    tracked_send_message(chat_id, user_id, MESSAGES[lang]['prompt_countdown_alerts'], reply_markup=markup)

def handle_countdown_callbacks(bot, call):
    """
    Handles callback queries for the countdown addition flow.
    """
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    lang = get_user_language(user_id)
    if user_id not in countdowns_states:
        return

    current_state = countdowns_states[user_id]['state']
    data = countdowns_states[user_id]['data']

    if current_state == 'awaiting_notify_choice':
        if call.data.startswith("countdown_notify_"):
            option = call.data.split("countdown_notify_")[1]
            if option in ['none', 'daily', 'weekly']:
                data['notify_schedule'] = option
                finalize_countdown(bot, chat_id, user_id)
                bot.answer_callback_query(call.id, MESSAGES[lang]['alert_option_set'].format(option=option.capitalize()))
            else:
                bot.answer_callback_query(call.id, MESSAGES[lang]['unknown_alert_option'])
    else:
        bot.answer_callback_query(call.id, MESSAGES[lang]['no_countdown_action'])

def finalize_countdown(bot, chat_id, user_id):
    """
    Finalizes the countdown event by saving it into the database and confirming to the user.
    Then, clears all extra messages from the flow.
    """
    lang = get_user_language(user_id)
    data = countdowns_states[user_id]['data']
    title = data.get('title')
    event_datetime = data.get('event_datetime')
    notify_schedule = data.get('notify_schedule', 'none')
    save_countdown_in_db(user_id, title, event_datetime, notify_schedule)
    time_left = compute_time_left(event_datetime, lang)
    bot.send_message(chat_id,
                     MESSAGES[lang]['countdown_added'].format(
                         title=title,
                         event_time=event_datetime.strftime('%Y-%m-%d %H:%M'),
                         time_left=time_left,
                         alerts=notify_schedule.capitalize()
                     ))
    countdowns_states.pop(user_id, None)
    clear_flow_messages(chat_id, user_id)

def save_countdown_in_db(user_id, title, event_datetime, notify_schedule):
    """
    Saves the countdown event into the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO countdowns (user_id, title, event_datetime, notify_schedule, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, title, event_datetime, notify_schedule, now))
    conn.commit()
    conn.close()

def compute_time_left(event_datetime, lang='en'):
    """
    Computes the time left until the event.
    Returns a string in the format "X days, Y hours left" (or "Event passed" if in the past).
    """
    now = datetime.now()
    delta = event_datetime - now
    if delta.total_seconds() < 0:
        return MESSAGES[lang].get('event_passed', "Event passed")
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    return ", ".join(parts) + " left" if parts else "Less than a minute left"

def list_countdowns(user_id):
    """
    Retrieves a list of countdown events for the given user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM countdowns WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    countdowns = cursor.fetchall()
    conn.close()
    return countdowns

def delete_countdown(user_id, countdown_id):
    """
    Deletes the specified countdown event from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM countdowns WHERE id = ? AND user_id = ?", (countdown_id, user_id))
    conn.commit()
    conn.close()
