import sqlite3
from datetime import datetime, timedelta
from telebot import types
from database import get_db_connection
from modules.date_conversion import parse_date  # Supports both Gregorian and Jalali date inputs
from messages import MESSAGES

# New import from our flow helpers.
from flow_helpers import tracked_send_message, tracked_user_message, clear_flow_messages

# Import the messages dictionary from the main bot.


# Global dictionary to track task conversation state per user.
tasks_states = {}

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

def start_add_task(bot, chat_id, user_id):
    """
    Initiates the add-task conversation.
    """
    lang = get_user_language(user_id)
    tasks_states[user_id] = {'state': 'awaiting_title', 'data': {}}
    tracked_send_message(chat_id, user_id, MESSAGES[lang]['enter_task_title'])

def handle_task_callbacks(bot, call):
    """
    Handles callback queries for the task addition flow.
    """
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    lang = get_user_language(user_id)
    if user_id not in tasks_states:
        return  # Not in a task conversation

    current_state = tasks_states[user_id]['state']
    data = tasks_states[user_id]['data']

    # --- Due Date Decision ---
    if call.data == "task_set_due_yes" and current_state == 'awaiting_due_decision':
        tasks_states[user_id]['state'] = 'awaiting_due_option'
        markup = types.InlineKeyboardMarkup()
        btn_today = types.InlineKeyboardButton(text=MESSAGES[lang]['due_date_today'], callback_data="task_due_today")
        btn_tomorrow = types.InlineKeyboardButton(text=MESSAGES[lang]['due_date_tomorrow'], callback_data="task_due_tomorrow")
        btn_custom = types.InlineKeyboardButton(text=MESSAGES[lang]['due_date_custom'], callback_data="task_due_custom")
        markup.add(btn_today, btn_tomorrow, btn_custom)
        bot.edit_message_text(MESSAGES[lang]['select_due_date_option'], chat_id, call.message.message_id, reply_markup=markup)
    elif call.data == "task_set_due_skip" and current_state == 'awaiting_due_decision':
        save_task_in_db(user_id, data.get('title'), None)
        bot.edit_message_text(MESSAGES[lang]['task_added_no_due'], chat_id, call.message.message_id)
        tasks_states.pop(user_id, None)
        clear_flow_messages(chat_id, user_id)
    # --- Due Date Options ---
    elif call.data == "task_due_today" and current_state == 'awaiting_due_option':
        due_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
        save_task_in_db(user_id, data.get('title'), due_date)
        bot.edit_message_text(MESSAGES[lang]['task_added_today'], chat_id, call.message.message_id)
        tasks_states.pop(user_id, None)
        clear_flow_messages(chat_id, user_id)
    elif call.data == "task_due_tomorrow" and current_state == 'awaiting_due_option':
        tomorrow = datetime.now() + timedelta(days=1)
        due_date = tomorrow.replace(hour=23, minute=59, second=59, microsecond=0)
        save_task_in_db(user_id, data.get('title'), due_date)
        bot.edit_message_text(MESSAGES[lang]['task_added_tomorrow'], chat_id, call.message.message_id)
        tasks_states.pop(user_id, None)
        clear_flow_messages(chat_id, user_id)
    elif call.data == "task_due_custom" and current_state == 'awaiting_due_option':
        tasks_states[user_id]['state'] = 'awaiting_custom_due_date'
        bot.edit_message_text(MESSAGES[lang]['enter_custom_due_date'], chat_id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "Unknown task action.")

def handle_task_messages(bot, message):
    """
    Handles text messages related to the add-task conversation.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    lang = get_user_language(user_id)
    if user_id not in tasks_states:
        return  # Not in an active task conversation

    # Track user message for flow cleanup.
    tracked_user_message(message)
    current_state = tasks_states[user_id]['state']
    data = tasks_states[user_id]['data']
    text = message.text.strip()

    if current_state == 'awaiting_title':
        # Save the task title and prompt for due date decision.
        data['title'] = text
        tasks_states[user_id]['state'] = 'awaiting_due_decision'
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton(text="Yes", callback_data="task_set_due_yes")
        btn_skip = types.InlineKeyboardButton(text="Skip", callback_data="task_set_due_skip")
        markup.add(btn_yes, btn_skip)
        tracked_send_message(chat_id, user_id, MESSAGES[lang]['set_due_date_prompt'], reply_markup=markup)
    elif current_state == 'awaiting_custom_due_date':
        # Expect a custom due date in "YYYY-MM-DD HH:MM" format.
        try:
            due_date = parse_date(text)
            save_task_in_db(user_id, data.get('title'), due_date)
            bot.send_message(chat_id, f"{MESSAGES[lang]['task_added_custom']} {due_date.strftime('%Y-%m-%d %H:%M')}")
            tasks_states.pop(user_id, None)
            clear_flow_messages(chat_id, user_id)
        except ValueError as e:
            bot.send_message(chat_id, MESSAGES[lang]['invalid_date_format'].format(e))
    else:
        bot.send_message(chat_id, MESSAGES[lang]['unexpected_input'])

def save_task_in_db(user_id, title, due_date):
    """
    Saves the task in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO tasks (user_id, title, description, due_date, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)
    """, (user_id, title, None, due_date, now))
    conn.commit()
    conn.close()

def list_tasks(user_id):
    """
    Retrieves a list of tasks for the given user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def mark_task_done(user_id, task_id):
    """
    Marks the specified task as done.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'done' WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()

def delete_task(user_id, task_id):
    """
    Deletes the specified task from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()
