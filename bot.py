"""
bot.py

This is the main entry point for the bot. It integrates:
  - Onboarding (multilingual language selection, time zone selection via inline buttons, summary schedule, random check-in)
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
# Multilingual Message Dictionary
# -------------------------------
MESSAGES = {
    'en': {
        'welcome': "Welcome to the bot! Please select your language:",
        'select_timezone': "Please select your timezone:",
        'set_timezone': "Timezone set to {}.",
        'select_summary': "How would you like to receive summaries? Choose one:",
        'enter_daily_time': "Please enter the time for your daily summary in HH:MM format (e.g., 20:00):",
        'enter_custom_interval': "Please enter the interval in hours for your summary (e.g., 3):",
        'enter_random_checkins': "How many random check-ins per day would you like? (Enter a number, e.g., 2)",
        'onboarding_complete': "Onboarding complete! Welcome to the bot."
    },
    'fa': {
        'welcome': "به ریمایندینو خوش آمدید! لطفاً زبان خود را انتخاب کنید:",
        'select_timezone': "لطفاً منطقه زمانی خود را انتخاب کنید:",
        'set_timezone': "منطقه زمانی {} تنظیم شد.",
        'select_summary': "چگونه می‌خواهید خلاصه‌ها را دریافت کنید؟ یکی را انتخاب کنید:",
        'enter_daily_time': "لطفاً زمان دریافت خلاصه روزانه خود را به فرمت HH:MM وارد کنید (مثلاً 20:00):",
        'enter_custom_interval': "لطفاً فاصله زمانی به ساعت برای دریافت خلاصه را وارد کنید (مثلاً 3):",
        'enter_random_checkins': "چند بار در روز می‌خواهید یادآوری‌های تصادفی دریافت کنید؟ (یک عدد وارد کنید، مثلاً 2)",
        'onboarding_complete': "فرایند راه‌اندازی کامل شد! به ریمایندینو خوش آمدید."
    }
}

# -------------------------------
# Pre-defined Time Zone Choices
# -------------------------------
TIMEZONE_CHOICES = [
    ("Tehran", "Asia/Tehran"),
    ("London", "Europe/London"),
    ("New York", "America/New_York"),
    ("Kolkata", "Asia/Kolkata"),
    ("Shanghai", "Asia/Shanghai"),
    ("Berlin", "Europe/Berlin"),
    ("Los Angeles", "America/Los_Angeles"),
    ("Sydney", "Australia/Sydney"),
    ("Sao Paulo", "America/Sao_Paulo"),
    ("Moscow", "Europe/Moscow")
]

# -------------------------------
# Onboarding State Definitions
# -------------------------------
STATE_LANGUAGE = "language"
STATE_TIMEZONE = "timezone"      # Now handled via inline buttons
STATE_SUMMARY_SCHEDULE = "summary_schedule"
STATE_SUMMARY_TIME = "summary_time"   # For daily time (HH:MM) or custom interval (in hours)
STATE_RANDOM_CHECKIN = "random_checkin"
STATE_COMPLETED = "completed"

# Global dictionary to store onboarding conversation state per user.
# Structure: { user_id: { 'state': <current_state>, 'data': { ... } } }
user_states = {}

# -------------------------------
# /start Command Handler & Onboarding Flow
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
    
    # Prompt for language selection with two buttons.
    markup = types.InlineKeyboardMarkup()
    btn_english = types.InlineKeyboardButton(text="English", callback_data="set_lang_en")
    btn_farsi = types.InlineKeyboardButton(text="فارسی", callback_data="set_lang_fa")
    markup.add(btn_english, btn_farsi)
    # Use English welcome text by default (it will be replaced once language is set).
    bot.send_message(message.chat.id, MESSAGES['en']['welcome'], reply_markup=markup)

# -------------------------------
# Language Selection Callback Handler
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def language_callback_handler(call):
    user_id = call.from_user.id
    if user_id not in user_states:
        return
    selected_lang = call.data.split("set_lang_")[1]  # either "en" or "fa"
    # Update user's language in DB.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (selected_lang, user_id))
    conn.commit()
    conn.close()

    user_states[user_id]['data']['language'] = selected_lang
    # Move state to timezone selection.
    user_states[user_id]['state'] = STATE_TIMEZONE
    bot.answer_callback_query(call.id, f"Language set to {selected_lang}")
    
    # Send timezone selection inline keyboard.
    lang = selected_lang
    tz_markup = types.InlineKeyboardMarkup(row_width=2)
    for label, tz_value in TIMEZONE_CHOICES:
        # You can localize the label if needed. Here, we use the same label.
        tz_btn = types.InlineKeyboardButton(text=label, callback_data=f"set_tz_{tz_value}")
        tz_markup.add(tz_btn)
    bot.send_message(call.message.chat.id, MESSAGES[lang]['select_timezone'], reply_markup=tz_markup)

# -------------------------------
# Time Zone Selection Callback Handler
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_tz_"))
def timezone_callback_handler(call):
    user_id = call.from_user.id
    if user_id not in user_states:
        return
    tz_value = call.data.split("set_tz_")[1]
    # Update user's timezone in DB.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET timezone = ? WHERE user_id = ?", (tz_value, user_id))
    conn.commit()
    conn.close()

    user_states[user_id]['data']['timezone'] = tz_value
    user_states[user_id]['state'] = STATE_SUMMARY_SCHEDULE
    lang = user_states[user_id]['data'].get('language', 'en')
    bot.answer_callback_query(call.id, MESSAGES[lang]['set_timezone'].format(tz_value))
    
    # Send inline keyboard for summary schedule selection.
    summary_markup = types.InlineKeyboardMarkup()
    btn_daily = types.InlineKeyboardButton(text=("Daily" if lang == 'en' else "روزانه"), callback_data="set_summary_daily")
    btn_custom = types.InlineKeyboardButton(text=("Every X hours" if lang == 'en' else "هر X ساعت"), callback_data="set_summary_custom")
    btn_none = types.InlineKeyboardButton(text=("None" if lang == 'en' else "هیچ"), callback_data="set_summary_none")
    summary_markup.add(btn_daily, btn_custom, btn_none)
    bot.send_message(call.message.chat.id, MESSAGES[lang]['select_summary'], reply_markup=summary_markup)

# -------------------------------
# Summary Schedule Callback Handler
# (Handles summary schedule selection)
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_summary_"))
def summary_callback_handler(call):
    user_id = call.from_user.id
    if user_id not in user_states:
        return
    lang = user_states[user_id]['data'].get('language', 'en')
    current_state = user_states[user_id]['state']
    if current_state != STATE_SUMMARY_SCHEDULE:
        return
    selection = call.data.split("set_summary_")[1]
    if selection == "daily":
        user_states[user_id]['data']['summary_schedule'] = 'daily'
        user_states[user_id]['state'] = STATE_SUMMARY_TIME
        bot.answer_callback_query(call.id, "Daily summary selected")
        bot.send_message(call.message.chat.id, MESSAGES[lang]['enter_daily_time'])
    elif selection == "custom":
        user_states[user_id]['data']['summary_schedule'] = 'custom'
        user_states[user_id]['state'] = STATE_SUMMARY_TIME
        bot.answer_callback_query(call.id, "Custom summary interval selected")
        bot.send_message(call.message.chat.id, MESSAGES[lang]['enter_custom_interval'])
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
        bot.send_message(call.message.chat.id, MESSAGES[lang]['enter_random_checkins'])
    else:
        bot.answer_callback_query(call.id, "Unhandled summary callback.")

# -------------------------------
# Onboarding Text Message Handler (for summary time and random check-ins)
# -------------------------------
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') in [STATE_SUMMARY_TIME, STATE_RANDOM_CHECKIN])
def onboarding_message_handler(message):
    user_id = message.from_user.id
    current_state = user_states[user_id]['state']
    text = message.text.strip()
    lang = user_states[user_id]['data'].get('language', 'en')

    if current_state == STATE_SUMMARY_TIME:
        summary_schedule = user_states[user_id]['data'].get('summary_schedule')
        if summary_schedule == 'daily':
            try:
                datetime.strptime(text, "%H:%M")  # Validate format.
                # Update DB.
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET summary_schedule = ?, summary_time = ? WHERE user_id = ?", ('daily', text, user_id))
                conn.commit()
                conn.close()
                user_states[user_id]['data']['summary_time'] = text
                user_states[user_id]['state'] = STATE_RANDOM_CHECKIN
                bot.send_message(message.chat.id, f"{MESSAGES[lang]['enter_random_checkins']}")
            except ValueError:
                bot.send_message(message.chat.id, MESSAGES[lang]['enter_daily_time'])
        elif summary_schedule == 'custom':
            if text.isdigit():
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET summary_schedule = ?, summary_time = ? WHERE user_id = ?", ('custom', text, user_id))
                conn.commit()
                conn.close()
                user_states[user_id]['data']['summary_time'] = text
                user_states[user_id]['state'] = STATE_RANDOM_CHECKIN
                bot.send_message(message.chat.id, MESSAGES[lang]['enter_random_checkins'])
            else:
                bot.send_message(message.chat.id, MESSAGES[lang]['enter_custom_interval'])
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
            bot.send_message(message.chat.id, MESSAGES[lang]['onboarding_complete'])
            # Show Main Menu.
            from modules.menu import send_main_menu
            send_main_menu(bot, message.chat.id)
        else:
            bot.send_message(message.chat.id, MESSAGES[lang]['enter_random_checkins'])

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
# (For now, the "View Summary" menu option calls send_summary.)

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
        send_summary(bot, chat_id, user_id)
    elif data == "menu_manage_items":
        bot.send_message(chat_id, "You selected Manage Items. [Placeholder for items management module]")
    elif data == "menu_quotes":
        start_add_quote(bot, chat_id, user_id)
    elif data == "menu_settings":
        bot.send_message(chat_id, "You selected Settings. [Placeholder for settings module]")
    else:
        bot.send_message(chat_id, "Unknown menu option selected.")

# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == "__main__":
    init_db()
    print("Bot is running...")
    bot.infinity_polling()