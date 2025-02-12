import sqlite3
from datetime import datetime, timedelta
from telebot import types
from database import get_db_connection

# Old line (to be removed):
# from bot import tracked_send_message, tracked_user_message, clear_flow_messages

# New import:
from flow_helpers import tracked_send_message, tracked_user_message, clear_flow_messages

# Global dictionary to track goal creation conversation state per user.
goals_states = {}

def start_add_goal(bot, chat_id, user_id):
    """
    Initiates the add-goal conversation.
    """
    goals_states[user_id] = {'state': 'awaiting_title', 'data': {}}
    tracked_send_message(chat_id, user_id, "Please enter the goal title:")

def handle_goal_messages(bot, message):
    """
    Handles text messages related to the add-goal conversation.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id not in goals_states:
        return  # Not in an active goal conversation

    # Track the user message for cleanup.
    tracked_user_message(message)
    current_state = goals_states[user_id]['state']
    data = goals_states[user_id]['data']
    text = message.text.strip()

    if current_state == 'awaiting_title':
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
        
        tracked_send_message(chat_id, user_id, "Please select the goal frequency:", reply_markup=markup)
    else:
        tracked_send_message(chat_id, user_id, "Unexpected input. Please follow the instructions.")

def handle_goal_callbacks(bot, call):
    """
    Handles callback queries for the goal creation flow.
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

        now = datetime.now()
        if frequency == "daily":
            next_check_date = now + timedelta(days=1)
        elif frequency == "weekly":
            next_check_date = now + timedelta(weeks=1)
        elif frequency == "monthly":
            next_check_date = now + timedelta(days=30)
        elif frequency == "seasonal":
            next_check_date = now + timedelta(days=90)
        elif frequency == "yearly":
            next_check_date = now + timedelta(days=365)
        else:
            next_check_date = now  # Fallback (should not occur)

        save_goal_in_db(user_id, data.get('title'), frequency, next_check_date)
        bot.answer_callback_query(call.id, "Goal added (" + frequency.capitalize() + ")")
        bot.edit_message_text(
            f"Goal added successfully.\nNext check date: {next_check_date.strftime('%Y-%m-%d %H:%M')}",
            chat_id,
            call.message.message_id
        )
        goals_states.pop(user_id, None)
        clear_flow_messages(chat_id, user_id)
    else:
        bot.answer_callback_query(call.id, "Unknown goal action.")

def save_goal_in_db(user_id, title, frequency, next_check_date):
    """
    Saves the goal in the database.
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

def list_goals(user_id):
    """
    Retrieves a list of goals for the given user.
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
