"""
scheduler.py

This module sets up the APScheduler BackgroundScheduler and registers scheduled jobs for:
  - Reminders: Schedules a job at each reminder's next_trigger_time.
  - Summaries: Schedules a summary report based on each user's summary schedule 
               (daily at a specific time or at custom intervals).
  - Random Check-Ins: Schedules random check-in messages for the user during the day.
  
It provides helper functions to initialize the scheduler, schedule jobs, and remove jobs when needed.
"""

import random
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

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
        # Convert summary_time (HH:MM) to a datetime today.
        try:
            summary_dt = datetime.strptime(summary_time, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day)
        except Exception:
            return
        # If the summary time has already passed today, schedule for tomorrow.
        if summary_dt < now:
            summary_dt += timedelta(days=1)
        trigger = DateTrigger(run_date=summary_dt)
        job_id = f"summary_daily_{user_id}"
        scheduler.add_job(func=send_summary, trigger=trigger, id=job_id,
                          args=[bot, chat_id, user_id])
    elif summary_schedule == 'custom':
        # summary_time is treated as an interval (in hours).
        try:
            interval_hours = int(summary_time)
        except ValueError:
            return
        trigger = IntervalTrigger(hours=interval_hours, start_date=now + timedelta(hours=interval_hours))
        job_id = f"summary_custom_{user_id}"
        scheduler.add_job(func=send_summary, trigger=trigger, id=job_id,
                          args=[bot, chat_id, user_id])
    else:
        # If summaries are disabled, remove any existing summary jobs.
        remove_job(f"summary_daily_{user_id}")
        remove_job(f"summary_custom_{user_id}")

def schedule_random_checkins(bot, user_id, chat_id, random_checkin_max):
    """
    Schedules random check-in jobs for the user for the current day.
    
    Parameters:
      - bot: The TeleBot instance.
      - user_id: Telegram user ID.
      - chat_id: Telegram chat ID.
      - random_checkin_max: The maximum number of random check-ins per day.
    
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

def remove_job(job_id):
    """Removes a scheduled job if it exists."""
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

if __name__ == "__main__":
    # For testing purposes, initialize the scheduler and keep the script running.
    init_scheduler()
    print("Scheduler is running...")
    while True:
        time.sleep(1)
