"""
modules/goals.py

This module implements the Goals functionality.
It allows users to add goals with a frequency option, schedules a next check date,
and provides helper functions for managing goals.

Goal Addition Flow:
1. User selects "Add Goal" from the Main Menu.
2. Bot: "Please enter the goal title:"
3. User sends the goal title → the title is saved in the conversation state.
4. Bot: "Please select the goal frequency:" with inline buttons (Daily, Weekly, Monthly, Seasonal, Yearly).
5. User selects a frequency → the callback handler computes the next_check_date and saves the goal to the DB.
6. A confirmation message is sent to the user.
7. Additional helper functions allow listing goals, marking them done, and deleting them.
"""

import sqlite3
from datetime import datetime, timedelta
from telebot import types
from database import get_db_connection

# Global dictionary to track goal creation conversation state per user.
# Structure: { user_id: { 'state': <state>, 'data': { ... } } }
goals_states = {}

def start_add_goal(bot, chat_id, user_id):
    """
    Initiates the add-goal conversation.
    Call this when the user selects "Add Goal" from the Main Menu.
    """
    goals_states[user_id] = {
        'state': 'awaiting_title',
        'data': {}
    }
    bot.send_message(chat_id, "Please enter the goal title:")

def handle_goal_messages(bot, message):
    """
    Handles text messages related to the add-goal conversation.
    This function should be registered as a message handler for users currently in goals_states.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in goals_states:
        return  # Not in an active goal conversation

    current_state = goals_states[user_id]['state']
    data = goals_states[user_id]['data']
    text = message.text.strip()

    if current_state == 'awaiting_title':
        # Save the goal title and prompt for frequency selection.
        data['title'] = text
        goals_states[user_id]['state'] = 'awaiting_frequency'
        
        # Create an inline keyboard for frequency selection.
        markup = types.InlineKeyboardMarkup()
        btn_daily = types.InlineKeyboardButton(text="Daily", callback_data="goal_freq_daily")
        btn_weekly = types.InlineKeyboardButton(text="Weekly", callback_data="goal_freq_weekly")
        btn_monthly = types.InlineKeyboardButton(text="Monthly", callback_data="goal_freq_monthly")
        btn_seasonal = types.InlineKeyboardButton(text="Seasonal", callback_data="goal_freq_seasonal")
        btn_yearly = types.InlineKeyboardButton(text="Yearly", callback_data="goal_freq_yearly")
        markup.row(btn_daily, btn_weekly)
        markup.row(btn_monthly, btn_seasonal, btn_yearly)
        
        bot.send_message(chat_id, "Please select the goal frequency:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Unexpected input. Please follow the instructions.")

def handle_goal_callbacks(bot, call):
    """
    Handles callback queries (inline button presses) for the goal creation flow.
    """
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if user_id not in goals_states:
        return  # Not in an active goal conversation

    current_state = goals_states[user_id]['state']
    data = goals_states[user_id]['data']

    if current_state == 'awaiting_frequency' and call.data.startswith("goal_freq_"):
        frequency = call.data.split("goal_freq_")[1]
        data['frequency'] = frequency

        # Compute next_check_date based on frequency.
        now = datetime.now()
        if frequency == "daily":
            next_check_date = now + timedelta(days=1)
        elif frequency == "weekly":
            next_check_date = now + timedelta(weeks=1)
        elif frequency == "monthly":
            # Approximate a month as 30 days.
            next_check_date = now + timedelta(days=30)
        elif frequency == "seasonal":
            # Approximate a season as 90 days.
            next_check_date = now + timedelta(days=90)
        elif frequency == "yearly":
            next_check_date = now + timedelta(days=365)
        else:
            next_check_date = now  # Fallback (should not occur)

        # Save the goal in the database.
        save_goal_in_db(user_id, data.get('title'), frequency, next_check_date)
        bot.answer_callback_query(call.id, "Goal added (" + frequency.capitalize() + ")")
        bot.edit_message_text(
            f"Goal added successfully.\nNext check date: {next_check_date.strftime('%Y-%m-%d %H:%M')}",
            chat_id,
            call.message.message_id
        )
        # Clear the conversation state.
        goals_states.pop(user_id, None)
        
        # Clear extra flow messages so that the main menu remains the last message.
        from bot import clear_flow_messages
        clear_flow_messages(chat_id, user_id)
    else:
        bot.answer_callback_query(call.id, "Unknown goal action.")

def save_goal_in_db(user_id, title, frequency, next_check_date):
    """
    Saves the goal in the database with status 'in_progress', the provided frequency,
    computed next_check_date, and the current creation timestamp.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO goals (user_id, title, frequency, next_check_date, status, created_at)
        VALUES (?, ?, ?, ?, 'in_progress', ?)
    """, (user_id, title, frequency, next_check_date, now))
    conn.commit()
    conn.close()

# Additional Goal Management Functions

def list_goals(user_id):
    """
    Retrieves a list of goals for the given user.
    Returns a list of sqlite3.Row objects.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    goals = cursor.fetchall()
    conn.close()
    return goals

def mark_goal_done(user_id, goal_id):
    """
    Marks the specified goal as done.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE goals SET status = 'done' WHERE id = ? AND user_id = ?", (goal_id, user_id))
    conn.commit()
    conn.close()

def delete_goal(user_id, goal_id):
    """
    Deletes the specified goal from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_id))
    conn.commit()
    conn.close()
#---------------------------
# Integration / Revision Summary:
#
# 1. database.py (Chunk 1) initializes the DB and tables.
# 2. bot.py (Chunk 2) contains bot initialization and onboarding.
# 3. modules/menu.py (Chunk 3) provides the Main Menu with navigation stubs.
# 4. modules/tasks.py (Chunk 4) implements task addition.
# 5. modules/goals.py (this Chunk 5) implements:
#      - start_add_goal(bot, chat_id, user_id): Initiates the goal creation flow.
#      - handle_goal_messages(bot, message): Processes goal title input.
#      - handle_goal_callbacks(bot, call): Processes frequency selection and computes next_check_date.
#      - save_goal_in_db(user_id, title, frequency, next_check_date): Inserts the goal record.
#      - Helper functions: list_goals, mark_goal_done, delete_goal.
#
# Integration Points in bot.py:
#    - Import the goals module:
#          from modules.goals import start_add_goal, handle_goal_messages, handle_goal_callbacks, goals_states
#
#    - Register a callback handler for goals:
#          @bot.callback_query_handler(func=lambda call: call.data.startswith("goal_freq_"))
#          def callback_goal_handler(call):
#              handle_goal_callbacks(bot, call)
#
#    - Register a message handler for goal conversations:
#          @bot.message_handler(func=lambda message: message.from_user.id in goals_states)
#          def message_goal_handler(message):
#              handle_goal_messages(bot, message)
#
#    - When the user selects "Add Goal" from the Main Menu, call:
#          start_add_goal(bot, chat_id, user_id)
#
# This module maintains consistency with the overall structure and end goal.
