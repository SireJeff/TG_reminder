# messages.py

MESSAGES = {
    'en': {
        # General messages
        "welcome": "Welcome to Remindino Bot! 🤖\nPlease select your language:",
        "select_timezone": "Please select your timezone:",
        "set_timezone": "Timezone set to {}. ⏰",
        "select_summary": "How would you like to receive summaries? Choose one:",
        "enter_daily_time": "Please enter the time for your daily summary in HH:MM format (e.g., 20:00):",
        "enter_custom_interval": "Please enter the interval in hours for your summary (e.g., 3):",
        "enter_random_checkins": "How many random check-ins per day would you like? (Enter a number, e.g., 2)",
        "onboarding_complete": "Onboarding complete! Welcome to Remindino! 🎉",
        "help": (
            "🤖 *Remindino Bot Help*\n\n"
            "Quick Overview:\n"
            "• /help: Brief overview of features.\n"
            "• /info: Detailed explanation of every feature, button, and input.\n\n"
            "Key Features:\n"
            "• *Tasks*: Add, update, and delete tasks with optional due dates.\n"
            "• *Goals*: Set long-term goals with daily, weekly, monthly, seasonal, or yearly frequencies.\n"
            "• *Reminders*: Set reminders for important events (preset or custom times).\n"
            "• *Countdowns*: Create countdowns for events (e.g., exams) and see the time left.\n"
            "• *Weekly Schedule*: Add recurring weekly events (e.g., classes, meetings).\n"
            "• *Random Check-Ins*: Receive friendly prompts throughout the day.\n"
            "• *Summaries*: Receive daily summaries of your items.\n"
            "• *Quotes*: Add motivational quotes.\n\n"
            "Manage items and adjust settings via the main menu.\n"
            "For a detailed explanation of each feature, type /info. Enjoy!"
        ),
        "info": (
            "🤖 *Detailed Info for Remindino*\n\n"
            "Welcome! Here’s a deep dive into how every part of Remindino works:\n\n"
            "1. *Onboarding*: \n"
            "   - When you type /start, you'll first choose your language using inline buttons. "
            "This selection sets the language for all messages. 🌐\n"
            "   - After selecting your language, you'll see a detailed info message explaining all the bot's features—such as adding tasks, setting goals, creating reminders and countdowns, and managing a weekly schedule. "
            "You can also use /info anytime to see these details again.\n"
            "   - Press the 'Let's go' button to continue the onboarding process.\n\n"
            "2. *Time Zone Selection*: \n"
            "   - Select your timezone from a list (e.g., Tehran, London) to ensure that all times are correct. ⏰\n\n"
            "3. *Summary Settings*: \n"
            "   - Choose how you'd like to receive daily summaries of your tasks, goals, reminders, and countdowns. 📋\n\n"
            "4. *Main Menu*: \n"
            "   - After onboarding, the main menu appears with options to add tasks, goals, reminders, countdowns, and weekly schedule events, view summaries, manage items, add quotes, and change settings.\n\n"
            "5. *Weekly Schedule*: \n"
            "   - This new feature lets you add recurring events on a specific day of the week at a specific time. "
            "For example, you can set a weekly event for 'Math Class' every Monday at 09:30. 📅\n\n"
            "6. *Manage Items & Settings*: \n"
            "   - View and delete existing tasks, reminders, goals, countdowns, or weekly events. "
            "Settings allow you to change your language or timezone at any time. ⚙️\n\n"
            "7. *Additional Commands*:\n"
            "   - /help: Shows a brief overview of features.\n"
            "   - /info: Shows this detailed explanation of every feature, button, and input.\n\n"
            "This guide is here to help you get the most out of Remindino. If you have questions, just type /info. Enjoy organizing your life! 😊"
        ),
        "onboard_info": (
            "Hey there! I'm Remindino – your friendly digital assistant here to help you organize your life! 🎉\n\n"
            "I can help you add tasks, set reminders, track countdowns for events, and even manage a weekly schedule for recurring events like classes or meetings. "
            "🤖 *Remindino Bot Help*\n\n"
            "Quick Overview:\n"
            "• /help: Brief overview of features.\n"
            "• /info: Detailed explanation of every feature, button, and input.\n\n"
            "Key Features:\n"
            "• *Tasks*: Add, update, and delete tasks with optional due dates.\n"
            "• *Goals*: Set long-term goals with daily, weekly, monthly, seasonal, or yearly frequencies.\n"
            "• *Reminders*: Set reminders for important events (preset or custom times).\n"
            "• *Countdowns*: Create countdowns for events (e.g., exams) and see the time left.\n"
            "• *Weekly Schedule*: Add recurring weekly events (e.g., classes, meetings).\n"
            "• *Random Check-Ins*: Receive friendly prompts throughout the day.\n"
            "• *Summaries*: Receive daily summaries of your items.\n"
            "• *Quotes*: Add motivational quotes.\n\n"
            "Manage items and adjust settings via the main menu.\n"
            "For a detailed explanation of each feature, type /info. Enjoy!\n\n"
            "When you're ready, press the button below to continue."
        ),
        "onboard_continue": "Let's go",
        
        # Task module messages
        "enter_task_title": "Please enter the task title:",
        "set_due_date_prompt": "Would you like to set a due date for this task?",
        "select_due_date_option": "Please select a due date option:",
        "due_date_today": "Today",
        "due_date_tomorrow": "Tomorrow",
        "due_date_custom": "Custom",
        "task_added_no_due": "Task added without a due date.",
        "task_added_today": "Task added with due date set to Today.",
        "task_added_tomorrow": "Task added with due date set to Tomorrow.",
        "enter_custom_due_date": "Please enter the custom due date and time in the format YYYY-MM-DD HH:MM (24hr):",
        "task_added_custom": "Task added with custom due date:",
        "invalid_date_format": "Invalid date format or conversion error: {}. Please enter the date and time as YYYY-MM-DD HH:MM",
        "unexpected_input": "Unexpected input. Please follow the instructions.",
        
        # Reminder module messages
        "enter_reminder_title": "What do you want to be reminded about?",
        "reminder_title_set": "Reminder Title set: {}",
        "prompt_reminder_time": "When would you like the reminder to trigger?",
        "in_1_hour": "In 1 hour",
        "in_2_hours": "In 2 hours",
        "tomorrow": "Tomorrow",
        "custom": "Custom",
        "reminder_time_set_1hr": "Reminder time set to 1 hour from now.",
        "reminder_time_set_2hrs": "Reminder time set to 2 hours from now.",
        "reminder_time_set_tomorrow": "Reminder time set to tomorrow.",
        "enter_custom_time": "Please enter the custom date and time in YYYY-MM-DD HH:MM format:",
        "prompt_repeat_choice": "Should this reminder repeat? Choose an option:",
        "one_time": "One-time",
        "every_x_hours": "Every X hours",
        "every_x_days": "Every X days",
        "daily": "Daily",
        "one_time_set": "One-time reminder set.",
        "enter_repeat_hours": "Please enter the number of hours for repetition:",
        "enter_repeat_days": "Please enter the number of days for repetition:",
        "daily_reminder_set": "Daily reminder set.",
        "invalid_repeat_interval": "Please enter a valid number for the repetition interval.",
        "reminder_added": "Reminder added:\nTitle: {title}\nNext Trigger: {next_trigger}\nRepeat: {repeat} {value}",
        "unknown_time_option": "Unknown time option.",
        "unknown_repeat_option": "Unknown repeat option.",
        "no_reminder_action": "No reminder action expected here.",
        
        # Goal module messages
        "enter_goal_title": "Please enter the goal title:",
        "select_goal_frequency": "Please select the goal frequency:",
        "goal_freq_daily": "Daily",
        "goal_freq_weekly": "Weekly",
        "goal_freq_monthly": "Monthly",
        "goal_freq_seasonal": "Seasonal",
        "goal_freq_yearly": "Yearly",
        "goal_added": "Goal added ({frequency})",
        "goal_added_successfully": "Goal added successfully.\nNext check date: {next_check_date}",
        "unknown_goal_action": "Unknown goal action.",
        
        # Countdown module messages
        "enter_countdown_title": "Please name your countdown event:",
        "enter_countdown_datetime": "When does it happen? Please enter the date and time in YYYY-MM-DD HH:MM format:",
        "invalid_countdown_datetime": "Invalid format or conversion error: {}. Please enter the date and time as YYYY-MM-DD HH:MM",
        "prompt_countdown_alerts": "Do you want periodic alerts for this event?",
        "no_alerts": "None",
        "daily_alerts": "Daily",
        "weekly_alerts": "Weekly",
        "alert_option_set": "Periodic alerts set: {option}",
        "unknown_alert_option": "Unknown notification option.",
        "no_countdown_action": "No countdown action expected here.",
        "countdown_added": "Countdown added:\nEvent: {title}\nEvent Time: {event_time}\nTime Left: {time_left}\nAlerts: {alerts}",
        "event_passed": "Event passed",
        
        # Quotes module messages
        "enter_quote_text": "Please enter the quote you want to add:",
        "quote_added": "Quote added successfully!",
        "language_set": "Language set to {}",
        "summary_daily": "Daily",
        "summary_custom": "Every X hours",
        "change_language": "Change Language",
        "change_timezone": "Change Timezone",
        "settings": "Settings:",
        "back_to_main_menu": "Back to Main Menu",
        "manage_tasks": "Manage Tasks",
        "manage_reminders": "Manage Reminders",
        "manage_goals": "Manage Goals",
        "manage_countdowns": "Manage Countdowns",
        "manage_items_menu": "Manage Items:\nSelect a category to view and delete items:",
        "back_to_main_menu": "Back to Main Menu"




    },
    'fa': {
        # General messages
        "welcome": "به ریمایندینو خوش آمدید! 🤖\nلطفاً زبان خود را انتخاب کنید:",
        "select_timezone": "لطفاً منطقه زمانی خود را انتخاب کنید:",
        "set_timezone": "منطقه زمانی {} تنظیم شد. ⏰",
        "select_summary": "چگونه می‌خواهید خلاصه‌ها را دریافت کنید؟ یکی را انتخاب کنید:",
        "enter_daily_time": "لطفاً زمان دریافت خلاصه روزانه خود را به فرمت HH:MM وارد کنید (مثلاً 20:00):",
        "enter_custom_interval": "لطفاً فاصله زمانی به ساعت برای دریافت خلاصه را وارد کنید (مثلاً 3):",
        "enter_random_checkins": "چند بار در روز می‌خواهید یادآوری‌های تصادفی دریافت کنید؟ (یک عدد وارد کنید، مثلاً 2)",
        "onboarding_complete": "فرایند راه‌اندازی کامل شد! به ریمایندینو خوش آمدید! 🎉",
        "help": (
            "🤖 *راهنمای ریمایندینو*\n\n"
            "نمای کلی کوتاه:\n"
            "• /help: نمای کلی کوتاهی از امکانات.\n"
            "• /info: توضیحات جامع و دقیق درباره هر ویژگی، دکمه و ورودی.\n\n"
            "امکانات اصلی:\n"
            "• *وظایف:* افزودن، به‌روزرسانی و حذف وظایف با امکان تعیین موعد.\n"
            "• *اهداف:* تنظیم اهداف بلندمدت با فرکانس‌های روزانه، هفتگی، ماهانه، فصلی یا سالانه.\n"
            "• *یادآوری‌ها:* دریافت یادآوری برای رویدادهای مهم با زمان‌های از پیش تعیین‌شده یا ورودی سفارشی.\n"
            "• *شمارش معکوس:* ایجاد شمارش معکوس برای رویدادهای مهم (مثلاً امتحانات) و نمایش زمان باقی‌مانده.\n"
            "• *برنامه هفتگی:* افزودن رویدادهای تکرارشونده در یک روز مشخص از هفته (مثلاً کلاس‌ها یا جلسات).\n"
            "• *بررسی‌های تصادفی:* دریافت پیام‌های دوستانه به‌صورت تصادفی.\n"
            "• *خلاصه و گزارش‌ها:* دریافت خلاصه روزانه از وظایف، اهداف، یادآوری‌ها و شمارش معکوس‌ها.\n"
            "• *نقل قول‌ها:* افزودن نقل قول‌های انگیزشی.\n\n"
            "شما می‌توانید از منوی اصلی موارد خود را مدیریت و از تنظیمات برای تغییر زبان یا منطقه زمانی استفاده کنید.\n\n"
            "برای توضیحات دقیق درباره هر بخش، /info را تایپ کنید. 😊"
        ),
        "info": (
            "🤖 *اطلاعات جامع درباره ریمایندینو*\n\n"
            "سلام! من ریمایندینو هستم، دستیار دیجیتال شما برای سازماندهی برنامه‌های روزانه. در اینجا به‌طور دقیق توضیح داده شده است که هر بخش و دکمه چه کاری انجام می‌دهد:\n\n"
            "1. *راه‌اندازی اولیه*: \n"
            "   - با دستور /start ابتدا زبان (انگلیسی یا فارسی) انتخاب می‌شود؛ این انتخاب باعث می‌شود تمام پیام‌ها به زبان مورد نظر شما نمایش داده شوند. 🌐\n"
            "   - سپس یک پیام راهنمای جامع با توضیحات دقیق و مثال‌های واقعی برای شما ارسال می‌شود. برای مثال، یاد خواهید گرفت چگونه وظایف، اهداف، یادآوری‌ها، شمارش معکوس و برنامه هفتگی را اضافه کنید.\n"
            "   - در پایان، دکمه «بزن بریم» قرار دارد تا پس از مطالعه راهنما، فرایند راه‌اندازی ادامه یابد.\n\n"
            "2. *انتخاب منطقه زمانی*: \n"
            "   - شما از میان گزینه‌های ارائه شده، منطقه زمانی خود را انتخاب می‌کنید تا تمام زمان‌های برنامه‌ریزی شده صحیح باشند. ⏰\n\n"
            "3. *تنظیم خلاصه روزانه*: \n"
            "   - شما مشخص می‌کنید چگونه خلاصه روزانه خود را دریافت کنید؛ مثلاً روزانه یا با فاصله‌های زمانی مشخص. این خلاصه شامل وظایف در انتظار، اهداف فعال، یادآوری‌های آتی، شمارش معکوس‌ها و برنامه هفتگی است. 📋\n\n"
            "4. *منوی اصلی*: \n"
            "   - پس از پایان راه‌اندازی، منوی اصلی شامل گزینه‌هایی برای افزودن وظایف، اهداف، یادآوری‌ها، شمارش معکوس، برنامه هفتگی، نمایش خلاصه، مدیریت موارد، نقل قول‌ها و تنظیمات است. هر دکمه به وضوح توضیح داده شده است.\n\n"
            "5. *برنامه هفتگی*: \n"
            "   - در این بخش می‌توانید رویدادهای تکرارشونده هفتگی (مانند کلاس‌ها یا جلسات) را اضافه کنید. برای مثال، می‌توانید یک رویداد برای 'کلاس ریاضی' در هر دوشنبه ساعت 09:30 تنظیم کنید. 📅\n\n"
            "6. *مدیریت موارد*: \n"
            "   - شما می‌توانید مواردی مانند وظایف، یادآوری‌ها، اهداف، شمارش معکوس و برنامه هفتگی را مشاهده و در صورت نیاز حذف کنید. 🗑\n\n"
            "7. *تنظیمات*: \n"
            "   - شما هر زمان می‌توانید زبان یا منطقه زمانی خود را تغییر دهید. ⚙️\n\n"
            "8. *دستورات اضافی*: \n"
            "   - /help: نمای کلی کوتاهی از امکانات ارائه می‌دهد.\n"
            "   - /info: این دستور توضیحات جامع و دقیقی درباره هر بخش و دکمه ارائه می‌دهد.\n\n"
            "امیدواریم این راهنما به شما کمک کند تا بهترین استفاده را از ریمایندینو ببرید. در هر زمان می‌توانید /info را تایپ کنید تا به این توضیحات دوباره دست پیدا کنید. 😊"
        ),
        "onboard_info": (
            "سلام! من ریمایندینو هستم – دستیار دیجیتال دوستانه شما برای سازماندهی زندگی! 🎉\n\n"
            "من به شما کمک می‌کنم تا وظایف، اهداف، یادآوری‌ها، شمارش معکوس‌ها و برنامه هفتگی رویدادها را مدیریت کنید. چه دانشجو باشید و چه حرفه‌ای، من همیشه در کنار شما هستم! 😎\n\n"
            "🤖 *راهنمای ریمایندینو*\n\n"
            "نمای کلی کوتاه:\n"
            "• /help: نمای کلی کوتاهی از امکانات.\n"
            "• /info: توضیحات جامع و دقیق درباره هر ویژگی، دکمه و ورودی.\n\n"
            "امکانات اصلی:\n"
            "• *وظایف:* افزودن، به‌روزرسانی و حذف وظایف با امکان تعیین موعد.\n"
            "• *اهداف:* تنظیم اهداف بلندمدت با فرکانس‌های روزانه، هفتگی، ماهانه، فصلی یا سالانه.\n"
            "• *یادآوری‌ها:* دریافت یادآوری برای رویدادهای مهم با زمان‌های از پیش تعیین‌شده یا ورودی سفارشی.\n"
            "• *شمارش معکوس:* ایجاد شمارش معکوس برای رویدادهای مهم (مثلاً امتحانات) و نمایش زمان باقی‌مانده.\n"
            "• *برنامه هفتگی:* افزودن رویدادهای تکرارشونده در یک روز مشخص از هفته (مثلاً کلاس‌ها یا جلسات).\n"
            "• *بررسی‌های تصادفی:* دریافت پیام‌های دوستانه به‌صورت تصادفی.\n"
            "• *خلاصه و گزارش‌ها:* دریافت خلاصه روزانه از وظایف، اهداف، یادآوری‌ها و شمارش معکوس‌ها.\n"
            "• *نقل قول‌ها:* افزودن نقل قول‌های انگیزشی.\n\n"
            "شما می‌توانید از منوی اصلی موارد خود را مدیریت و از تنظیمات برای تغییر زبان یا منطقه زمانی استفاده کنید.\n\n"
            "برای توضیحات دقیق درباره هر بخش، /info را تایپ کنید. 😊\n"
            "برای شروع، دکمه «بزن بریم» را فشار دهید تا فرایند راه‌اندازی ادامه یابد."
        ),
        "onboard_continue": "بزن بریم",
        
        # Task module messages
        "enter_task_title": "لطفاً عنوان وظیفه را وارد کنید:",
        "set_due_date_prompt": "آیا می‌خواهید برای این وظیفه یک موعد تعیین کنید؟",
        "select_due_date_option": "لطفاً یک گزینه برای تعیین موعد انتخاب کنید:",
        "due_date_today": "امروز",
        "due_date_tomorrow": "فردا",
        "due_date_custom": "سفارشی",
        "task_added_no_due": "وظیفه بدون تعیین موعد اضافه شد.",
        "task_added_today": "وظیفه با موعد امروز اضافه شد.",
        "task_added_tomorrow": "وظیفه با موعد فردا اضافه شد.",
        "enter_custom_due_date": "لطفاً موعد سفارشی را به فرمت YYYY-MM-DD HH:MM وارد کنید:",
        "task_added_custom": "وظیفه با موعد سفارشی اضافه شد:",
        "invalid_date_format": "فرمت تاریخ نامعتبر یا خطا در تبدیل: {}. لطفاً تاریخ و زمان را به صورت YYYY-MM-DD HH:MM وارد کنید",
        "unexpected_input": "ورودی نامشخص. لطفاً دستورالعمل‌ها را دنبال کنید.",
        
        # Reminder module messages
        "enter_reminder_title": "چه چیزی را می‌خواهید یادآوری کنم؟",
        "reminder_title_set": "عنوان یادآوری تنظیم شد: {}",
        "prompt_reminder_time": "چه زمانی می‌خواهید یادآوری انجام شود؟",
        "in_1_hour": "در 1 ساعت",
        "in_2_hours": "در 2 ساعت",
        "tomorrow": "فردا",
        "custom": "سفارشی",
        "reminder_time_set_1hr": "زمان یادآوری در 1 ساعت از حالا تنظیم شد.",
        "reminder_time_set_2hrs": "زمان یادآوری در 2 ساعت از حالا تنظیم شد.",
        "reminder_time_set_tomorrow": "زمان یادآوری برای فردا تنظیم شد.",
        "enter_custom_time": "لطفاً تاریخ و زمان سفارشی را به فرمت YYYY-MM-DD HH:MM وارد کنید:",
        "prompt_repeat_choice": "آیا می‌خواهید این یادآوری تکرار شود؟ یک گزینه انتخاب کنید:",
        "one_time": "یک‌بار",
        "every_x_hours": "هر X ساعت",
        "every_x_days": "هر X روز",
        "daily": "روزانه",
        "one_time_set": "یادآوری یک‌بار تنظیم شد.",
        "enter_repeat_hours": "لطفاً تعداد ساعت برای تکرار را وارد کنید:",
        "enter_repeat_days": "لطفاً تعداد روز برای تکرار را وارد کنید:",
        "daily_reminder_set": "یادآوری روزانه تنظیم شد.",
        "invalid_repeat_interval": "لطفاً یک عدد معتبر برای فاصله زمانی تکرار وارد کنید.",
        "reminder_added": "یادآوری اضافه شد:\nعنوان: {title}\nزمان بعدی: {next_trigger}\nتکرار: {repeat} {value}",
        "unknown_time_option": "گزینه زمان ناشناخته است.",
        "unknown_repeat_option": "گزینه تکرار ناشناخته است.",
        "no_reminder_action": "هیچ عملی برای یادآوری مورد انتظار نیست.",
        
        # Goal module messages
        "enter_goal_title": "لطفاً عنوان هدف را وارد کنید:",
        "select_goal_frequency": "لطفاً فرکانس هدف را انتخاب کنید:",
        "goal_freq_daily": "روزانه",
        "goal_freq_weekly": "هفتگی",
        "goal_freq_monthly": "ماهانه",
        "goal_freq_seasonal": "فصلی",
        "goal_freq_yearly": "سالانه",
        "goal_added": "هدف اضافه شد ({frequency})",
        "goal_added_successfully": "هدف با موفقیت اضافه شد.\nتاریخ بررسی بعدی: {next_check_date}",
        "unknown_goal_action": "عملکرد نامشخص برای هدف.",
        
        # Countdown module messages
        "enter_countdown_title": "لطفاً نام رویداد شمارش معکوس را وارد کنید:",
        "enter_countdown_datetime": "زمان برگزاری رویداد را به فرمت YYYY-MM-DD HH:MM وارد کنید:",
        "invalid_countdown_datetime": "فرمت نامعتبر یا خطای تبدیل: {}. لطفاً تاریخ و زمان را به صورت YYYY-MM-DD HH:MM وارد کنید",
        "prompt_countdown_alerts": "آیا برای این رویداد اعلان‌های دوره‌ای می‌خواهید؟",
        "no_alerts": "هیچ",
        "daily_alerts": "روزانه",
        "weekly_alerts": "هفتگی",
        "alert_option_set": "اعلان‌های دوره‌ای تنظیم شدند: {option}",
        "unknown_alert_option": "گزینه اعلان ناشناخته است.",
        "no_countdown_action": "هیچ عملی برای شمارش معکوس مورد انتظار نیست.",
        "countdown_added": "شمارش معکوس اضافه شد:\nرویداد: {title}\nزمان رویداد: {event_time}\nزمان باقی‌مانده: {time_left}\nاعلان‌ها: {alerts}",
        "event_passed": "رویداد گذشته است",
        
        # Quotes module messages
        "enter_quote_text": "لطفاً نقل قول مورد نظر خود را وارد کنید:",
        "quote_added": "نقل قول با موفقیت اضافه شد!",
        "language_set": "زبان به {} تنظیم شد",
        "summary_daily": "روزانه",
        "summary_custom": "هر X ساعت",
        "change_language": "تغییر زبان",
        "change_timezone": "تغییر منطقه زمانی",
        "settings": "تنظیمات:",
        "back_to_main_menu": "بازگشت به منوی اصلی",
        "manage_tasks": "مدیریت وظایف",
        "manage_reminders": "مدیریت یادآوری‌ها",
        "manage_goals": "مدیریت اهداف",
        "manage_countdowns": "مدیریت شمارش معکوس",
        "manage_items_menu": "مدیریت موارد:\nیک دسته را برای مشاهده و حذف موارد انتخاب کنید:",
        "back_to_main_menu": "بازگشت به منوی اصلی"

        
    }
}
