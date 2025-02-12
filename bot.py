"""
bot.py

This is the main entry point for the bot. It integrates:
  - Onboarding (multilingual language selection, detailed onboarding info, time zone selection via inline buttons, summary schedule, random check-in)
  - Main Menu & Navigation
  - Tasks Module
  - Goals Module
  - Reminders Module
  - Countdowns Module
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
            "Use /help for a quick overview or /info for a detailed explanation of all features.\n\n"
            "Key features include:\n"
            "• *Tasks*: Add, update, and delete tasks with optional due dates.\n"
            "• *Goals*: Set long-term goals with daily, weekly, monthly, seasonal, or yearly frequencies.\n"
            "• *Reminders*: Get notified about important events – choose preset times or enter a custom date.\n"
            "• *Countdowns*: See how much time remains until an event (like an exam or meeting).\n"
            "• *Random Check-Ins*: Receive friendly prompts throughout the day.\n"
            "• *Summaries*: Receive daily summaries of your tasks, goals, reminders, and countdowns.\n"
            "• *Quotes*: Add motivational quotes to inspire you.\n\n"
            "You can manage your items and adjust settings (language, timezone) via the main menu.\n\n"
            "For detailed explanations of each feature, try the /info command. 😊"
        ),
        'info': (
            "🤖 *Detailed Info for Remindino*\n\n"
            "Welcome! Here’s a deep dive into how every part of Remindino works:\n\n"
            "1. *Onboarding*: \n"
            "   - When you type /start, you'll first choose your language (English or فارسی) using inline buttons. "
            "     This sets the language for all messages and buttons. 🌐\n"
            "   - After selecting your language, you'll receive a detailed info message explaining all the bot's features. "
            "     For example, you'll learn that Remindino can help you add tasks, set reminders, manage goals, and more. "
            "     Then, press the 'Let's go' (or 'بزن بریم') button to begin.\n\n"
            "2. *Time Zone Selection*: \n"
            "   - Next, you'll select your timezone from a set of popular options (like Tehran, London, New York, etc.). "
            "     This ensures that all scheduled times (due dates, reminders, etc.) are correctly converted to your local time. ⏰\n\n"
            "3. *Summary Settings*: \n"
            "   - You'll be asked how you want to receive daily summaries. You can choose daily, a custom interval, or disable them. "
            "     These summaries provide an overview of your pending tasks, active goals, upcoming reminders, and countdowns. 📋\n\n"
            "4. *Main Menu*: \n"
            "   - Once onboarding is complete, you'll see the main menu. Here are what the buttons do:\n"
            "     • *Add Task*: Create new tasks with optional due dates. For example, you might add a task 'Submit assignment' "
            "       and set the due date to today or tomorrow. ✅\n"
            "     • *Add Goal*: Set long-term goals (like 'Exercise daily') and choose how frequently you want to check on them. 🎯\n"
            "     • *Add Reminder*: Set reminders for important events. You can use preset times (e.g., in 1 hour, 2 hours, or tomorrow) "
            "       or enter a custom date and time. 🔔\n"
            "     • *Add Countdown*: Create countdowns for events such as exams or meetings. You'll see how much time is left until the event. ⏳\n"
            "     • *View Summary*: Get a full report of your tasks, goals, reminders, and countdowns for the day. 📊\n"
            "     • *Manage Items*: View and delete your existing tasks, reminders, goals, and countdowns. 🗑\n"
            "     • *Quotes*: Add motivational quotes that you can include in your daily summary. 🌟\n"
            "     • *Settings*: Change your language or timezone at any time. ⚙️\n\n"
            "5. *Additional Commands*:\n"
            "   - /help: Provides a brief overview of the bot's features and usage.\n"
            "   - /info: (This command) Provides a detailed explanation of every feature, button, and input with real-life examples and emojis.\n\n"
            "This comprehensive guide should help you understand how to get the most out of Remindino. "
            "If you have any questions, simply refer back to /info. Enjoy organizing your life with Remindino! 😊"
        ),
        'onboard_info': (
            "Hey there! I'm Remindino – your friendly digital assistant to help you organize your life! 🎉\n\n"
            "I can help you add tasks, set reminders, track countdowns for exams or events, and even provide daily summaries of everything on your schedule. Whether you're a student juggling classes or a professional managing deadlines, I've got your back! 😎\n\n"
            "You can enter dates in either the Western format (e.g., 2023/04/15) or the Iranian format (e.g., 1402/01/26), and I'll automatically convert them for you. Cool, right? 📅✨\n\n"
                        "• *Weekly Schedule:* Manage your fixed weekly events — your personal timetable for classes or meetings.\n\n"
            "• *Task Reminders:* Set reminders for assignments, projects, or daily tasks. For example, 'Submit your project by 2023-04-15 23:59 📅'.\n\n"
            "• *Countdowns:* Create countdowns for upcoming quizzes, exams, or important events. See exactly how much time is left ⏰.\n\n"
            "• *Random Check-Ins:* Receive friendly prompts like 'Anything new to add?' at random times.\n\n"
            "• *Summaries & Reports:* Get a daily summary of your tasks and events so you never miss a beat!\n\n"
            "• *Quotes:* Add motivational quotes to brighten your day 🌟.\n\n"
            "⚙️ *Manage Items:* Easily view and delete your tasks, reminders, goals, and countdowns.\n\n"
            "⚙️ *Settings:* Change your language and timezone anytime.\n\n"
            "💡 *How to Get Started:*\n\n"
            "1. Type /start to begin. You'll be guided through language and timezone selection using inline buttons.\n"
            "2. After onboarding, you'll see the main menu. Tap an option (e.g., 'Add Task', 'Add Countdown', etc.) to start.\n"
            "3. Dates can be entered in either the Western (e.g., 2023/04/15) or Iranian calendar (e.g., 1402/01/26); I'll handle the conversion automatically.\n\n"
            "😊 *Enjoy using Remindino!* If you need these instructions again, just type /help or /info.\n\n"
            "When you're ready, press 'بزن بریم' to start your onboarding!"
        ),
        'onboard_continue': "Let's go",
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
            "به ریمایندینو خوش آمدید، دستیار دیجیتال شما برای سازماندهی زندگی! چه دانشجو باشید و چه حرفه‌ای، این بات به شما کمک می‌کند تا برنامه‌ها و وظایف خود را به خوبی مدیریت کنید.\n\n"
            "📚 *امکانات:*\n"
            "• *برنامه هفتگی:* رویدادهای ثابت هفتگی خود را مدیریت کنید، مانند برنامه کلاس‌های روزانه یا جلسات کاری.\n"
            "• *یادآوری وظایف:* یادآوری‌هایی برای تکالیف، پروژه‌ها یا وظایف روزانه تنظیم کنید. مثلاً، 'پروژه‌تان را تا تاریخ 2023-04-15 23:59 ارسال کنید 📅'.\n"
            "• *شمارش معکوس:* شمارش معکوس برای آزمون‌ها، امتحانات یا رویدادهای مهم ایجاد کنید تا دقیقاً ببینید چقدر زمان باقی مانده است ⏰.\n"
            "• *بررسی‌های تصادفی:* پیام‌های دوستانه‌ای مانند 'چیزی برای اضافه کردن دارید؟' به صورت تصادفی دریافت کنید.\n"
            "• *خلاصه و گزارش‌ها:* خلاصه‌ای از وظایف و رویدادهای روزانه دریافت کنید تا هیچ اتفاقی از دست ندهید!\n"
            "• *نقل قول‌ها:* نقل قول‌های انگیزشی اضافه کنید تا روحیه‌تان بالا بماند 🌟.\n\n"
            "⚙️ *مدیریت موارد:* به راحتی وظایف، یادآوری‌ها، اهداف و شمارش معکوس‌های خود را مشاهده و حذف کنید.\n"
            "⚙️ *تنظیمات:* هر زمان که خواستید، زبان یا منطقه زمانی خود را تغییر دهید.\n\n"
            "💡 *چگونه شروع کنیم:*\n"
            "1. دستور /start را تایپ کنید. ابتدا از طریق دکمه‌های اینلاین، زبان (انگلیسی یا فارسی) خود را انتخاب می‌کنید.\n"
            "2. سپس یک پیام راهنمای جامع (با توضیحات کامل و مثال‌های واقعی) برای شما ارسال می‌شود. برای مشاهده جزئیات، دستور /info را هم می‌توانید تایپ کنید.\n"
            "3. در پایان، دکمه 'بزن بریم' را فشار دهید تا فرایند راه‌اندازی ادامه یابد.\n\n"
            "😊 *از ریمایندینو لذت ببرید!* برای مشاهده دوباره این دستورالعمل‌ها، /help را تایپ کنید."
        ),
        'info': (
            "🤖 *اطلاعات جامع درباره ریمایندینو*\n\n"
            "سلام! من ریمایندینو هستم، دستیار دیجیتال شما برای سازماندهی برنامه‌های روزانه. در اینجا به صورت دقیق توضیح داده شده است که هر بخش و دکمه چه کاری انجام می‌دهد:\n\n"
            "1. *فرایند راه‌اندازی*: \n"
            "   - با دستور /start آغاز کنید. ابتدا از طریق دکمه‌های اینلاین، زبان (انگلیسی یا فارسی) انتخاب می‌شود. این انتخاب تمام پیام‌ها و دکمه‌ها را به زبان مورد نظر شما نمایش می‌دهد. 🌐\n"
            "   - سپس یک پیام راهنمای کامل با توضیحات دقیق (با مثال‌های واقعی و ایموجی‌ها) برای شما ارسال می‌شود تا متوجه شوید چگونه از امکانات ریمایندینو استفاده کنید. برای مثال، یاد خواهید گرفت که چگونه وظایف، اهداف، یادآوری‌ها و شمارش معکوس‌ها را اضافه کنید.\n"
            "   - در پایان این بخش، با فشار دادن دکمه «بزن بریم» فرایند راه‌اندازی ادامه پیدا می‌کند.\n\n"
            "2. *انتخاب منطقه زمانی*: \n"
            "   - پس از انتخاب زبان، شما باید منطقه زمانی خود را از میان گزینه‌های ارائه شده انتخاب کنید تا تمام زمان‌ها به درستی محاسبه شوند. ⏰\n\n"
            "3. *تنظیم خلاصه روزانه*: \n"
            "   - شما مشخص می‌کنید که چگونه می‌خواهید خلاصه روزانه دریافت کنید؛ مثلا روزانه یا با فاصله‌های زمانی مشخص. این خلاصه شامل وظایف در انتظار، اهداف فعال، یادآوری‌های آتی و شمارش معکوس‌ها خواهد بود. 📋\n\n"
            "4. *منوی اصلی*: \n"
            "   - پس از پایان راه‌اندازی، منوی اصلی ظاهر می‌شود که شامل گزینه‌هایی مانند افزودن وظیفه، هدف، یادآوری، شمارش معکوس، نمایش خلاصه، مدیریت موارد، نقل قول‌ها و تنظیمات است. برای مثال، دکمه 'افزودن وظیفه' به شما امکان می‌دهد وظایف جدیدی اضافه کنید.\n\n"
            "5. *مدیریت موارد*: \n"
            "   - در این بخش می‌توانید تمامی موارد (وظایف، یادآوری‌ها، اهداف، شمارش معکوس) را مشاهده کرده و در صورت نیاز، حذف کنید. 🗑\n\n"
            "6. *تنظیمات*: \n"
            "   - شما می‌توانید در هر زمان زبان یا منطقه زمانی خود را تغییر دهید. ⚙️\n\n"
            "7. *دستورات اضافی*: \n"
            "   - /help: یک نمای کلی کوتاه از امکانات ریمایندینو ارائه می‌دهد.\n"
            "   - /info: این دستور اطلاعات جامع و دقیقی درباره هر بخش و دکمه ارائه می‌دهد.\n\n"
            "امیدوارم این راهنما به شما کمک کند تا بهترین استفاده را از ریمایندینو ببرید. اگر سوالی داشتید، کافیست دوباره /info را تایپ کنید. 😊"
        ),
        'onboard_info': (
            "سلام! من ریمایندینو هستم – دستیار دیجیتال دوستانه شما برای سازماندهی زندگی! 🎉\n\n"
            "من به شما کمک می‌کنم تا وظایف، اهداف، یادآوری‌ها و شمارش معکوس‌های برنامه‌ی شلوغ خود را مدیریت کنید. چه دانشجو باشید و چه حرفه‌ای، من همیشه در کنار شما هستم! 😎\n\n"
            "تاریخ‌ها را می‌توانید به صورت تقویم غربی (مثلاً 2023/04/15) یا ایرانی (مثلاً 1402/01/26) وارد کنید و من آن‌ها را به‌طور خودکار تبدیل می‌کنم. چقدر عالیه! 📅✨\n\n"
            "📚 *امکانات:*\n"
            "• *برنامه هفتگی:* رویدادهای ثابت هفتگی خود را مدیریت کنید، مانند برنامه کلاس‌ها یا جلسات کاری.\n\n"
            "• *یادآوری وظایف:* برای تکالیف، پروژه‌ها یا وظایف روزانه یادآوری تنظیم کنید. مثلاً 'پروژه‌تان را تا تاریخ 2023-04-15 23:59 ارسال کنید 📅'.\n\n"
            "• *شمارش معکوس:* شمارش معکوس برای آزمون‌ها، امتحانات یا رویدادهای مهم ایجاد کنید تا دقیقاً ببینید چقدر زمان باقی مانده است ⏰.\n\n"
            "• *بررسی‌های تصادفی:* پیام‌های دوستانه مانند 'چیزی برای اضافه کردن دارید؟' به‌طور تصادفی دریافت کنید.\n\n"
            "• *خلاصه و گزارش‌ها:* خلاصه‌ای از وظایف و رویدادهای روزانه دریافت کنید تا هیچ چیزی از دست ندهید!\n\n"
            "• *نقل قول‌ها:* نقل قول‌های انگیزشی اضافه کنید تا روحیه‌تان بالا بماند 🌟.\n\n"
            "⚙️ *مدیریت موارد:* به راحتی وظایف، یادآوری‌ها، اهداف و شمارش معکوس‌های خود را مشاهده و حذف کنید.\n\n"
            "⚙️ *تنظیمات:* هر زمان که خواستید، زبان یا منطقه زمانی خود را تغییر دهید.\n\n"
            "💡 *چگونه شروع کنیم:*\n\n"
            "1. دستور /start را تایپ کنید. شما از طریق دکمه‌های اینلاین، زبان (انگلیسی یا فارسی) و منطقه زمانی خود را انتخاب خواهید کرد.\n"
            "2. پس از راه‌اندازی، منوی اصلی نمایش داده می‌شود. گزینه‌هایی مانند 'افزودن وظیفه' یا 'افزودن شمارش معکوس' را لمس کنید.\n"
            "3. هنگام وارد کردن تاریخ، می‌توانید از تقویم غربی (مثلاً 2023/04/15) یا ایرانی (مثلاً 1402/01/26) استفاده کنید؛ من تبدیل آن‌ها را انجام می‌دهم.\n\n"
            "😊 *از ریمایندینو لذت ببرید!* برای مشاهده دوباره این دستورالعمل‌ها، تنها /info یا /help را تایپ کنید."
            "برای شروع، دکمه «بزن بریم» را فشار دهید تا با هم روزتان را مدیریت کنیم! 🚀"
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
STATE_TIMEZONE = "timezone"      # Handled via inline buttons
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
# /help Command Handler
# -------------------------------
@bot.message_handler(commands=['help'])
def handle_help(message):
    user_id = message.from_user.id
    lang = 'en'
    if user_id in user_states and 'language' in user_states[user_id]['data']:
        lang = user_states[user_id]['data']['language']
    help_text = MESSAGES[lang]['help']
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# -------------------------------
# /info Command Handler
# -------------------------------
@bot.message_handler(commands=['info'])
def handle_info(message):
    user_id = message.from_user.id
    lang = 'en'
    if user_id in user_states and 'language' in user_states[user_id]['data']:
        lang = user_states[user_id]['data']['language']
    # A very detailed explanation of every action and button.
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
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (selected_lang, user_id))
    conn.commit()
    conn.close()
    user_states[user_id]['data']['language'] = selected_lang
    # Instead of continuing immediately, send the onboarding info message.
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
    # Continue with onboarding: set state to TIMEZONE and show timezone options.
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
        user_states[user_id]['state'] = STATE_LANGUAGE
        markup = types.InlineKeyboardMarkup()
        btn_english = types.InlineKeyboardButton(text="English", callback_data="set_lang_en")
        btn_farsi = types.InlineKeyboardButton(text="فارسی", callback_data="set_lang_fa")
        markup.add(btn_english, btn_farsi)
        bot.send_message(chat_id, "Please select your language:", reply_markup=markup)
    elif data == "settings_change_tz":
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
from modules.menu import send_main_menu

# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == "__main__":
    from database import init_db
    init_db()
    print("Bot is running...")
    bot.infinity_polling()
