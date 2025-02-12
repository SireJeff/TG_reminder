"""
bot.py

This is the main entry point for the bot. It integrates:
  - Onboarding (multilingual language selection, onboarding info, time zone selection via inline buttons, summary schedule, random check-in)
  - Main Menu & Navigation
  - Tasks Module
  - Goals Module
  - Reminders Module
  - Countdowns Module
  - Random Check-Ins Module
  - Summaries & Reports Module
  - Quotes Module
  - Help Command (detailed explanation with emojis)
  - Manage Items (view and delete tasks, reminders, goals, countdowns)
  - Settings (change language and timezone)

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
  - modules/date_conversion.py

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
        'welcome': "Welcome to Remindino Bot! 🤖\nPlease select your language:",
        'select_timezone': "Please select your timezone:",
        'set_timezone': "Timezone set to {}. ⏰",
        'select_summary': "How would you like to receive summaries? Choose one:",
        'enter_daily_time': "Please enter the time for your daily summary in HH:MM format (e.g., 20:00):",
        'enter_custom_interval': "Please enter the interval in hours for your summary (e.g., 3):",
        'enter_random_checkins': "How many random check-ins per day would you like? (Enter a number, e.g., 2)",
        'onboarding_complete': "Onboarding complete! Welcome to Remindino! 🎉",
        'help': (
            "🤖 *Remindino Bot Help*\n\n"
            "Welcome to Remindino, your smart digital planner! Whether you're a student managing your class schedule or a professional tracking deadlines, this bot is here to help you stay organized.\n\n"
            "📚 *Features:*\n"
            "• *Weekly Schedule:* Manage your fixed weekly events—your personal timetable for classes or meetings.\n"
            "• *Task Reminders:* Set reminders for assignments, projects, or daily tasks. For example, 'Submit your project by 2023-04-15 23:59 📅'.\n"
            "• *Countdowns:* Create countdowns for upcoming quizzes, exams, or important events. See exactly how much time is left ⏰.\n"
            "• *Random Check-Ins:* Receive friendly prompts like, 'Anything new to add?' at random times.\n"
            "• *Summaries & Reports:* Get a daily summary of your tasks and events so you never miss a beat!\n"
            "• *Quotes:* Add motivational quotes to brighten your day 🌟.\n\n"
            "⚙️ *Manage Items:* Easily view and delete your tasks, reminders, goals, and countdowns.\n"
            "⚙️ *Settings:* Change your language and timezone anytime.\n\n"
            "💡 *How to Get Started:*\n"
            "1. Type /start to begin. You'll be guided through language and timezone selection using inline buttons. For instance, select 'Tehran' if you're in Iran or 'New York' if you're on the East Coast.\n"
            "2. After onboarding, you'll see the main menu. Tap an option (e.g., 'Add Task', 'Add Countdown', etc.) to start.\n"
            "3. When entering dates, you can use either the Western (e.g., 2023/04/15) or Iranian calendar (e.g., 1402/01/26). The bot detects and converts Iranian dates automatically.\n\n"
            "😊 *Enjoy using Remindino!* If you need these instructions again, just type /help."
        ),
        'onboard_info': (
            "Here's a quick overview of how Remindino works:\n"
            "• You can add tasks, goals, reminders, and countdowns to keep track of your schedule.\n"
            "• Dates can be entered in either Western or Iranian formats, and they will be automatically converted.\n"
            "• Use the main menu to navigate between features.\n\n"
            "Press 'Let's go' to begin your onboarding!"
        ),
        'onboard_continue': "Let's go"
    },
    'fa': {
        'welcome': "به ریمایندینو خوش آمدید! 🤖\nلطفاً زبان خود را انتخاب کنید:",
        'select_timezone': "لطفاً منطقه زمانی خود را انتخاب کنید:",
        'set_timezone': "منطقه زمانی {} تنظیم شد. ⏰",
        'select_summary': "چگونه می‌خواهید خلاصه‌ها را دریافت کنید؟ یکی را انتخاب کنید:",
        'enter_daily_time': "لطفاً زمان دریافت خلاصه روزانه خود را به فرمت HH:MM وارد کنید (مثلاً 20:00):",
        'enter_custom_interval': "لطفاً فاصله زمانی به ساعت برای دریافت خلاصه را وارد کنید (مثلاً 3):",
        'enter_random_checkins': "چند بار در روز می‌خواهید یادآوری‌های تصادفی دریافت کنید؟ (یک عدد وارد کنید، مثلاً 2)",
        'onboarding_complete': "فرایند راه‌اندازی کامل شد! به ریمایندینو خوش آمدید! 🎉",
        'help': (
            "🤖 *راهنمای ریمایندینو*\n\n"
            "به ریمایندینو خوش آمدید، برنامه‌ریز دیجیتال هوشمند شما! چه دانشجو باشید که برنامه کلاس‌های خود را مدیریت می‌کنید و چه حرفه‌ای که به دنبال پیگیری مهلت‌ها هستید، این بات برای کمک به شما در سازماندهی امور طراحی شده است.\n\n"
            "📚 *امکانات:*\n"
            "• *برنامه هفتگی:* رویدادهای ثابت هفتگی خود را مدیریت کنید — همانند برنامه کلاس‌های روزانه یا جلسات کاری شما.\n"
            "• *یادآوری وظایف:* یادآوری‌هایی برای تکالیف، پروژه‌ها یا وظایف روزانه تنظیم کنید. مثلاً، 'پروژه خود را تا تاریخ 2023-04-15 23:59 ارسال کنید 📅'.\n"
            "• *شمارش معکوس:* شمارش معکوس برای آزمون‌ها، امتحانات یا رویدادهای مهم ایجاد کنید و دقیقاً ببینید چقدر زمان باقی مانده است ⏰.\n"
            "• *بررسی‌های تصادفی:* به صورت تصادفی پیام‌هایی مانند 'چیزی برای اضافه کردن دارید؟' دریافت کنید.\n"
            "• *خلاصه و گزارش‌ها:* خلاصه روزانه‌ای از وظایف و رویدادهای خود دریافت کنید تا هیچ اتفاقی از دست ندهید!\n"
            "• *نقل قول‌ها:* نقل قول‌های انگیزشی اضافه کنید تا در روزهای شلوغ روحیه‌تان بالا بماند 🌟.\n\n"
            "⚙️ *مدیریت موارد:* به راحتی وظایف، یادآوری‌ها، اهداف و شمارش معکوس‌های خود را مشاهده و حذف کنید.\n"
            "⚙️ *تنظیمات:* هر زمان که خواستید زبان یا منطقه زمانی خود را تغییر دهید.\n\n"
            "💡 *چگونه شروع کنیم:*\n"
            "1. دستور /start را تایپ کنید. شما از طریق دکمه‌های اینلاین، زبان (انگلیسی یا فارسی) و منطقه زمانی خود را انتخاب خواهید کرد. مثلاً 'Tehran' را انتخاب کنید اگر در ایران هستید یا 'New York' را اگر در شرق آمریکا هستید.\n"
            "2. پس از فرایند راه‌اندازی، منوی اصلی نمایش داده می‌شود. گزینه‌ای مانند 'افزودن وظیفه' یا 'افزودن شمارش معکوس' را لمس کنید.\n"
            "3. هنگام وارد کردن تاریخ، می‌توانید از تقویم غربی (مثلاً 2023/04/15) یا ایرانی (مثلاً 1402/01/26) استفاده کنید. بات به‌طور خودکار تشخیص داده و تاریخ ایرانی را تبدیل می‌کند.\n\n"
            "😊 *از ریمایندینو لذت ببرید!* برای مشاهده دوباره این دستورالعمل‌ها، تنها /help را تایپ کنید."
        ),
        'onboard_info': (
            "در اینجا یک مرور سریع بر نحوه کار ریمایندینو ارائه شده است:\n"
            "• شما می‌توانید وظایف، اهداف، یادآوری‌ها و شمارش معکوس‌ها را برای پیگیری برنامه خود اضافه کنید.\n"
            "• تاریخ‌ها را می‌توان به صورت تقویم غربی یا ایرانی وارد کرد و به صورت خودکار تبدیل می‌شوند.\n"
            "• از منوی اصلی برای حرکت بین امکانات استفاده کنید.\n\n"
            "برای شروع، 'بزن بریم' را فشار دهید!"
        ),
        'onboard_continue': "بزن بریم"
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
user_states = {}

# -------------------------------
# /start Command Handler & Pre-Onboarding Flow
# -------------------------------
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    # Check if the user exists; if not, create a new record.
    from database import get_db_connection
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
    # Prompt for language selection.
    markup = types.InlineKeyboardMarkup()
    btn_english = types.InlineKeyboardButton(text="English", callback_data="set_lang_en")
    btn_farsi = types.InlineKeyboardButton(text="فارسی", callback_data="set_lang_fa")
    markup.add(btn_english, btn_farsi)
    bot.send_message(message.chat.id, MESSAGES['en']['welcome'], reply_markup=markup)

# -------------------------------
# Language Selection Callback Handler
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def language_callback_handler(call):
    user_id = call.from_user.id
    if user_id not in user_states:
        return
    selected_lang = call.data.split("set_lang_")[1]  # "en" or "fa"
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (selected_lang, user_id))
    conn.commit()
    conn.close()
    user_states[user_id]['data']['language'] = selected_lang
    # Instead of immediately continuing, send an onboarding info message.
    help_msg = MESSAGES[selected_lang]['onboard_info']
    markup = types.InlineKeyboardMarkup()
    btn_continue = types.InlineKeyboardButton(text=MESSAGES[selected_lang]['onboard_continue'], callback_data="onboard_continue")
    markup.add(btn_continue)
    bot.send_message(call.message.chat.id, help_msg, reply_markup=markup)
    bot.answer_callback_query(call.id, f"Language set to {selected_lang}")

# -------------------------------
# Onboard Continue Callback Handler
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "onboard_continue")
def onboard_continue_handler(call):
    user_id = call.from_user.id
    lang = user_states[user_id]['data'].get('language', 'en')
    # Now continue with onboarding: set state to TIMEZONE and show timezone options.
    user_states[user_id]['state'] = STATE_TIMEZONE
    tz_markup = types.InlineKeyboardMarkup(row_width=2)
    for label, tz_value in TIMEZONE_CHOICES:
        tz_btn = types.InlineKeyboardButton(text=label, callback_data=f"set_tz_{tz_value}")
        tz_markup.add(tz_btn)
    bot.send_message(call.message.chat.id, MESSAGES[lang]['select_timezone'], reply_markup=tz_markup)
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
    from database import get_db_connection
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
    btn_daily = types.InlineKeyboardButton(text=("Daily" if lang == 'en' else "روزانه"), callback_data="set_summary_daily")
    btn_custom = types.InlineKeyboardButton(text=("Every X hours" if lang == 'en' else "هر X ساعت"), callback_data="set_summary_custom")
    btn_none = types.InlineKeyboardButton(text=("None" if lang == 'en' else "هیچ"), callback_data="set_summary_none")
    summary_markup.add(btn_daily, btn_custom, btn_none)
    bot.send_message(call.message.chat.id, MESSAGES[lang]['select_summary'], reply_markup=summary_markup)

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
        bot.answer_callback_query(call.id, "Daily summary selected")
        bot.send_message(call.message.chat.id, MESSAGES[lang]['enter_daily_time'])
    elif selection == "custom":
        user_states[user_id]['data']['summary_schedule'] = 'custom'
        user_states[user_id]['state'] = STATE_SUMMARY_TIME
        bot.answer_callback_query(call.id, "Custom summary interval selected")
        bot.send_message(call.message.chat.id, MESSAGES[lang]['enter_custom_interval'])
    elif selection == "none":
        user_states[user_id]['data']['summary_schedule'] = 'disabled'
        from database import get_db_connection
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
                datetime.strptime(text, "%H:%M")
                from database import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET summary_schedule = ?, summary_time = ? WHERE user_id = ?", ('daily', text, user_id))
                conn.commit()
                conn.close()
                user_states[user_id]['data']['summary_time'] = text
                user_states[user_id]['state'] = STATE_RANDOM_CHECKIN
                bot.send_message(message.chat.id, MESSAGES[lang]['enter_random_checkins'])
            except ValueError:
                bot.send_message(message.chat.id, MESSAGES[lang]['enter_daily_time'])
        elif summary_schedule == 'custom':
            if text.isdigit():
                from database import get_db_connection
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
            from database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET random_checkin_max = ? WHERE user_id = ?", (random_checkin, user_id))
            conn.commit()
            conn.close()
            user_states[user_id]['data']['random_checkin'] = random_checkin
            user_states[user_id]['state'] = STATE_COMPLETED
            bot.send_message(message.chat.id, MESSAGES[lang]['onboarding_complete'])
            from modules.menu import send_main_menu
            send_main_menu(bot, message.chat.id, lang)
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
# Additional Utility: Manage Items Menu
# -------------------------------
def manage_items_menu(bot, chat_id, user_id):
    """
    Displays a management menu for the user to view and delete their items.
    """
    markup = types.InlineKeyboardMarkup()
    btn_tasks = types.InlineKeyboardButton(text="Manage Tasks", callback_data="manage_tasks")
    btn_reminders = types.InlineKeyboardButton(text="Manage Reminders", callback_data="manage_reminders")
    btn_goals = types.InlineKeyboardButton(text="Manage Goals", callback_data="manage_goals")
    btn_countdowns = types.InlineKeyboardButton(text="Manage Countdowns", callback_data="manage_countdowns")
    btn_back = types.InlineKeyboardButton(text="Back to Main Menu", callback_data="back_main")
    markup.row(btn_tasks, btn_reminders)
    markup.row(btn_goals, btn_countdowns)
    markup.add(btn_back)
    bot.send_message(chat_id, "Manage Items:\nSelect a category to view and delete items:", reply_markup=markup)

def manage_tasks(bot, chat_id, user_id):
    """
    Lists tasks with delete buttons.
    """
    from modules.tasks import list_tasks, delete_task
    tasks = list_tasks(user_id)
    if not tasks:
        bot.send_message(chat_id, "No tasks found.")
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
    """
    Lists reminders with delete buttons.
    """
    from modules.reminders import list_reminders, delete_reminder
    reminders = list_reminders(user_id)
    if not reminders:
        bot.send_message(chat_id, "No reminders found.")
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
    """
    Lists goals with delete buttons.
    """
    from modules.goals import list_goals, delete_goal
    goals = list_goals(user_id)
    if not goals:
        bot.send_message(chat_id, "No goals found.")
        return
    for goal in goals:
        goal_id = goal["id"]
        title = goal["title"]
        markup = types.InlineKeyboardMarkup()
        btn_delete = types.InlineKeyboardButton(text="Delete 🗑", callback_data=f"delete_goal_{goal_id}")
        markup.add(btn_delete)
        bot.send_message(chat_id, f"Goal: {title}", reply_markup=markup)

def manage_countdowns(bot, chat_id, user_id):
    """
    Lists countdowns with delete buttons.
    """
    from modules.countdowns import list_countdowns, delete_countdown
    countdowns = list_countdowns(user_id)
    if not countdowns:
        bot.send_message(chat_id, "No countdowns found.")
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
    """
    Displays a settings menu to change language and timezone.
    """
    markup = types.InlineKeyboardMarkup()
    btn_change_lang = types.InlineKeyboardButton(text="Change Language", callback_data="settings_change_lang")
    btn_change_tz = types.InlineKeyboardButton(text="Change Timezone", callback_data="settings_change_tz")
    btn_back = types.InlineKeyboardButton(text="Back to Main Menu", callback_data="back_main")
    markup.row(btn_change_lang, btn_change_tz)
    markup.add(btn_back)
    bot.send_message(chat_id, "Settings:", reply_markup=markup)

# -------------------------------
# Callback Handlers for Manage Items and Settings
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("manage_") or call.data in ["back_main", "settings_change_lang", "settings_change_tz"])
def manage_callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data
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
        lang = user_states[user_id]['data'].get('language', 'en')
        send_main_menu(bot, chat_id, lang)
    elif data == "settings_change_lang":
        # Restart language selection
        user_states[user_id]['state'] = STATE_LANGUAGE
        markup = types.InlineKeyboardMarkup()
        btn_english = types.InlineKeyboardButton(text="English", callback_data="set_lang_en")
        btn_farsi = types.InlineKeyboardButton(text="فارسی", callback_data="set_lang_fa")
        markup.add(btn_english, btn_farsi)
        bot.send_message(chat_id, "Please select your language:", reply_markup=markup)
    elif data == "settings_change_tz":
        # Restart timezone selection using predefined choices
        user_states[user_id]['state'] = STATE_TIMEZONE
        lang = user_states[user_id]['data'].get('language', 'en')
        tz_markup = types.InlineKeyboardMarkup(row_width=2)
        for label, tz_value in TIMEZONE_CHOICES:
            tz_btn = types.InlineKeyboardButton(text=label, callback_data=f"set_tz_{tz_value}")
            tz_markup.add(tz_btn)
        bot.send_message(chat_id, MESSAGES[lang]['select_timezone'], reply_markup=tz_markup)
    else:
        bot.answer_callback_query(call.id, "Unhandled manage/settings option.")

# -------------------------------
# Callback Handlers for Deletion Actions
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_task_"))
def delete_task_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    task_id = int(call.data.split("delete_task_")[1])
    from modules.tasks import delete_task
    delete_task(user_id, task_id)
    bot.answer_callback_query(call.id, "Task deleted.")
    bot.send_message(chat_id, "Task has been deleted.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_reminder_"))
def delete_reminder_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    rem_id = int(call.data.split("delete_reminder_")[1])
    from modules.reminders import delete_reminder
    delete_reminder(user_id, rem_id)
    bot.answer_callback_query(call.id, "Reminder deleted.")
    bot.send_message(chat_id, "Reminder has been deleted.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_goal_"))
def delete_goal_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    goal_id = int(call.data.split("delete_goal_")[1])
    from modules.goals import delete_goal
    delete_goal(user_id, goal_id)
    bot.answer_callback_query(call.id, "Goal deleted.")
    bot.send_message(chat_id, "Goal has been deleted.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_countdown_"))
def delete_countdown_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    cd_id = int(call.data.split("delete_countdown_")[1])
    from modules.countdowns import delete_countdown
    delete_countdown(user_id, cd_id)
    bot.answer_callback_query(call.id, "Countdown deleted.")
    bot.send_message(chat_id, "Countdown has been deleted.")

# -------------------------------
# Integration: Main Menu Selections
# -------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def callback_menu_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
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
    elif data == "menu_view_summary":
        from modules.summaries import send_summary
        # Retrieve user's language to pass to send_summary.
        user_lang = user_states[user_id]['data'].get('language', 'en')
        send_summary(bot, chat_id, user_id, user_lang)
    elif data == "menu_manage_items":
        manage_items_menu(bot, chat_id, user_id)
    elif data == "menu_quotes":
        from modules.quotes import start_add_quote
        start_add_quote(bot, chat_id, user_id)
    elif data == "menu_settings":
        settings_menu(bot, chat_id, user_id)
    else:
        bot.send_message(chat_id, "Unknown menu option selected.")

# -------------------------------
# Integration: Main Menu from modules/menu.py
# -------------------------------
from modules.menu import send_main_menu  # Use this to return to main menu when needed.

# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == "__main__":
    from database import init_db
    init_db()
    print("Bot is running...")
    bot.infinity_polling()
