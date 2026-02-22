"""
bot.py

This is the main entry point for the bot. It integrates:
  - Onboarding (multilingual language selection, detailed onboarding info, time zone selection via inline buttons, summary schedule, random check-in)
  - Main Menu & Navigation
  - Tasks Module
  - Goals Module
  - Reminders Module
  - Countdowns Module
  - Weekly Schedule Module
  - Random Check-Ins Module
  - Summaries & Reports Module
  - Quotes Module
  - Help Command (brief instructions with emojis)
  - Info Command (deep, detailed explanation of every action, button, and input)
  - Manage Items (view and delete tasks, reminders, goals, countdowns)
  - Settings (change language and timezone)

Ensure that the following modules/files are available:
  - database.py
  - modules/menu.py
  - modules/tasks.py
  - modules/goals.py
  - modules/reminders.py
  - modules/countdowns.py
  - modules/weekly_schedule.py
  - modules/random_checkins.py
  - modules/summaries.py
  - modules/quotes.py
  - modules/date_conversion.py

Replace "YOUR_TELEGRAM_BOT_TOKEN" with your actual bot token.

Revisions in this file:
  - All messages sent as part of multi‐step flows now use tracked_send_message.
  - All user-sent messages that are part of these flows are tracked via tracked_user_message.
  - The clear_flow_messages function now attempts to delete both bot and user messages.
  - Logging was added to aid in debugging message deletions.
  - **New:** Integration of scheduler.py functions during onboarding to schedule summary reports, random check-ins, and due/upcoming summaries.
  - **New:** When scheduling jobs, the user's chosen timezone (from the bot) is passed into the scheduler functions.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import telebot
from telebot import types
from datetime import datetime, timedelta
import logging
from messages import MESSAGES

# Setup basic logging for debugging flow cleanup.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database import get_db_connection, init_db
from modules.weekly_schedule import start_add_weekly_event, weekly_states
from flow_helpers import tracked_send_message, tracked_user_message, clear_flow_messages, set_bot

# Import scheduler functions from scheduler.py
from scheduler import (
    init_scheduler,
    schedule_reminder,
    schedule_summary,
    schedule_random_checkins,
    schedule_weekly_event_reminders,
    schedule_nightly_tomorrow_summary,
    schedule_due_and_upcoming_summary
)

# -------------------------------
# Global Flow Tracking & State Definitions
# -------------------------------
STATE_LANGUAGE = "language"
STATE_TIMEZONE = "timezone"      # Handled via inline buttons
STATE_SUMMARY_SCHEDULE = "summary_schedule"
STATE_SUMMARY_TIME = "summary_time"   # For daily time (HH:MM) or custom interval (in hours)
STATE_RANDOM_CHECKIN = "random_checkin"
STATE_COMPLETED = "completed"
user_states = {}  # Global dictionary to store onboarding conversation state per user.

# -------------------------------
# Bot Initialization
# -------------------------------
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Replace with your actual token.
bot = telebot.TeleBot(BOT_TOKEN)
set_bot(bot)

# Start the scheduler in the background.
init_scheduler()

# -------------------------------
# Helper Function: Schedule All Jobs for a User
# -------------------------------
# ... [imports and other code above unchanged] ...

# -------------------------------
# Helper Function: Schedule All Jobs for a User
# -------------------------------
def schedule_all_jobs(bot, user_id, chat_id):
    """
    Reads the user settings from the database and schedules:
      - Summary messages (daily or custom)
      - Random check-ins (if set)
      - Due/upcoming summary (every 30 minutes)
      - Nightly summary at 21:00
      - Weekly event reminders
    The user's timezone is also retrieved and passed to the scheduler functions.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT summary_schedule, summary_time, random_checkin_max, timezone FROM users WHERE user_id = ?",
        (user_id,)
    )
    user_settings = cursor.fetchone()
    conn.close()
    if not user_settings:
        return

    # Convert the sqlite3.Row to a dict so that we can use .get()
    user_settings = dict(user_settings)
    summary_schedule = user_settings.get("summary_schedule")
    summary_time = user_settings.get("summary_time")
    random_checkin_max = user_settings.get("random_checkin_max")
    user_tz = user_settings.get("timezone", "UTC")

    if summary_schedule in ("daily", "custom"):
        schedule_summary(bot, user_id, chat_id, summary_schedule, summary_time, user_tz)
    if random_checkin_max and int(random_checkin_max) > 0:
        schedule_random_checkins(bot, user_id, chat_id, int(random_checkin_max), user_tz)
    schedule_due_and_upcoming_summary(bot, user_id, chat_id, user_tz)
    schedule_nightly_tomorrow_summary(bot, user_id, chat_id, user_tz)
    schedule_weekly_event_reminders(bot, user_id, chat_id, user_tz)

# ... [rest of your bot.py remains unchanged] ...

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
# Weekly Schedule Handlers
# -------------------------------
@bot.message_handler(func=lambda message: message.from_user.id in weekly_states)
def message_weekly_handler(message):
    from modules.weekly_schedule import handle_weekly_event_messages
    user_lang = weekly_states.get(message.from_user.id, {}).get('data', {}).get('language', 'en')
    handle_weekly_event_messages(bot, message, user_lang=user_lang)

@bot.callback_query_handler(func=lambda call: call.data.startswith("week_day_"))
def weekly_callback_handler(call):
    from modules.weekly_schedule import handle_weekly_event_callbacks
    handle_weekly_event_callbacks(bot, call)

# -------------------------------
# /start Command Handler & Pre-Onboarding Flow
# -------------------------------
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
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
    # (Optionally, you could schedule jobs for returning users here.)
    user_states[user_id] = {'state': STATE_LANGUAGE, 'data': {}}
    markup = types.InlineKeyboardMarkup()
    btn_english = types.InlineKeyboardButton(text="English", callback_data="set_lang_en")
    btn_farsi = types.InlineKeyboardButton(text="فارسی", callback_data="set_lang_fa")
    markup.add(btn_english, btn_farsi)
    tracked_send_message(message.chat.id, user_id, MESSAGES['en']['welcome'], reply_markup=markup)

# -------------------------------
# /help and /info Command Handlers
# -------------------------------
@bot.message_handler(commands=['help'])
def handle_help(message):
    user_id = message.from_user.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    bot.send_message(message.chat.id, MESSAGES[lang]['help'], parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def handle_info(message):
    user_id = message.from_user.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    bot.send_message(message.chat.id, MESSAGES[lang]['info'], parse_mode="Markdown")

# -------------------------------
# Language Selection Callback Handler
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def language_callback_handler(call):
    user_id = call.from_user.id
    if user_id not in user_states:
        return
    selected_lang = call.data.split("set_lang_")[1]  # "en" or "fa"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (selected_lang, user_id))
    conn.commit()
    conn.close()
    user_states[user_id]['data']['language'] = selected_lang
    help_msg = MESSAGES[selected_lang]['onboard_info']
    markup = types.InlineKeyboardMarkup()
    btn_continue = types.InlineKeyboardButton(text=MESSAGES[selected_lang]['onboard_continue'], callback_data="onboard_continue")
    markup.add(btn_continue)
    tracked_send_message(call.message.chat.id, user_id, help_msg, reply_markup=markup)
    bot.answer_callback_query(call.id, "Language set.")

# -------------------------------
# Onboard Continue Callback Handler
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "onboard_continue")
def onboard_continue_handler(call):
    user_id = call.from_user.id
    lang = user_states[user_id]['data'].get('language', 'en')
    clear_flow_messages(call.message.chat.id, user_id)
    user_states[user_id]['state'] = STATE_TIMEZONE
    tz_markup = types.InlineKeyboardMarkup(row_width=2)
    for label, tz_value in TIMEZONE_CHOICES:
        tz_btn = types.InlineKeyboardButton(text=label, callback_data=f"set_tz_{tz_value}")
        tz_markup.add(tz_btn)
    tracked_send_message(call.message.chat.id, user_id, MESSAGES[lang]['select_timezone'], reply_markup=tz_markup)
    bot.answer_callback_query(call.id, "")

# -------------------------------
# Time Zone Selection Callback Handler
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_tz_"))
def timezone_callback_handler(call):
    user_id = call.from_user.id
    if user_id not in user_states:
        return
    tz_value = call.data.split("set_tz_")[1]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET timezone = ? WHERE user_id = ?", (tz_value, user_id))
    conn.commit()
    conn.close()
    user_states[user_id]['data']['timezone'] = tz_value
    user_states[user_id]['state'] = STATE_SUMMARY_SCHEDULE
    lang = user_states[user_id]['data'].get('language', 'en')
    bot.answer_callback_query(call.id, MESSAGES[lang]['set_timezone'].format(tz_value))
    summary_markup = types.InlineKeyboardMarkup()
    btn_daily = types.InlineKeyboardButton(text=MESSAGES[lang].get('summary_daily', "Daily"), callback_data="set_summary_daily")
    btn_custom = types.InlineKeyboardButton(text=MESSAGES[lang].get('summary_custom', "Every X hours"), callback_data="set_summary_custom")
    btn_none = types.InlineKeyboardButton(text=MESSAGES[lang].get('summary_none', "None"), callback_data="set_summary_none")
    summary_markup.add(btn_daily, btn_custom, btn_none)
    tracked_send_message(call.message.chat.id, user_id, MESSAGES[lang]['select_summary'], reply_markup=summary_markup)

# -------------------------------
# Summary Schedule Callback Handler
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_summary_"))
def summary_callback_handler(call):
    user_id = call.from_user.id
    if user_id not in user_states:
        return
    lang = user_states[user_id]['data'].get('language', 'en')
    if user_states[user_id]['state'] != STATE_SUMMARY_SCHEDULE:
        return
    selection = call.data.split("set_summary_")[1]
    if selection == "daily":
        user_states[user_id]['data']['summary_schedule'] = 'daily'
        user_states[user_id]['state'] = STATE_SUMMARY_TIME
        bot.answer_callback_query(call.id, "Daily summary selected.")
        tracked_send_message(call.message.chat.id, user_id, MESSAGES[lang]['enter_daily_time'])
    elif selection == "custom":
        user_states[user_id]['data']['summary_schedule'] = 'custom'
        user_states[user_id]['state'] = STATE_SUMMARY_TIME
        bot.answer_callback_query(call.id, "Custom summary interval selected.")
        tracked_send_message(call.message.chat.id, user_id, MESSAGES[lang]['enter_custom_interval'])
    elif selection == "none":
        user_states[user_id]['data']['summary_schedule'] = 'disabled'
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET summary_schedule = ? WHERE user_id = ?", ('disabled', user_id))
        conn.commit()
        conn.close()
        user_states[user_id]['state'] = STATE_RANDOM_CHECKIN
        bot.answer_callback_query(call.id, "No summary will be sent.")
        tracked_send_message(call.message.chat.id, user_id, MESSAGES[lang]['enter_random_checkins'])
    else:
        bot.answer_callback_query(call.id, "Unhandled summary callback.")

# -------------------------------
# Onboarding Text Message Handler (for summary time and random check-ins)
# -------------------------------
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') in [STATE_SUMMARY_TIME, STATE_RANDOM_CHECKIN])
def onboarding_message_handler(message):
    user_id = message.from_user.id
    tracked_user_message(message)
    current_state = user_states[user_id]['state']
    text = message.text.strip()
    lang = user_states[user_id]['data'].get('language', 'en')
    if current_state == STATE_SUMMARY_TIME:
        summary_schedule = user_states[user_id]['data'].get('summary_schedule')
        if summary_schedule == 'daily':
            try:
                datetime.strptime(text, "%H:%M")
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET summary_schedule = ?, summary_time = ? WHERE user_id = ?", ('daily', text, user_id))
                conn.commit()
                conn.close()
                user_states[user_id]['data']['summary_time'] = text
                user_states[user_id]['state'] = STATE_RANDOM_CHECKIN
                tracked_send_message(message.chat.id, user_id, MESSAGES[lang]['enter_random_checkins'])
            except ValueError:
                tracked_send_message(message.chat.id, user_id, MESSAGES[lang]['enter_daily_time'])
        elif summary_schedule == 'custom':
            if text.isdigit():
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET summary_schedule = ?, summary_time = ? WHERE user_id = ?", ('custom', text, user_id))
                conn.commit()
                conn.close()
                user_states[user_id]['data']['summary_time'] = text
                user_states[user_id]['state'] = STATE_RANDOM_CHECKIN
                tracked_send_message(message.chat.id, user_id, MESSAGES[lang]['enter_random_checkins'])
            else:
                tracked_send_message(message.chat.id, user_id, MESSAGES[lang]['enter_custom_interval'])
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
            clear_flow_messages(message.chat.id, user_id)
            bot.send_message(message.chat.id, MESSAGES[lang]['onboarding_complete'])
            # --- NEW: Schedule user-specific jobs based on onboarding settings ---
            schedule_all_jobs(bot, user_id, message.chat.id)
            from modules.menu import send_main_menu
            send_main_menu(bot, message.chat.id, lang)
        else:
            tracked_send_message(message.chat.id, user_id, MESSAGES[lang]['enter_random_checkins'])

# -------------------------------
# Integration: Tasks Module
# -------------------------------
from modules.tasks import start_add_task, handle_task_callbacks, handle_task_messages, tasks_states

@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def callback_task_handler(call):
    handle_task_callbacks(bot, call)

@bot.message_handler(func=lambda message: message.from_user.id in tasks_states)
def message_task_handler(message):
    handle_task_messages(bot, message)

# -------------------------------
# Integration: Goals Module
# -------------------------------
from modules.goals import start_add_goal, handle_goal_callbacks, handle_goal_messages, goals_states

@bot.callback_query_handler(func=lambda call: call.data.startswith("goal_freq_"))
def callback_goal_handler(call):
    handle_goal_callbacks(bot, call)

@bot.message_handler(func=lambda message: message.from_user.id in goals_states)
def message_goal_handler(message):
    handle_goal_messages(bot, message)

# -------------------------------
# Integration: Reminders Module
# -------------------------------
from modules.reminders import start_add_reminder, handle_reminder_callbacks, handle_reminder_messages, reminders_states

@bot.callback_query_handler(func=lambda call: call.data.startswith("rem_"))
def callback_reminder_handler(call):
    handle_reminder_callbacks(bot, call)

@bot.message_handler(func=lambda message: message.from_user.id in reminders_states)
def message_reminder_handler(message):
    handle_reminder_messages(bot, message)

# -------------------------------
# Integration: Countdowns Module
# -------------------------------
from modules.countdowns import start_add_countdown, handle_countdown_messages, handle_countdown_callbacks, countdowns_states

@bot.callback_query_handler(func=lambda call: call.data.startswith("countdown_notify_"))
def callback_countdown_handler(call):
    handle_countdown_callbacks(bot, call)

@bot.message_handler(func=lambda message: message.from_user.id in countdowns_states)
def message_countdown_handler(message):
    handle_countdown_messages(bot, message)

# -------------------------------
# Integration: Random Check-Ins Module
# -------------------------------
from modules.random_checkins import send_random_checkin, handle_random_checkin_callback, schedule_daily_checkins

@bot.callback_query_handler(func=lambda call: call.data.startswith("random_"))
def callback_random_handler(call):
    handle_random_checkin_callback(bot, call)

# -------------------------------
# Integration: Summaries & Reports Module
# -------------------------------
from modules.summaries import send_summary, generate_summary
# (For now, the "View Summary" menu option calls send_summary.)

# -------------------------------
# Integration: Quotes Module
# -------------------------------
from modules.quotes import start_add_quote, handle_quote_messages, quotes_states, get_random_quote

@bot.message_handler(func=lambda message: message.from_user.id in quotes_states)
def message_quote_handler(message):
    handle_quote_messages(bot, message)

# -------------------------------
# Additional Utility: Manage Items Menu
# -------------------------------
def manage_items_menu(bot, chat_id, user_id):
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    markup = types.InlineKeyboardMarkup()
    btn_tasks = types.InlineKeyboardButton(text=MESSAGES[lang].get('manage_tasks', "Manage Tasks"), callback_data="manage_tasks")
    btn_reminders = types.InlineKeyboardButton(text=MESSAGES[lang].get('manage_reminders', "Manage Reminders"), callback_data="manage_reminders")
    btn_goals = types.InlineKeyboardButton(text=MESSAGES[lang].get('manage_goals', "Manage Goals"), callback_data="manage_goals")
    btn_countdowns = types.InlineKeyboardButton(text=MESSAGES[lang].get('manage_countdowns', "Manage Countdowns"), callback_data="manage_countdowns")
    btn_back = types.InlineKeyboardButton(text=MESSAGES[lang].get('back_to_main_menu', "Back to Main Menu"), callback_data="back_main")
    markup.row(btn_tasks, btn_reminders)
    markup.row(btn_goals, btn_countdowns)
    markup.add(btn_back)
    tracked_send_message(chat_id, user_id, MESSAGES[lang].get('manage_items_menu', "Manage Items:\nSelect a category to view and delete items:"), reply_markup=markup)

def manage_tasks(bot, chat_id, user_id):
    from modules.tasks import list_tasks, delete_task
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    tasks = list_tasks(user_id)
    if not tasks:
        bot.send_message(chat_id, MESSAGES[lang].get('no_tasks_found', "No tasks found."))
        return
    for task in tasks:
        task_id = task["id"]
        title = task["title"]
        due = task["due_date"] if task["due_date"] else "No due date"
        markup = types.InlineKeyboardMarkup()
        btn_delete = types.InlineKeyboardButton(text="Delete 🗑", callback_data=f"delete_task_{task_id}")
        markup.add(btn_delete)
        bot.send_message(chat_id, f"Task: {title}\nDue: {due}", reply_markup=markup)

def manage_reminders(bot, chat_id, user_id):
    from modules.reminders import list_reminders, delete_reminder
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    reminders = list_reminders(user_id)
    if not reminders:
        bot.send_message(chat_id, MESSAGES[lang].get('no_reminders_found', "No reminders found."))
        return
    for rem in reminders:
        rem_id = rem["id"]
        title = rem["title"]
        trigger = rem["next_trigger_time"]
        markup = types.InlineKeyboardMarkup()
        btn_delete = types.InlineKeyboardButton(text="Delete 🗑", callback_data=f"delete_reminder_{rem_id}")
        markup.add(btn_delete)
        bot.send_message(chat_id, f"Reminder: {title}\nNext: {trigger}", reply_markup=markup)

def manage_goals(bot, chat_id, user_id):
    from modules.goals import list_goals, delete_goal
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    goals = list_goals(user_id)
    if not goals:
        bot.send_message(chat_id, MESSAGES[lang].get('no_goals_found', "No goals found."))
        return
    for goal in goals:
        goal_id = goal["id"]
        title = goal["title"]
        markup = types.InlineKeyboardMarkup()
        btn_delete = types.InlineKeyboardButton(text="Delete 🗑", callback_data=f"delete_goal_{goal_id}")
        markup.add(btn_delete)
        bot.send_message(chat_id, f"Goal: {title}", reply_markup=markup)

def manage_countdowns(bot, chat_id, user_id):
    from modules.countdowns import list_countdowns, delete_countdown
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    countdowns = list_countdowns(user_id)
    if not countdowns:
        bot.send_message(chat_id, MESSAGES[lang].get('no_countdowns_found', "No countdowns found."))
        return
    for cd in countdowns:
        cd_id = cd["id"]
        title = cd["title"]
        event_time = cd["event_datetime"]
        markup = types.InlineKeyboardMarkup()
        btn_delete = types.InlineKeyboardButton(text="Delete 🗑", callback_data=f"delete_countdown_{cd_id}")
        markup.add(btn_delete)
        bot.send_message(chat_id, f"Countdown: {title}\nEvent: {event_time}", reply_markup=markup)

# -------------------------------
# Additional Utility: Settings Menu
# -------------------------------
def settings_menu(bot, chat_id, user_id):
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    markup = types.InlineKeyboardMarkup()
    btn_change_lang = types.InlineKeyboardButton(
        text=MESSAGES[lang].get('change_language', "Change Language"),
        callback_data="settings_change_lang"
    )
    btn_change_tz = types.InlineKeyboardButton(
        text=MESSAGES[lang].get('change_timezone', "Change Timezone"),
        callback_data="settings_change_tz"
    )
    btn_back = types.InlineKeyboardButton(
        text=MESSAGES[lang].get('back_to_main_menu', "Back to Main Menu"),
        callback_data="back_main"
    )
    markup.row(btn_change_lang, btn_change_tz)
    markup.add(btn_back)
    tracked_send_message(chat_id, user_id, MESSAGES[lang].get('settings', "Settings:"), reply_markup=markup)

# -------------------------------
# Callback Handlers for Manage Items and Settings
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("manage_") or call.data in ["back_main", "settings_change_lang", "settings_change_tz"])
def manage_callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    if data == "manage_tasks":
        manage_tasks(bot, chat_id, user_id)
    elif data == "manage_reminders":
        manage_reminders(bot, chat_id, user_id)
    elif data == "manage_goals":
        manage_goals(bot, chat_id, user_id)
    elif data == "manage_countdowns":
        manage_countdowns(bot, chat_id, user_id)
    elif data == "back_main":
        from modules.menu import send_main_menu
        send_main_menu(bot, chat_id, lang)
    elif data == "settings_change_lang":
        user_states[user_id]['state'] = STATE_LANGUAGE
        markup = types.InlineKeyboardMarkup()
        btn_english = types.InlineKeyboardButton(text="English", callback_data="set_lang_en")
        btn_farsi = types.InlineKeyboardButton(text="فارسی", callback_data="set_lang_fa")
        markup.add(btn_english, btn_farsi)
        tracked_send_message(chat_id, user_id, MESSAGES[lang].get('select_language', "Please select your language:"), reply_markup=markup)
    elif data == "settings_change_tz":
        user_states[user_id]['state'] = STATE_TIMEZONE
        tz_markup = types.InlineKeyboardMarkup(row_width=2)
        for label, tz_value in TIMEZONE_CHOICES:
            tz_btn = types.InlineKeyboardButton(text=label, callback_data=f"set_tz_{tz_value}")
            tz_markup.add(tz_btn)
        tracked_send_message(chat_id, user_id, MESSAGES[lang].get('select_timezone', "Please select your timezone:"), reply_markup=tz_markup)
    else:
        bot.answer_callback_query(call.id, MESSAGES[lang].get('unknown_menu_option', "Unknown menu option selected."))

# -------------------------------
# Callback Handlers for Deletion Actions
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_task_"))
def delete_task_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    task_id = int(call.data.split("delete_task_")[1])
    from modules.tasks import delete_task
    delete_task(user_id, task_id)
    bot.answer_callback_query(call.id, MESSAGES[lang].get('task_deleted', "Task deleted."))
    bot.send_message(chat_id, MESSAGES[lang].get('task_deleted_confirmation', "Task has been deleted."))
    clear_flow_messages(chat_id, user_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_reminder_"))
def delete_reminder_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    rem_id = int(call.data.split("delete_reminder_")[1])
    from modules.reminders import delete_reminder
    delete_reminder(user_id, rem_id)
    bot.answer_callback_query(call.id, MESSAGES[lang].get('reminder_deleted', "Reminder deleted."))
    bot.send_message(chat_id, MESSAGES[lang].get('reminder_deleted_confirmation', "Reminder has been deleted."))
    clear_flow_messages(chat_id, user_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_goal_"))
def delete_goal_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    goal_id = int(call.data.split("delete_goal_")[1])
    from modules.goals import delete_goal
    delete_goal(user_id, goal_id)
    bot.answer_callback_query(call.id, MESSAGES[lang].get('goal_deleted', "Goal deleted."))
    bot.send_message(chat_id, MESSAGES[lang].get('goal_deleted_confirmation', "Goal has been deleted."))
    clear_flow_messages(chat_id, user_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_countdown_"))
def delete_countdown_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    cd_id = int(call.data.split("delete_countdown_")[1])
    from modules.countdowns import delete_countdown
    delete_countdown(user_id, cd_id)
    bot.answer_callback_query(call.id, MESSAGES[lang].get('countdown_deleted', "Countdown deleted."))
    bot.send_message(chat_id, MESSAGES[lang].get('countdown_deleted_confirmation', "Countdown has been deleted."))
    clear_flow_messages(chat_id, user_id)

# -------------------------------
# Integration: Weekly Schedule Module
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_weekly_schedule"))
def callback_weekly_schedule_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    from modules.weekly_schedule import start_add_weekly_event
    start_add_weekly_event(bot, chat_id, user_id, user_lang=user_states[user_id]['data'].get('language', 'en'))

# -------------------------------
# Integration: Main Menu Selections
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def callback_menu_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    if data == "menu_add_task":
        from modules.tasks import start_add_task
        start_add_task(bot, chat_id, user_id)
    elif data == "menu_add_goal":
        from modules.goals import start_add_goal
        start_add_goal(bot, chat_id, user_id)
    elif data == "menu_add_reminder":
        from modules.reminders import start_add_reminder
        start_add_reminder(bot, chat_id, user_id)
    elif data == "menu_add_countdown":
        from modules.countdowns import start_add_countdown
        start_add_countdown(bot, chat_id, user_id)
    elif data == "menu_weekly_schedule":
        from modules.weekly_schedule import start_add_weekly_event
        start_add_weekly_event(bot, chat_id, user_id, user_lang=lang)
    elif data == "menu_view_summary":
        from modules.summaries import send_summary
        send_summary(bot, chat_id, user_id, lang)
    elif data == "menu_manage_items":
        manage_items_menu(bot, chat_id, user_id)
    elif data == "menu_quotes":
        from modules.quotes import start_add_quote
        start_add_quote(bot, chat_id, user_id)
    elif data == "menu_settings":
        settings_menu(bot, chat_id, user_id)
    else:
        bot.send_message(chat_id, MESSAGES[lang].get('unknown_menu_option', "Unknown menu option selected."))

# -------------------------------
# Integration: Main Menu from modules/menu.py
# -------------------------------
from modules.menu import send_main_menu

# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == "__main__":
    init_db()
    print("Bot is running...")
    bot.infinity_polling()
