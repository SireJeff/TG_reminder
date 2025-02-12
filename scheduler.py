import random
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from database import get_db_connection
from modules.summaries import send_summary
from modules.random_checkins import send_random_checkin

# Create the BackgroundScheduler instance
scheduler = BackgroundScheduler()

def init_scheduler():
    """Initializes and starts the scheduler."""
    scheduler.start()

def schedule_reminder(reminder_id, next_trigger_time, user_id, chat_id):
    """
    Schedules a job for a reminder at its next_trigger_time.
    
    Parameters:
      - reminder_id: The unique ID of the reminder.
      - next_trigger_time: A datetime object when the reminder should trigger.
      - user_id: Telegram user ID.
      - chat_id: Telegram chat ID.
    """
    trigger = DateTrigger(run_date=next_trigger_time)
    job_id = f"reminder_{reminder_id}"
    scheduler.add_job(func=send_reminder_wrapper, trigger=trigger, id=job_id,
                      args=[user_id, chat_id, reminder_id])

def send_reminder_wrapper(user_id, chat_id, reminder_id):
    """
    Wrapper function that retrieves the reminder details and sends the reminder message.
    This example assumes that a function `send_reminder_message` is defined in the reminders module.
    """
    from modules.reminders import send_reminder_message  # Import here to avoid circular dependency
    send_reminder_message(user_id, chat_id, reminder_id)

def schedule_summary(bot, user_id, chat_id, summary_schedule, summary_time):
    """
    Schedules a summary report for the user based on their settings.
    
    Parameters:
      - bot: The TeleBot instance.
      - user_id: Telegram user ID.
      - chat_id: Telegram chat ID.
      - summary_schedule: 'daily' or 'custom' (or other values to indicate disabled).
      - summary_time: If 'daily', a string in "HH:MM" format; if 'custom', the interval in hours.
    """
    now = datetime.now()
    if summary_schedule == 'daily':
        try:
            summary_dt = datetime.strptime(summary_time, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day)
        except Exception:
            return
        if summary_dt < now:
            summary_dt += timedelta(days=1)
        trigger = DateTrigger(run_date=summary_dt)
        job_id = f"summary_daily_{user_id}"
        scheduler.add_job(func=send_summary, trigger=trigger, id=job_id,
                          args=[bot, chat_id, user_id])
    elif summary_schedule == 'custom':
        try:
            interval_hours = int(summary_time)
        except ValueError:
            return
        trigger = IntervalTrigger(hours=interval_hours, start_date=now + timedelta(hours=interval_hours))
        job_id = f"summary_custom_{user_id}"
        scheduler.add_job(func=send_summary, trigger=trigger, id=job_id,
                          args=[bot, chat_id, user_id])
    else:
        remove_job(f"summary_daily_{user_id}")
        remove_job(f"summary_custom_{user_id}")

def schedule_random_checkins(bot, user_id, chat_id, random_checkin_max):
    """
    Schedules random check-in jobs for the user for the current day.
    
    For demonstration, check-ins are scheduled randomly between 8 AM and 9 PM.
    """
    now = datetime.now()
    start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
    total_seconds = (end_time - start_time).total_seconds()
    if total_seconds <= 0:
        return
    for i in range(random_checkin_max):
        random_offset_seconds = random.randint(0, int(total_seconds))
        run_date = start_time + timedelta(seconds=random_offset_seconds)
        if run_date < now:
            run_date = now + timedelta(minutes=1)
        job_id = f"random_checkin_{user_id}_{i}"
        scheduler.add_job(func=send_random_checkin, trigger=DateTrigger(run_date=run_date),
                          id=job_id, args=[bot, chat_id, user_id])

def schedule_weekly_event_reminders(bot, user_id, chat_id):
    """
    Schedules reminders for all weekly events for the user.
    For each weekly event, the reminder is set to trigger 30 minutes before its next occurrence.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, day_of_week, time_of_day FROM weekly_schedule WHERE user_id = ?", (user_id,))
    events = cursor.fetchall()
    conn.close()
    
    now = datetime.now()
    for event in events:
        event_id = event["id"]
        title = event["title"]
        day_str = event["day_of_week"]  # Expected to be a weekday name (e.g., "Monday")
        time_str = event["time_of_day"]  # Expected format "HH:MM"
        
        # Compute the weekday number for the event (Monday=0, Sunday=6)
        weekdays = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}
        event_weekday = weekdays.get(day_str, None)
        if event_weekday is None:
            continue  # Skip if the weekday is unrecognized
        
        # Get hour and minute from time_str
        try:
            hour, minute = map(int, time_str.split(":"))
        except Exception:
            continue  # Skip if time parsing fails
        
        # Compute next occurrence of the event:
        # Get today's weekday number
        today_weekday = now.weekday()
        days_ahead = event_weekday - today_weekday
        if days_ahead < 0 or (days_ahead == 0 and now.time() >= datetime(now.year, now.month, now.day, hour, minute).time()):
            days_ahead += 7
        next_event_date = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        # Set trigger time 30 minutes before the event
        trigger_time = next_event_date - timedelta(minutes=30)
        # If trigger_time is in the past, add 7 days
        if trigger_time < now:
            trigger_time += timedelta(days=7)
        
        job_id = f"weekly_event_{event_id}_{user_id}"
        scheduler.add_job(func=send_weekly_event_reminder, trigger=DateTrigger(run_date=trigger_time),
                          id=job_id, args=[bot, user_id, chat_id, event_id, title, next_event_date.strftime('%H:%M')])
        
def send_weekly_event_reminder(bot, user_id, chat_id, event_id, title, event_time_str):
    """
    Sends a reminder message for a weekly event.
    """
    bot.send_message(chat_id, f"Reminder: Your weekly event '{title}' is scheduled to start at {event_time_str} (in 30 minutes).")

def schedule_nightly_tomorrow_summary(bot, user_id, chat_id):
    """
    Schedules a daily job at 9 PM that sends a summary of tomorrow's weekly events.
    """
    job_id = f"nightly_tomorrow_summary_{user_id}"
    trigger = CronTrigger(hour=21, minute=0)
    scheduler.add_job(func=send_tomorrow_weekly_summary, trigger=trigger, id=job_id,
                      args=[bot, user_id, chat_id])

def send_tomorrow_weekly_summary(bot, user_id, chat_id):
    """
    Retrieves weekly events for tomorrow and sends a summary message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_weekday = tomorrow.strftime("%A")  # e.g., "Monday"
    cursor.execute("SELECT title, time_of_day FROM weekly_schedule WHERE user_id = ? AND day_of_week = ?", (user_id, tomorrow_weekday))
    events = cursor.fetchall()
    conn.close()
    
    if events:
        message_lines = [f"Tomorrow's Weekly Events ({tomorrow_weekday}):"]
        for event in events:
            title = event["title"]
            time_of_day = event["time_of_day"]
            message_lines.append(f"- {title} at {time_of_day}")
        summary_message = "\n".join(message_lines)
        bot.send_message(chat_id, summary_message)
    else:
        bot.send_message(chat_id, "No weekly events scheduled for tomorrow.")

def remove_job(job_id):
    """Removes a scheduled job if it exists."""
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

# -------------------------------
# Existing Functions (Unchanged)
# -------------------------------
def schedule_summary(bot, user_id, chat_id, summary_schedule, summary_time):
    now = datetime.now()
    if summary_schedule == 'daily':
        try:
            summary_dt = datetime.strptime(summary_time, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day)
        except Exception:
            return
        if summary_dt < now:
            summary_dt += timedelta(days=1)
        trigger = DateTrigger(run_date=summary_dt)
        job_id = f"summary_daily_{user_id}"
        scheduler.add_job(func=send_summary, trigger=trigger, id=job_id,
                          args=[bot, chat_id, user_id])
    elif summary_schedule == 'custom':
        try:
            interval_hours = int(summary_time)
        except ValueError:
            return
        trigger = IntervalTrigger(hours=interval_hours, start_date=now + timedelta(hours=interval_hours))
        job_id = f"summary_custom_{user_id}"
        scheduler.add_job(func=send_summary, trigger=trigger, id=job_id,
                          args=[bot, chat_id, user_id])
    else:
        remove_job(f"summary_daily_{user_id}")
        remove_job(f"summary_custom_{user_id}")

def schedule_random_checkins(bot, user_id, chat_id, random_checkin_max):
    now = datetime.now()
    start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
    total_seconds = (end_time - start_time).total_seconds()
    if total_seconds <= 0:
        return
    for i in range(random_checkin_max):
        random_offset_seconds = random.randint(0, int(total_seconds))
        run_date = start_time + timedelta(seconds=random_offset_seconds)
        if run_date < now:
            run_date = now + timedelta(minutes=1)
        job_id = f"random_checkin_{user_id}_{i}"
        scheduler.add_job(func=send_random_checkin, trigger=DateTrigger(run_date=run_date),
                          id=job_id, args=[bot, chat_id, user_id])

if __name__ == "__main__":
    import time
    init_scheduler = lambda: scheduler.start()  # For testing purposes.
    init_scheduler()
    print("Scheduler is running...")
    while True:
        time.sleep(1)
