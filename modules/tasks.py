"""
modules/tasks.py

This module implements the Tasks functionality.
It allows users to add tasks with an optional due date,
and provides functions to list, mark as done, or delete tasks.

Task Addition Flow:
1. User initiates task creation (e.g., via the Main Menu).
2. Bot: "Please enter the task title:"
3. User sends title → state saved.
4. Bot: "Would you like to set a due date for this task?" (Inline buttons: Yes / Skip)
5. If Yes → Bot offers options: Today, Tomorrow, Custom.
    - Today: Sets due date to today at 23:59.
    - Tomorrow: Sets due date to tomorrow at 23:59.
    - Custom: Bot prompts: "Enter due date and time in YYYY-MM-DD HH:MM format:"
6. Once the due date is set (or skipped), the task is saved in the database.
7. A confirmation message is sent.
"""

import sqlite3
from datetime import datetime, timedelta
from telebot import types
from database import get_db_connection

# Global dictionary to track task conversation state per user.
# Structure: { user_id: { 'state': <state>, 'data': { ... } } }
tasks_states = {}

def start_add_task(bot, chat_id, user_id):
    """
    Initiates the add-task conversation.
    
    Call this when the user selects "Add Task" from the Main Menu.
    """
    tasks_states[user_id] = {
        'state': 'awaiting_title',
        'data': {}
    }
    bot.send_message(chat_id, "Please enter the task title:")

def handle_task_callbacks(bot, call):
    """
    Handles callback queries (inline button presses) for the task addition flow.
    """
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if user_id not in tasks_states:
        return  # Not currently in a task conversation

    current_state = tasks_states[user_id]['state']
    data = tasks_states[user_id]['data']

    # --- Due Date Decision ---
    if call.data == "task_set_due_yes" and current_state == 'awaiting_due_decision':
        # User chose to set a due date. Offer options.
        tasks_states[user_id]['state'] = 'awaiting_due_option'
        markup = types.InlineKeyboardMarkup()
        btn_today = types.InlineKeyboardButton(text="Today", callback_data="task_due_today")
        btn_tomorrow = types.InlineKeyboardButton(text="Tomorrow", callback_data="task_due_tomorrow")
        btn_custom = types.InlineKeyboardButton(text="Custom", callback_data="task_due_custom")
        markup.add(btn_today, btn_tomorrow, btn_custom)
        bot.edit_message_text("Please select a due date option:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data == "task_set_due_skip" and current_state == 'awaiting_due_decision':
        # User chose not to set a due date.
        save_task_in_db(user_id, data.get('title'), None)
        bot.edit_message_text("Task added without a due date.", chat_id, call.message.message_id)
        tasks_states.pop(user_id, None)
    # --- Due Date Options ---
    elif call.data == "task_due_today" and current_state == 'awaiting_due_option':
        due_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
        save_task_in_db(user_id, data.get('title'), due_date)
        bot.edit_message_text("Task added with due date set to Today.", chat_id, call.message.message_id)
        tasks_states.pop(user_id, None)
    elif call.data == "task_due_tomorrow" and current_state == 'awaiting_due_option':
        tomorrow = datetime.now() + timedelta(days=1)
        due_date = tomorrow.replace(hour=23, minute=59, second=59, microsecond=0)
        save_task_in_db(user_id, data.get('title'), due_date)
        bot.edit_message_text("Task added with due date set to Tomorrow.", chat_id, call.message.message_id)
        tasks_states.pop(user_id, None)
    elif call.data == "task_due_custom" and current_state == 'awaiting_due_option':
        # Ask the user for a custom due date.
        tasks_states[user_id]['state'] = 'awaiting_custom_due_date'
        bot.edit_message_text("Please enter the custom due date and time in the format YYYY-MM-DD HH:MM (24hr):", chat_id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "Unknown task action.")

def handle_task_messages(bot, message):
    """
    Handles text messages related to the add-task conversation.
    This function should be registered as a message handler for users currently in tasks_states.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id not in tasks_states:
        return  # Not in an active task conversation
    
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
        bot.send_message(chat_id, "Would you like to set a due date for this task?", reply_markup=markup)
    elif current_state == 'awaiting_custom_due_date':
        # Expect a custom due date in "YYYY-MM-DD HH:MM" format.
        try:
            due_date = datetime.strptime(text, "%Y-%m-%d %H:%M")
            save_task_in_db(user_id, data.get('title'), due_date)
            bot.send_message(chat_id, f"Task added with custom due date: {due_date.strftime('%Y-%m-%d %H:%M')}")
            tasks_states.pop(user_id, None)
        except ValueError:
            bot.send_message(chat_id, "Invalid format. Please enter the date and time as YYYY-MM-DD HH:MM")
    else:
        bot.send_message(chat_id, "Unexpected input. Please follow the instructions.")

def save_task_in_db(user_id, title, due_date):
    """
    Saves the task in the database with status 'pending' and the current timestamp.
    
    Parameters:
      - user_id: Telegram user ID.
      - title: Task title.
      - due_date: A datetime object for the due date, or None.
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

# Additional Task Management Functions:

def list_tasks(user_id):
    """
    Retrieves a list of tasks for the given user.
    Returns a list of sqlite3.Row objects.
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

# --------------------------------------------
# Integration/Revision Summary:
#
# 1. database.py: (Chunk 1) Initializes the DB and tables.
# 2. bot.py: (Chunk 2) Contains bot initialization and onboarding.
# 3. modules/menu.py: (Chunk 3) Provides the Main Menu with navigation stubs.
# 4. modules/tasks.py: (Chunk 4) Implements task addition, including:
#      - start_add_task(bot, chat_id, user_id): Starts the task creation flow.
#      - handle_task_callbacks(bot, call): Processes inline button callbacks.
#      - handle_task_messages(bot, message): Processes text messages during task creation.
#      - save_task_in_db(user_id, title, due_date): Saves the task.
#      - Additional helper functions: list_tasks, mark_task_done, delete_task.
#
# Integration Points in bot.py:
#    - Import tasks module:
#          from modules.tasks import start_add_task, handle_task_callbacks, handle_task_messages
#
#    - Register a callback handler for task-related callbacks:
#          @bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
#          def callback_task_handler(call):
#              handle_task_callbacks(bot, call)
#
#    - Register a message handler for users in the tasks conversation:
#          @bot.message_handler(func=lambda message: message.from_user.id in tasks_states)
#          def message_task_handler(message):
#              handle_task_messages(bot, message)
#
#    - When the user selects "Add Task" from the main menu:
#          start_add_task(bot, chat_id, user_id)
#
# This revision ensures consistency with the overall project structure and end goal.
