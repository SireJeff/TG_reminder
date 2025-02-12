import sqlite3
from datetime import datetime, timedelta
from telebot import types
from database import get_db_connection
from modules.date_conversion import parse_date  # Supports both Gregorian and Jalali date inputs

# Old line (to be removed):
# from bot import tracked_send_message, tracked_user_message, clear_flow_messages

# New import:
from flow_helpers import tracked_send_message, tracked_user_message, clear_flow_messages


# Global dictionary to track task conversation state per user.
tasks_states = {}

def start_add_task(bot, chat_id, user_id):
    """
    Initiates the add-task conversation.
    """
    tasks_states[user_id] = {'state': 'awaiting_title', 'data': {}}
    tracked_send_message(chat_id, user_id, "Please enter the task title:")

def handle_task_callbacks(bot, call):
    """
    Handles callback queries for the task addition flow.
    """
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if user_id not in tasks_states:
        return  # Not in a task conversation

    current_state = tasks_states[user_id]['state']
    data = tasks_states[user_id]['data']

    # --- Due Date Decision ---
    if call.data == "task_set_due_yes" and current_state == 'awaiting_due_decision':
        tasks_states[user_id]['state'] = 'awaiting_due_option'
        markup = types.InlineKeyboardMarkup()
        btn_today = types.InlineKeyboardButton(text="Today", callback_data="task_due_today")
        btn_tomorrow = types.InlineKeyboardButton(text="Tomorrow", callback_data="task_due_tomorrow")
        btn_custom = types.InlineKeyboardButton(text="Custom", callback_data="task_due_custom")
        markup.add(btn_today, btn_tomorrow, btn_custom)
        bot.edit_message_text("Please select a due date option:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data == "task_set_due_skip" and current_state == 'awaiting_due_decision':
        save_task_in_db(user_id, data.get('title'), None)
        bot.edit_message_text("Task added without a due date.", chat_id, call.message.message_id)
        tasks_states.pop(user_id, None)
        clear_flow_messages(chat_id, user_id)
    # --- Due Date Options ---
    elif call.data == "task_due_today" and current_state == 'awaiting_due_option':
        due_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
        save_task_in_db(user_id, data.get('title'), due_date)
        bot.edit_message_text("Task added with due date set to Today.", chat_id, call.message.message_id)
        tasks_states.pop(user_id, None)
        clear_flow_messages(chat_id, user_id)
    elif call.data == "task_due_tomorrow" and current_state == 'awaiting_due_option':
        tomorrow = datetime.now() + timedelta(days=1)
        due_date = tomorrow.replace(hour=23, minute=59, second=59, microsecond=0)
        save_task_in_db(user_id, data.get('title'), due_date)
        bot.edit_message_text("Task added with due date set to Tomorrow.", chat_id, call.message.message_id)
        tasks_states.pop(user_id, None)
        clear_flow_messages(chat_id, user_id)
    elif call.data == "task_due_custom" and current_state == 'awaiting_due_option':
        tasks_states[user_id]['state'] = 'awaiting_custom_due_date'
        bot.edit_message_text("Please enter the custom due date and time in the format YYYY-MM-DD HH:MM (24hr):", chat_id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "Unknown task action.")

def handle_task_messages(bot, message):
    """
    Handles text messages related to the add-task conversation.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id not in tasks_states:
        return  # Not in an active task conversation

    # Track user message for flow cleanup
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
        tracked_send_message(chat_id, user_id, "Would you like to set a due date for this task?", reply_markup=markup)
    elif current_state == 'awaiting_custom_due_date':
        # Expect a custom due date in "YYYY-MM-DD HH:MM" format.
        try:
            due_date = parse_date(text)
            save_task_in_db(user_id, data.get('title'), due_date)
            bot.send_message(chat_id, f"Task added with custom due date: {due_date.strftime('%Y-%m-%d %H:%M')}")
            tasks_states.pop(user_id, None)
            clear_flow_messages(chat_id, user_id)
        except ValueError as e:
            bot.send_message(chat_id, f"Invalid date format or conversion error: {e}\nPlease enter the date and time as YYYY-MM-DD HH:MM")
    else:
        bot.send_message(chat_id, "Unexpected input. Please follow the instructions.")

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
