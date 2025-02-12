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
  - All messages sent as part of multi‐step flows (onboarding, summary schedule, etc.) now use tracked_send_message.
  - In addition, all user-sent messages that are part of these flows are tracked via tracked_user_message.
  - The clear_flow_messages function now attempts to delete both bot and user messages.
  - Logging was added to aid in debugging message deletions.
"""

import telebot
from telebot import types
from datetime import datetime
import logging
from messages import MESSAGES

# Setup basic logging for debugging flow cleanup.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database import get_db_connection, init_db
from modules.weekly_schedule import start_add_weekly_event, weekly_states
# Old line (to be removed):
# from bot import tracked_send_message, tracked_user_message, clear_flow_messages

# New import:
from flow_helpers import tracked_send_message, tracked_user_message, clear_flow_messages, set_bot

# -------------------------------
# Global Flow Tracking
# -------------------------------

# -------------------------------
# Bot Initialization
# -------------------------------
BOT_TOKEN = "7993339613:AAH2wXp3RKqIPoZssPvtbHvzKleu5yVbDzQ"
bot = telebot.TeleBot(BOT_TOKEN)
set_bot(bot)



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
STATE_TIMEZONE = "timezone"      # Handled via inline buttons
STATE_SUMMARY_SCHEDULE = "summary_schedule"
STATE_SUMMARY_TIME = "summary_time"   # For daily time (HH:MM) or custom interval (in hours)
STATE_RANDOM_CHECKIN = "random_checkin"
STATE_COMPLETED = "completed"
user_states = {}  # Global dictionary to store onboarding conversation state per user.

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
    user_states[user_id] = {'state': STATE_LANGUAGE, 'data': {}}
    # Prompt for language selection using tracked_send_message.
    markup = types.InlineKeyboardMarkup()
    btn_english = types.InlineKeyboardButton(text="English", callback_data="set_lang_en")
    btn_farsi = types.InlineKeyboardButton(text="فارسی", callback_data="set_lang_fa")
    markup.add(btn_english, btn_farsi)
    # Since language isn't set yet, we use the English welcome message.
    tracked_send_message(message.chat.id, user_id, MESSAGES['en']['welcome'], reply_markup=markup)

# -------------------------------
# /help Command Handler
# -------------------------------
@bot.message_handler(commands=['help'])
def handle_help(message):
    user_id = message.from_user.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    help_text = MESSAGES[lang]['help']
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# -------------------------------
# /info Command Handler
# -------------------------------
@bot.message_handler(commands=['info'])
def handle_info(message):
    user_id = message.from_user.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    info_text = MESSAGES[lang]['info']
    bot.send_message(message.chat.id, info_text, parse_mode="Markdown")

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
    # Send the detailed onboarding info message using tracked_send_message.
    help_msg = MESSAGES[selected_lang]['onboard_info']
    markup = types.InlineKeyboardMarkup()
    btn_continue = types.InlineKeyboardButton(text=MESSAGES[selected_lang]['onboard_continue'], callback_data="onboard_continue")
    markup.add(btn_continue)
    tracked_send_message(call.message.chat.id, user_id, help_msg, reply_markup=markup)
    localized_text = MESSAGES[selected_lang]['language_set'].format(selected_lang)
    bot.answer_callback_query(call.id, localized_text)

# -------------------------------
# Onboard Continue Callback Handler
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "onboard_continue")
def onboard_continue_handler(call):
    user_id = call.from_user.id
    lang = user_states[user_id]['data'].get('language', 'en')
    # Before continuing, clear all tracked flow messages (bot & user).
    clear_flow_messages(call.message.chat.id, user_id)
    # Continue with onboarding: set state to TIMEZONE and show timezone options.
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
    btn_daily = types.InlineKeyboardButton(text=MESSAGES[lang]['summary_daily'], callback_data="set_summary_daily")
    btn_custom = types.InlineKeyboardButton(text=MESSAGES[lang]['summary_custom'], callback_data="set_summary_custom")
    btn_none = types.InlineKeyboardButton(text=MESSAGES[lang]['summary_none'], callback_data="set_summary_none")
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
        bot.answer_callback_query(call.id, MESSAGES[lang]['daily_summary_selected'])
        tracked_send_message(call.message.chat.id, user_id, MESSAGES[lang]['enter_daily_time'])
    elif selection == "custom":
        user_states[user_id]['data']['summary_schedule'] = 'custom'
        user_states[user_id]['state'] = STATE_SUMMARY_TIME
        bot.answer_callback_query(call.id, MESSAGES[lang]['custom_summary_interval_selected'])
        tracked_send_message(call.message.chat.id, user_id, MESSAGES[lang]['enter_custom_interval'])
    elif selection == "none":
        user_states[user_id]['data']['summary_schedule'] = 'disabled'
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET summary_schedule = ? WHERE user_id = ?", ('disabled', user_id))
        conn.commit()
        conn.close()
        user_states[user_id]['state'] = STATE_RANDOM_CHECKIN
        bot.answer_callback_query(call.id, MESSAGES[lang]['no_summary_will_be_sent'])
        tracked_send_message(call.message.chat.id, user_id, MESSAGES[lang]['enter_random_checkins'])
    else:
        bot.answer_callback_query(call.id, "Unhandled summary callback.")

# -------------------------------
# Onboarding Text Message Handler (for summary time and random check-ins)
# -------------------------------
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') in [STATE_SUMMARY_TIME, STATE_RANDOM_CHECKIN])
def onboarding_message_handler(message):
    user_id = message.from_user.id
    # Track the user-sent message as part of the flow.
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
            # Clear all flow messages (both bot and user) before showing main menu.
            clear_flow_messages(message.chat.id, user_id)
            bot.send_message(message.chat.id, MESSAGES[lang]['onboarding_complete'])
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
    btn_tasks = types.InlineKeyboardButton(text="Manage Tasks", callback_data="manage_tasks")
    btn_reminders = types.InlineKeyboardButton(text="Manage Reminders", callback_data="manage_reminders")
    btn_goals = types.InlineKeyboardButton(text="Manage Goals", callback_data="manage_goals")
    btn_countdowns = types.InlineKeyboardButton(text="Manage Countdowns", callback_data="manage_countdowns")
    btn_back = types.InlineKeyboardButton(text=MESSAGES[lang]['back_to_main_menu'], callback_data="back_main")
    markup.row(btn_tasks, btn_reminders)
    markup.row(btn_goals, btn_countdowns)
    markup.add(btn_back)
    bot.send_message(chat_id, MESSAGES[lang]['manage_items_menu'], reply_markup=markup)

def manage_tasks(bot, chat_id, user_id):
    from modules.tasks import list_tasks, delete_task
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    tasks = list_tasks(user_id)
    if not tasks:
        bot.send_message(chat_id, MESSAGES[lang]['no_tasks_found'])
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
        bot.send_message(chat_id, MESSAGES[lang]['no_reminders_found'])
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
        bot.send_message(chat_id, MESSAGES[lang]['no_goals_found'])
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
        bot.send_message(chat_id, MESSAGES[lang]['no_countdowns_found'])
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
    btn_change_lang = types.InlineKeyboardButton(text="Change Language", callback_data="settings_change_lang")
    btn_change_tz = types.InlineKeyboardButton(text="Change Timezone", callback_data="settings_change_tz")
    btn_back = types.InlineKeyboardButton(text=MESSAGES[lang]['back_to_main_menu'], callback_data="back_main")
    markup.row(btn_change_lang, btn_change_tz)
    markup.add(btn_back)
    bot.send_message(chat_id, MESSAGES[lang]['settings'], reply_markup=markup)

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
        bot.send_message(chat_id, MESSAGES[lang]['select_language'], reply_markup=markup)
    elif data == "settings_change_tz":
        user_states[user_id]['state'] = STATE_TIMEZONE
        tz_markup = types.InlineKeyboardMarkup(row_width=2)
        for label, tz_value in TIMEZONE_CHOICES:
            tz_btn = types.InlineKeyboardButton(text=label, callback_data=f"set_tz_{tz_value}")
            tz_markup.add(tz_btn)
        bot.send_message(chat_id, MESSAGES[lang]['select_timezone'], reply_markup=tz_markup)
    else:
        bot.answer_callback_query(call.id, MESSAGES[lang]['unknown_menu_option'])

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
    bot.answer_callback_query(call.id, MESSAGES[lang]['task_deleted'])
    bot.send_message(chat_id, MESSAGES[lang]['task_deleted_confirmation'])

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_reminder_"))
def delete_reminder_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    rem_id = int(call.data.split("delete_reminder_")[1])
    from modules.reminders import delete_reminder
    delete_reminder(user_id, rem_id)
    bot.answer_callback_query(call.id, MESSAGES[lang]['reminder_deleted'])
    bot.send_message(chat_id, MESSAGES[lang]['reminder_deleted_confirmation'])

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_goal_"))
def delete_goal_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    goal_id = int(call.data.split("delete_goal_")[1])
    from modules.goals import delete_goal
    delete_goal(user_id, goal_id)
    bot.answer_callback_query(call.id, MESSAGES[lang]['goal_deleted'])
    bot.send_message(chat_id, MESSAGES[lang]['goal_deleted_confirmation'])

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_countdown_"))
def delete_countdown_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    lang = user_states.get(user_id, {}).get('data', {}).get('language', 'en')
    cd_id = int(call.data.split("delete_countdown_")[1])
    from modules.countdowns import delete_countdown
    delete_countdown(user_id, cd_id)
    bot.answer_callback_query(call.id, MESSAGES[lang]['countdown_deleted'])
    bot.send_message(chat_id, MESSAGES[lang]['countdown_deleted_confirmation'])

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
        bot.send_message(chat_id, MESSAGES[lang]['unknown_menu_option'])

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
