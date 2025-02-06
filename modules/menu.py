# modules/menu.py

from telebot import types

def send_main_menu(bot, chat_id):
    """
    Sends the Main Menu to the user with options for:
      - Add Task
      - Add Goal
      - Add Reminder
      - Add Countdown
      - View Summary
      - Manage Items
      - Quotes
      - Settings
    """
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_add_task = types.InlineKeyboardButton(text="Add Task", callback_data="menu_add_task")
    btn_add_goal = types.InlineKeyboardButton(text="Add Goal", callback_data="menu_add_goal")
    btn_add_reminder = types.InlineKeyboardButton(text="Add Reminder", callback_data="menu_add_reminder")
    btn_add_countdown = types.InlineKeyboardButton(text="Add Countdown", callback_data="menu_add_countdown")
    btn_view_summary = types.InlineKeyboardButton(text="View Summary", callback_data="menu_view_summary")
    btn_manage_items = types.InlineKeyboardButton(text="Manage Items", callback_data="menu_manage_items")
    btn_quotes = types.InlineKeyboardButton(text="Quotes", callback_data="menu_quotes")
    btn_settings = types.InlineKeyboardButton(text="Settings", callback_data="menu_settings")
    
    # Arrange buttons in rows.
    markup.row(btn_add_task, btn_add_goal)
    markup.row(btn_add_reminder, btn_add_countdown)
    markup.row(btn_view_summary, btn_manage_items)
    markup.row(btn_quotes, btn_settings)
    
    bot.send_message(chat_id, "Main Menu:", reply_markup=markup)

def register_menu_handlers(bot):
    """
    Registers callback query handlers for main menu selections.
    This is a basic placeholder handler that can be overridden in your main bot file.
    """
    @bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
    def handle_menu(call):
        chat_id = call.message.chat.id
        data = call.data
        
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
