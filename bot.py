"""
bot.py

This is the main entry point for the bot. It integrates:
  - Onboarding (language, timezone, summary schedule, random check-in)
  - Main Menu & Navigation
  - Tasks Module
  - Goals Module
  - Reminders Module
  - Countdowns Module
  - Random Check-Ins Module
  - Summaries & Reports Module
  - Quotes Module

Ensure that the following modules/files are available:
  - database.py
  - modules/menu.py
  - modules/tasks.py
  - modules/goals.py
  - modules/reminders.py
  - modules/countdowns.py
  - modules/random_checkins.py
  - modules/summaries.py
  - modules/quotes.py

Replace "YOUR_TELEGRAM_BOT_TOKEN" with your actual bot token.
"""

import telebot
from telebot import types
from datetime import datetime
from database import get_db_connection, init_db

# -------------------------------
# Bot Initialization
# -------------------------------
BOT_TOKEN = "7993339613:AAH2wXp3RKqIPoZssPvtbHvzKleu5yVbDzQ"
bot = telebot.TeleBot(BOT_TOKEN)

# -------------------------------
# Onboarding State Definitions (Chunk 2)
# -------------------------------
STATE_LANGUAGE = "language"
STATE_TIMEZONE = "timezone"
STATE_SUMMARY_SCHEDULE = "summary_schedule"
STATE_SUMMARY_TIME = "summary_time"   # For daily time (HH:MM) or custom interval (in hours)
STATE_RANDOM_CHECKIN = "random_checkin"
STATE_COMPLETED = "completed"

# Global dictionary to store onboarding conversation state per user.
# Structure: { user_id: { 'state': <current_state>, 'data': { ... } } }
user_states = {}

# -------------------------------
# /start Command Handler & Onboarding Flow (Chunk 2)
# -------------------------------
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id

    # Check if the user exists in the DB; if not, create a new record.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        # Create a new user record with default values.
        cursor.execute("""
            INSERT INTO users (user_id, language, timezone, summary_schedule, summary_time, random_checkin_max)
            VALUES (?, 'en', 'UTC', 'disabled', NULL, 0)
        """, (user_id,))
        conn.commit()
    conn.close()

    # Initialize onboarding state.
    user_states[user_id] = {
        'state': STATE_LANGUAGE,
        'data': {}
    }
    
    # Prompt for language selection.
    markup = types.InlineKeyboardMarkup()
    btn_english = types.InlineKeyboardButton(text="English", callback_data="set_lang_en")
    markup.add(btn_english)
    bot.send_message(message.chat.id, "Welcome to the bot! Please select your language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_") or call.data.startswith("set_summary_"))
def onboarding_callback_handler(call):
    user_id = call.from_user.id
    if user_id not in user_states:
        return
    state_info = user_states[user_id]
    current_state = state_info.get('state')

    # --- Language Selection ---
    if call.data.startswith("set_lang_") and current_state == STATE_LANGUAGE:
        selected_lang = call.data.split("set_lang_")[1]
        # Update user's language in the DB.
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (selected_lang, user_id))
        conn.commit()
        conn.close()

        user_states[user_id]['data']['language'] = selected_lang
        user_states[user_id]['state'] = STATE_TIMEZONE

        bot.answer_callback_query(call.id, "Language set to " + selected_lang)
        bot.send_message(call.message.chat.id, "Please enter your timezone (e.g., Asia/Tehran or UTC+3:30):")
    
    # --- Summary Schedule Selection ---
    elif call.data.startswith("set_summary_") and current_state == STATE_SUMMARY_SCHEDULE:
        selection = call.data.split("set_summary_")[1]
        if selection == "daily":
            user_states[user_id]['data']['summary_schedule'] = 'daily'
            user_states[user_id]['state'] = STATE_SUMMARY_TIME
            bot.answer_callback_query(call.id, "Daily summary selected")
            bot.send_message(call.message.chat.id, "Please enter the time for your daily summary in HH:MM format (e.g., 20:00):")
        elif selection == "custom":
            user_states[user_id]['data']['summary_schedule'] = 'custom'
            user_states[user_id]['state'] = STATE_SUMMARY_TIME
            bot.answer_callback_query(call.id, "Custom summary interval selected")
            bot.send_message(call.message.chat.id, "Please enter the interval in hours for your summary (e.g., 3):")
        elif selection == "none":
            user_states[user_id]['data']['summary_schedule'] = 'disabled'
            # Update DB immediately.
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET summary_schedule = ? WHERE user_id = ?", ('disabled', user_id))
            conn.commit()
            conn.close()

            user_states[user_id]['state'] = STATE_RANDOM_CHECKIN
            bot.answer_callback_query(call.id, "No summary will be sent")
            bot.send_message(call.message.chat.id, "How many random check-ins per day would you like? (Enter a number, e.g., 2)")
    else:
        bot.answer_callback_query(call.id, "Unhandled onboarding callback.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') in [STATE_TIMEZONE, STATE_SUMMARY_TIME, STATE_RANDOM_CHECKIN])
def onboarding_message_handler(message):
    user_id = message.from_user.id
    current_state = user_states[user_id]['state']
    text = message.text.strip()

    # --- Timezone Entry ---
    if current_state == STATE_TIMEZONE:
        # Save timezone in DB.
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET timezone = ? WHERE user_id = ?", (text, user_id))
        conn.commit()
        conn.close()

        user_states[user_id]['data']['timezone'] = text
        user_states[user_id]['state'] = STATE_SUMMARY_SCHEDULE

        # Build inline keyboard for summary schedule options.
        markup = types.InlineKeyboardMarkup()
        btn_daily = types.InlineKeyboardButton(text="Daily", callback_data="set_summary_daily")
        btn_custom = types.InlineKeyboardButton(text="Every X hours", callback_data="set_summary_custom")
        btn_none = types.InlineKeyboardButton(text="None", callback_data="set_summary_none")
        markup.add(btn_daily, btn_custom, btn_none)
        bot.send_message(message.chat.id, "How would you like to receive summaries? Choose one:", reply_markup=markup)
    
    # --- Summary Time / Custom Interval ---
    elif current_state == STATE_SUMMARY_TIME:
        summary_schedule = user_states[user_id]['data'].get('summary_schedule')
        if summary_schedule == 'daily':
            try:
                datetime.strptime(text, "%H:%M")  # Validate HH:MM format.
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET summary_schedule = ?, summary_time = ? WHERE user_id = ?", ('daily', text, user_id))
                conn.commit()
                conn.close()

                user_states[user_id]['data']['summary_time'] = text
                user_states[user_id]['state'] = STATE_RANDOM_CHECKIN
                bot.send_message(message.chat.id, f"Daily summary set at {text}. Now, how many random check-ins per day would you like? (Enter a number, e.g., 2)")
            except ValueError:
                bot.send_message(message.chat.id, "Invalid time format. Please enter HH:MM (e.g., 20:00)")
        elif summary_schedule == 'custom':
            if text.isdigit():
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET summary_schedule = ?, summary_time = ? WHERE user_id = ?", ('custom', text, user_id))
                conn.commit()
                conn.close()

                user_states[user_id]['data']['summary_time'] = text
                user_states[user_id]['state'] = STATE_RANDOM_CHECKIN
                bot.send_message(message.chat.id, f"Custom summary interval set to every {text} hours. Now, how many random check-ins per day would you like? (Enter a number, e.g., 2)")
            else:
                bot.send_message(message.chat.id, "Please enter a valid number (e.g., 3):")
    
    # --- Random Check-In Preference ---
    elif current_state == STATE_RANDOM_CHECKIN:
        if text.isdigit():
            random_checkin = int(text)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET random_checkin_max = ? WHERE user_id = ?", (random_checkin, user_id))
            conn.commit()
            conn.close()

            user_states[user_id]['data']['random_checkin'] = random_checkin
            user_states[user_id]['state'] = STATE_COMPLETED
            bot.send_message(message.chat.id, "Onboarding complete! Welcome to the bot.")
            # Show the Main Menu after onboarding.
            from modules.menu import send_main_menu
            send_main_menu(bot, message.chat.id)
        else:
            bot.send_message(message.chat.id, "Please enter a valid number (e.g., 2):")

# -------------------------------
# Integration: Main Menu Module (Chunk 3)
# -------------------------------
from modules.menu import send_main_menu, register_menu_handlers
register_menu_handlers(bot)  # Registers main menu callback handlers.

# -------------------------------
# Integration: Tasks Module (Chunk 4)
# -------------------------------
from modules.tasks import start_add_task, handle_task_callbacks, handle_task_messages, tasks_states

@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def callback_task_handler(call):
    handle_task_callbacks(bot, call)

@bot.message_handler(func=lambda message: message.from_user.id in tasks_states)
def message_task_handler(message):
    handle_task_messages(bot, message)

# -------------------------------
# Integration: Goals Module (Chunk 5)
# -------------------------------
from modules.goals import start_add_goal, handle_goal_callbacks, handle_goal_messages, goals_states

@bot.callback_query_handler(func=lambda call: call.data.startswith("goal_freq_"))
def callback_goal_handler(call):
    handle_goal_callbacks(bot, call)

@bot.message_handler(func=lambda message: message.from_user.id in goals_states)
def message_goal_handler(message):
    handle_goal_messages(bot, message)

# -------------------------------
# Integration: Reminders Module (Chunk 6)
# -------------------------------
from modules.reminders import start_add_reminder, handle_reminder_callbacks, handle_reminder_messages, reminders_states

@bot.callback_query_handler(func=lambda call: call.data.startswith("rem_"))
def callback_reminder_handler(call):
    handle_reminder_callbacks(bot, call)

@bot.message_handler(func=lambda message: message.from_user.id in reminders_states)
def message_reminder_handler(message):
    handle_reminder_messages(bot, message)

# -------------------------------
# Integration: Countdowns Module (Chunk 7)
# -------------------------------
from modules.countdowns import start_add_countdown, handle_countdown_messages, handle_countdown_callbacks, countdowns_states

@bot.callback_query_handler(func=lambda call: call.data.startswith("countdown_notify_"))
def callback_countdown_handler(call):
    handle_countdown_callbacks(bot, call)

@bot.message_handler(func=lambda message: message.from_user.id in countdowns_states)
def message_countdown_handler(message):
    handle_countdown_messages(bot, message)

# -------------------------------
# Integration: Random Check-Ins Module (Chunk 8)
# -------------------------------
from modules.random_checkins import send_random_checkin, handle_random_checkin_callback, schedule_daily_checkins

@bot.callback_query_handler(func=lambda call: call.data.startswith("random_"))
def callback_random_handler(call):
    handle_random_checkin_callback(bot, call)

# -------------------------------
# Integration: Summaries & Reports Module (Chunk 9)
# -------------------------------
from modules.summaries import send_summary, generate_summary
# (You may later integrate scheduling of summaries using a scheduler.
# For now, the menu option below will trigger the summary report.)

# -------------------------------
# Integration: Quotes Module (Chunk 10)
# -------------------------------
from modules.quotes import start_add_quote, handle_quote_messages, quotes_states, get_random_quote

@bot.message_handler(func=lambda message: message.from_user.id in quotes_states)
def message_quote_handler(message):
    handle_quote_messages(bot, message)

# -------------------------------
# Integration: Main Menu Selections
# (Overrides the placeholders in the Main Menu to call the proper modules.)
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def callback_menu_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    if data == "menu_add_task":
        start_add_task(bot, chat_id, user_id)
    elif data == "menu_add_goal":
        start_add_goal(bot, chat_id, user_id)
    elif data == "menu_add_reminder":
        start_add_reminder(bot, chat_id, user_id)
    elif data == "menu_add_countdown":
        start_add_countdown(bot, chat_id, user_id)
    elif data == "menu_view_summary":
        # Call the summaries module to send a summary report.
        send_summary(bot, chat_id, user_id)
    elif data == "menu_manage_items":
        bot.send_message(chat_id, "You selected Manage Items. [Placeholder for items management module]")
    elif data == "menu_quotes":
        # Start the quote addition flow.
        start_add_quote(bot, chat_id, user_id)
    elif data == "menu_settings":
        bot.send_message(chat_id, "You selected Settings. [Placeholder for settings module]")
    else:
        bot.send_message(chat_id, "Unknown menu option selected.")

# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == "__main__":
    # Initialize the database.
    init_db()
    print("Bot is running...")
    bot.infinity_polling()
