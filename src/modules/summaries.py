"""
This module implements the Summaries & Reports functionality.
It generates a summary report for the user that includes:
  - Pending Tasks (with due dates)
  - Goals in progress (with frequency and next check date)
  - Upcoming Reminders (in the next 24 hours)
  - Countdowns (with computed time left until the event)
  - Weekly Schedule events (recurring events added by the user)
  - Optionally, a random quote (if any exists for the user)

Key functions:
  - generate_summary(user_id, user_lang='en'): Returns a formatted summary string (localized).
  - send_summary(bot, chat_id, user_id, user_lang='en'): Sends the summary to the user.
  - get_random_quote(user_id): Retrieves a random quote from the database.
"""

from datetime import datetime, timedelta
from database import get_db_connection

# A dictionary for localized summary labels:
SUMMARY_LABELS = {
    'en': {
        'pending_tasks': "**Pending Tasks:**",
        'no_pending_tasks': "No pending tasks.",
        'goals_in_progress': "**Goals in Progress:**",
        'no_goals': "No active goals.",
        'upcoming_reminders': "**Upcoming Reminders (next 24 hours):**",
        'no_reminders': "No reminders in the next 24 hours.",
        'countdowns': "**Countdowns:**",
        'no_countdowns': "No active countdowns.",
        'weekly_schedule': "**Weekly Schedule:**",
        'no_weekly_events': "No weekly events.",
        'quote_of_the_day': "**Quote of the Day:**",
        'event_passed': "Event passed",
        'daily_frequency': "Daily",
        'weekly_frequency': "Weekly",
        'monthly_frequency': "Monthly",
        'seasonal_frequency': "Seasonal",
        'yearly_frequency': "Yearly",
    },
    'fa': {
        'pending_tasks': "**وظایف در انتظار:**",
        'no_pending_tasks': "هیچ وظیفه‌ای در انتظار نیست.",
        'goals_in_progress': "**اهداف در حال پیشرفت:**",
        'no_goals': "هیچ هدف فعالی ندارید.",
        'upcoming_reminders': "**یادآوری‌های پیش رو (۲۴ ساعت آینده):**",
        'no_reminders': "یادآوری‌ای برای ۲۴ ساعت آینده وجود ندارد.",
        'countdowns': "**شمارش معکوس‌ها:**",
        'no_countdowns': "شمارش معکوسی فعال نیست.",
        'weekly_schedule': "**برنامه هفتگی:**",
        'no_weekly_events': "هیچ رویداد هفتگی وجود ندارد.",
        'quote_of_the_day': "**نقل قول روز:**",
        'event_passed': "رویداد گذشته است",
        'daily_frequency': "روزانه",
        'weekly_frequency': "هفتگی",
        'monthly_frequency': "ماهانه",
        'seasonal_frequency': "فصلی",
        'yearly_frequency': "سالانه",
    }
}

def generate_summary(user_id, user_lang='en'):
    """
    Generates a localized summary string for the given user.
    """
    labels = SUMMARY_LABELS.get(user_lang, SUMMARY_LABELS['en'])
    summary_lines = []
    now = datetime.now()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # --- Pending Tasks ---
    cursor.execute("""
        SELECT title, due_date 
        FROM tasks 
        WHERE user_id = ? AND status = 'pending' 
        ORDER BY created_at DESC
    """, (user_id,))
    tasks = cursor.fetchall()
    if tasks:
        summary_lines.append(labels['pending_tasks'])
        for task in tasks:
            title = task["title"]
            due_date = task["due_date"]
            if due_date:
                try:
                    due_dt = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
                    due_str = due_dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    due_str = due_date
            else:
                due_str = ("No due date" if user_lang == 'en' else "بدون موعد")
            summary_lines.append(f"- {title}\n  (Due: {due_str})")
    else:
        summary_lines.append(labels['no_pending_tasks'])
    
    # --- Active Goals ---
    cursor.execute("""
        SELECT title, frequency, next_check_date 
        FROM goals 
        WHERE user_id = ? AND status = 'in_progress' 
        ORDER BY created_at DESC
    """, (user_id,))
    goals = cursor.fetchall()
    if goals:
        summary_lines.append(f"\n{labels['goals_in_progress']}")
        for goal in goals:
            title = goal["title"]
            frequency = goal["frequency"]
            next_check_date = goal["next_check_date"]
            if user_lang == 'fa':
                if frequency == 'daily': freq_str = labels['daily_frequency']
                elif frequency == 'weekly': freq_str = labels['weekly_frequency']
                elif frequency == 'monthly': freq_str = labels['monthly_frequency']
                elif frequency == 'seasonal': freq_str = labels['seasonal_frequency']
                elif frequency == 'yearly': freq_str = labels['yearly_frequency']
                else: freq_str = frequency
            else:
                freq_str = frequency.capitalize()
            if next_check_date:
                try:
                    next_check_dt = datetime.strptime(next_check_date, "%Y-%m-%d %H:%M:%S")
                    next_check_str = next_check_dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    next_check_str = next_check_date
            else:
                next_check_str = ("N/A" if user_lang == 'en' else "نامشخص")
            summary_lines.append(f"- {title}\n  ({freq_str} | Next: {next_check_str})")
    else:
        summary_lines.append(f"\n{labels['no_goals']}")
    
    # --- Upcoming Reminders (Next 24 hours) ---
    next_day = now + timedelta(days=1)
    cursor.execute("""
        SELECT title, next_trigger_time 
        FROM reminders 
        WHERE user_id = ? AND next_trigger_time BETWEEN ? AND ? 
        ORDER BY next_trigger_time ASC
    """, (user_id, now, next_day))
    reminders = cursor.fetchall()
    if reminders:
        summary_lines.append(f"\n{labels['upcoming_reminders']}")
        for rem in reminders:
            title = rem["title"]
            trigger_time = rem["next_trigger_time"]
            try:
                trigger_dt = datetime.strptime(trigger_time, "%Y-%m-%d %H:%M:%S")
                trigger_str = trigger_dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                trigger_str = trigger_time
            summary_lines.append(f"- {title}\n  (At: {trigger_str})")
    else:
        summary_lines.append(f"\n{labels['no_reminders']}")
    
    # --- Countdowns ---
    cursor.execute("""
        SELECT title, event_datetime 
        FROM countdowns 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (user_id,))
    countdowns = cursor.fetchall()
    if countdowns:
        summary_lines.append(f"\n{labels['countdowns']}")
        for cd in countdowns:
            title = cd["title"]
            event_datetime = cd["event_datetime"]
            try:
                event_dt = datetime.strptime(event_datetime, "%Y-%m-%d %H:%M:%S")
                delta = event_dt - now
                if delta.total_seconds() < 0:
                    time_left = labels['event_passed']
                else:
                    days = delta.days
                    hours, rem = divmod(delta.seconds, 3600)
                    minutes, _ = divmod(rem, 60)
                    if user_lang == 'en':
                        time_left = f"{days}d {hours}h {minutes}m left"
                    else:
                        time_left = f"{days}روز {hours}ساعت {minutes}دقیقه باقی‌مانده"
            except Exception:
                time_left = event_datetime
            summary_lines.append(f"- {title}\n  {time_left}")
    else:
        summary_lines.append(f"\n{labels['no_countdowns']}")
    
    # --- Weekly Schedule ---
    cursor.execute("""
        SELECT title, day_of_week, time_of_day 
        FROM weekly_schedule 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (user_id,))
    weekly_events = cursor.fetchall()
    if weekly_events:
        summary_lines.append(f"\n{labels['weekly_schedule']}")
        for event in weekly_events:
            title = event["title"]
            day = event["day_of_week"]
            time_of_day = event["time_of_day"]
            summary_lines.append(f"- {title}\n  on {day} at {time_of_day}")
    else:
        summary_lines.append(f"\n{labels['no_weekly_events']}")
    
    conn.close()
    
    # --- Optional Random Quote ---
    quote = get_random_quote(user_id)
    if quote:
        summary_lines.append(f"\n{labels['quote_of_the_day']}")
        summary_lines.append(f"_{quote}_")
    
    return "\n".join(summary_lines)

def send_summary(bot, chat_id, user_id, user_lang='en'):
    """
    Generates and sends the summary report to the user (localized by user_lang).
    """
    summary_text = generate_summary(user_id, user_lang)
    bot.send_message(chat_id, summary_text, parse_mode="Markdown")

def get_random_quote(user_id):
    """
    Retrieves a random quote for the given user from the 'quotes' table.
    Returns the quote text if found, otherwise None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT quote_text 
        FROM quotes 
        WHERE user_id = ? 
        ORDER BY RANDOM() LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["quote_text"]
    return None
