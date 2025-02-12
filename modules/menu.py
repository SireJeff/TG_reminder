# modules/menu.py

from telebot import types

# A simple dictionary holding menu labels for English (en) and Persian (fa).
MENU_LABELS = {
    'en': {
        'main_menu': "Main Menu:",
        'add_task': "Add Task",
        'add_goal': "Add Goal",
        'add_reminder': "Add Reminder",
        'add_countdown': "Add Countdown",
        'view_summary': "View Summary",
        'manage_items': "Manage Items",
        'quotes': "Quotes",
        'settings': "Settings"
    },
    'fa': {
        'main_menu': "منوی اصلی:",
        'add_task': "افزودن وظیفه",
        'add_goal': "افزودن هدف",
        'add_reminder': "افزودن یادآوری",
        'add_countdown': "افزودن شمارش معکوس",
        'view_summary': "نمایش خلاصه",
        'manage_items': "مدیریت موارد",
        'quotes': "نقل قول‌ها",
        'settings': "تنظیمات"
    }
}

def send_main_menu(bot, chat_id, user_lang='en'):
    """
    Sends the Main Menu to the user with localized options.
    
    Parameters:
      bot: TeleBot instance
      chat_id: Telegram chat ID
      user_lang: The user's language code ('en' or 'fa'), default 'en'.
    """
    labels = MENU_LABELS.get(user_lang, MENU_LABELS['en'])  # Fallback to English if not found

    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_add_task = types.InlineKeyboardButton(text=labels['add_task'], callback_data="menu_add_task")
    btn_add_goal = types.InlineKeyboardButton(text=labels['add_goal'], callback_data="menu_add_goal")
    btn_add_reminder = types.InlineKeyboardButton(text=labels['add_reminder'], callback_data="menu_add_reminder")
    btn_add_countdown = types.InlineKeyboardButton(text=labels['add_countdown'], callback_data="menu_add_countdown")
    btn_view_summary = types.InlineKeyboardButton(text=labels['view_summary'], callback_data="menu_view_summary")
    btn_manage_items = types.InlineKeyboardButton(text=labels['manage_items'], callback_data="menu_manage_items")
    btn_quotes = types.InlineKeyboardButton(text=labels['quotes'], callback_data="menu_quotes")
    btn_settings = types.InlineKeyboardButton(text=labels['settings'], callback_data="menu_settings")
    
    # Arrange buttons in rows.
    markup.row(btn_add_task, btn_add_goal)
    markup.row(btn_add_reminder, btn_add_countdown)
    markup.row(btn_view_summary, btn_manage_items)
    markup.row(btn_quotes, btn_settings)
    
    bot.send_message(chat_id, labels['main_menu'], reply_markup=markup)

def register_menu_handlers(bot):
    """
    Registers callback query handlers for main menu selections.
    This is a basic placeholder handler that can be overridden in your main bot file.
    """
    @bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
    def handle_menu(call):
        chat_id = call.message.chat.id
        data = call.data

        # In a real app, you'd retrieve user_lang from user_states or DB:
        # user_lang = user_states[user_id]['data'].get('language', 'en')
        
        if data == "menu_add_task":
            bot.send_message(chat_id, "You selected Add Task. [Placeholder for tasks module]")
        elif data == "menu_add_goal":
            bot.send_message(chat_id, "You selected Add Goal. [Placeholder for goals module]")
        elif data == "menu_add_reminder":
            bot.send_message(chat_id, "You selected Add Reminder. [Placeholder for reminders module]")
        elif data == "menu_add_countdown":
            bot.send_message(chat_id, "You selected Add Countdown. [Placeholder for countdowns module]")
        elif data == "menu_view_summary":
            bot.send_message(chat_id, "You selected View Summary. [Placeholder for summary module]")
        elif data == "menu_manage_items":
            bot.send_message(chat_id, "You selected Manage Items. [Placeholder for items management module]")
        elif data == "menu_quotes":
            bot.send_message(chat_id, "You selected Quotes. [Placeholder for quotes module]")
        elif data == "menu_settings":
            bot.send_message(chat_id, "You selected Settings. [Placeholder for settings module]")
        else:
            bot.send_message(chat_id, "Unknown menu option selected.")
