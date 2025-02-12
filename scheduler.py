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
import pytz

# The scheduler is set to UTC – all run_date values must be given in UTC.
scheduler = BackgroundScheduler(timezone=pytz.utc)


def init_scheduler():
    """Initializes and starts the scheduler."""
    scheduler.start()


def schedule_reminder(reminder_id, next_trigger_time, user_id, chat_id):
    """
    Schedules a job for a reminder at its next_trigger_time.
    (Assumes next_trigger_time is already in UTC.)
    """
    trigger = DateTrigger(run_date=next_trigger_time)
    job_id = f"reminder_{reminder_id}"
    scheduler.add_job(func=send_reminder_wrapper, trigger=trigger, id=job_id,
                      args=[user_id, chat_id, reminder_id])
    print(f"Scheduled reminder job {job_id} for {next_trigger_time}")


def send_reminder_wrapper(user_id, chat_id, reminder_id):
    """
    Wrapper that retrieves reminder details and sends the reminder message.
    """
    from modules.reminders import send_reminder_message  # Avoid circular dependency
    send_reminder_message(user_id, chat_id, reminder_id)


def schedule_summary(bot, user_id, chat_id, summary_schedule, summary_time, user_tz):
    """
    Schedules a summary report for the user using their chosen timezone.
    user_tz is a string (e.g. "Asia/Tehran") that is converted to a pytz timezone.
    """
    tz = pytz.timezone(user_tz)
    now = datetime.now(tz)
    if summary_schedule == 'daily':
        try:
            # Parse the summary time (HH:MM) as a naive datetime and then localize it
            summary_time_naive = datetime.strptime(summary_time, "%H:%M")
            summary_dt = tz.localize(datetime(
                year=now.year, month=now.month, day=now.day,
                hour=summary_time_naive.hour, minute=summary_time_naive.minute))
        except Exception as e:
            print("Error parsing summary time:", e)
            return
        if summary_dt < now:
            summary_dt += timedelta(days=1)
        # Convert to UTC for scheduling
        summary_dt_utc = summary_dt.astimezone(pytz.utc)
        trigger = DateTrigger(run_date=summary_dt_utc)
        job_id = f"summary_daily_{user_id}"
        scheduler.add_job(func=send_summary, trigger=trigger, id=job_id,
                          args=[bot, chat_id, user_id])
        print(f"Scheduled daily summary for user {user_id} at {summary_dt} (local), {summary_dt_utc} (UTC)")
    elif summary_schedule == 'custom':
        try:
            interval_hours = int(summary_time)
        except ValueError:
            return
        start_date = now + timedelta(hours=interval_hours)
        start_date_utc = start_date.astimezone(pytz.utc)
        trigger = IntervalTrigger(hours=interval_hours, start_date=start_date_utc, timezone=pytz.utc)
        job_id = f"summary_custom_{user_id}"
        scheduler.add_job(func=send_summary, trigger=trigger, id=job_id,
                          args=[bot, chat_id, user_id])
        print(f"Scheduled custom summary for user {user_id} every {interval_hours} hours, starting at {start_date} (local)")
    else:
        remove_job(f"summary_daily_{user_id}")
        remove_job(f"summary_custom_{user_id}")


def schedule_random_checkins(bot, user_id, chat_id, random_checkin_max, user_tz):
    """
    Schedules random check-in jobs for the user during the period 8:00 to 21:00 in the user's timezone.
    
    - If current time is before 8:00: schedules for today (8:00 to 21:00).
    - If current time is between 8:00 and 21:00: schedules for the remaining time today.
    - If current time is after 21:00: schedules for tomorrow (8:00 to 21:00).
    
    The available time window is divided into equal intervals, and one random check-in is
    scheduled within each interval.
    """
    import pytz  # ensure pytz is imported
    tz = pytz.timezone(user_tz)
    now = datetime.now(tz)
    
    # Define today's start and end (8:00 and 21:00)
    today_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=21, minute=0, second=0, microsecond=0)
    
    if now < today_start:
        # Before 8 AM: schedule for today
        start_time = today_start
        end_time = today_end
    elif now > today_end:
        # After 9 PM: schedule for tomorrow
        tomorrow = now + timedelta(days=1)
        start_time = tomorrow.replace(hour=8, minute=0, second=0, microsecond=0)
        end_time = tomorrow.replace(hour=21, minute=0, second=0, microsecond=0)
    else:
        # Now is between 8:00 and 21:00: schedule for the remaining time today.
        start_time = now
        end_time = today_end

    total_seconds = (end_time - start_time).total_seconds()
    if total_seconds <= 0 or random_checkin_max <= 0:
        return

    # Divide the available period into equal intervals.
    interval_length = total_seconds / random_checkin_max

    for i in range(random_checkin_max):
        # Each interval starts at:
        interval_start = start_time + timedelta(seconds=i * interval_length)
        # Pick a random offset within the interval:
        random_offset_seconds = random.randint(0, int(interval_length))
        run_date = interval_start + timedelta(seconds=random_offset_seconds)
        run_date_utc = run_date.astimezone(pytz.utc)
        job_id = f"random_checkin_{user_id}_{i}"
        scheduler.add_job(
            func=send_random_checkin,
            trigger=DateTrigger(run_date=run_date_utc),
            id=job_id,
            args=[bot, chat_id, user_id]
        )
        print(f"Scheduled random check-in {i} for user {user_id} at {run_date} (local), {run_date_utc} (UTC)")

def schedule_weekly_event_reminders(bot, user_id, chat_id, user_tz):
    """
    Schedules reminders for all weekly events for the user.
    Each reminder is set 30 minutes before the next occurrence,
    using the user's chosen timezone.
    """
    tz = pytz.timezone(user_tz)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, day_of_week, time_of_day FROM weekly_schedule WHERE user_id = ?", (user_id,))
    events = cursor.fetchall()
    conn.close()
    
    now = datetime.now(tz)
    weekdays = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
                "Friday": 4, "Saturday": 5, "Sunday": 6}
    for event in events:
        event_id = event["id"]
        title = event["title"]
        day_str = event["day_of_week"]  # e.g., "Monday"
        time_str = event["time_of_day"]  # Expected "HH:MM"
        
        event_weekday = weekdays.get(day_str, None)
        if event_weekday is None:
            continue
        try:
            hour, minute = map(int, time_str.split(":"))
        except Exception:
            continue
        
        # Compute the next occurrence date
        days_ahead = event_weekday - now.weekday()
        next_date = now + timedelta(days=days_ahead)
        next_event_naive = datetime(year=next_date.year, month=next_date.month, day=next_date.day, hour=hour, minute=minute)
        next_event_date = tz.localize(next_event_naive)
        if days_ahead < 0 or (days_ahead == 0 and now >= next_event_date):
            next_date = now + timedelta(days=days_ahead + 7)
            next_event_naive = datetime(year=next_date.year, month=next_date.month, day=next_date.day, hour=hour, minute=minute)
            next_event_date = tz.localize(next_event_naive)
        
        trigger_time = next_event_date - timedelta(minutes=30)
        if trigger_time < now:
            trigger_time += timedelta(days=7)
        trigger_time_utc = trigger_time.astimezone(pytz.utc)
        job_id = f"weekly_event_{event_id}_{user_id}"
        scheduler.add_job(func=send_weekly_event_reminder, trigger=DateTrigger(run_date=trigger_time_utc),
                          id=job_id, args=[bot, user_id, chat_id, event_id, title, next_event_date.strftime('%H:%M')])
        print(f"Scheduled weekly event reminder for event {event_id} for user {user_id} at {trigger_time} (local), {trigger_time_utc} (UTC)")


def send_weekly_event_reminder(bot, user_id, chat_id, event_id, title, event_time_str):
    """
    Sends a reminder message for a weekly event.
    """
    bot.send_message(chat_id,
                     f"Reminder: Your weekly event '{title}' is scheduled to start at {event_time_str} (in 30 minutes).")


def schedule_nightly_tomorrow_summary(bot, user_id, chat_id, user_tz):
    """
    Schedules a daily job at 21:00 (user's local time) that sends a summary of tomorrow's weekly events.
    """
    # CronTrigger accepts a timezone parameter, so we pass the user's tz.
    trigger = CronTrigger(hour=21, minute=0, timezone=pytz.timezone(user_tz))
    job_id = f"nightly_tomorrow_summary_{user_id}"
    scheduler.add_job(func=send_tomorrow_weekly_summary, trigger=trigger, id=job_id,
                      args=[bot, user_id, chat_id])
    print(f"Scheduled nightly summary for user {user_id} at 21:00 {user_tz}")


def send_tomorrow_weekly_summary(bot, user_id, chat_id):
    """
    Retrieves weekly events for tomorrow and sends a summary message.
    (Assumes that events are stored in a format consistent with the user’s local time.)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_weekday = tomorrow.strftime("%A")
    cursor.execute("SELECT title, time_of_day FROM weekly_schedule WHERE user_id = ? AND day_of_week = ?",
                   (user_id, tomorrow_weekday))
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


def send_due_and_upcoming_summary(bot, user_id, chat_id, user_tz):
    """
    Sends a summary of items due for today and items upcoming in the next 30 minutes.
    Uses the user's timezone for determining today’s window.
    """
    tz = pytz.timezone(user_tz)
    now = datetime.now(tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query tasks due today
    cursor.execute("SELECT title, due_date FROM tasks WHERE user_id = ? AND due_date BETWEEN ? AND ?",
                   (user_id, today_start, today_end))
    tasks = cursor.fetchall()
    
    # Query reminders due today
    cursor.execute("SELECT title, next_trigger_time FROM reminders WHERE user_id = ? AND next_trigger_time BETWEEN ? AND ?",
                   (user_id, today_start, today_end))
    reminders = cursor.fetchall()
    
    # Query countdowns with event_datetime today
    cursor.execute("SELECT title, event_datetime FROM countdowns WHERE user_id = ? AND event_datetime BETWEEN ? AND ?",
                   (user_id, today_start, today_end))
    countdowns = cursor.fetchall()
    
    # Query upcoming items in the next 30 minutes
    upcoming_end = now + timedelta(minutes=30)
    cursor.execute("SELECT title, due_date FROM tasks WHERE user_id = ? AND due_date BETWEEN ? AND ?",
                   (user_id, now, upcoming_end))
    tasks_upcoming = cursor.fetchall()
    cursor.execute("SELECT title, next_trigger_time FROM reminders WHERE user_id = ? AND next_trigger_time BETWEEN ? AND ?",
                   (user_id, now, upcoming_end))
    reminders_upcoming = cursor.fetchall()
    cursor.execute("SELECT title, event_datetime FROM countdowns WHERE user_id = ? AND event_datetime BETWEEN ? AND ?",
                   (user_id, now, upcoming_end))
    countdowns_upcoming = cursor.fetchall()
    conn.close()
    
    summary_lines = ["Summary for Today:"]
    if tasks:
        summary_lines.append("Tasks due today:")
        for row in tasks:
            summary_lines.append(f"- {row[0]} at {row[1].strftime('%H:%M')}")
    if reminders:
        summary_lines.append("Reminders due today:")
        for row in reminders:
            summary_lines.append(f"- {row[0]} at {row[1].strftime('%H:%M')}")
    if countdowns:
        summary_lines.append("Countdown events today:")
        for row in countdowns:
            summary_lines.append(f"- {row[0]} at {row[1].strftime('%H:%M')}")
    
    summary_lines.append("\nUpcoming in next 30 minutes:")
    if tasks_upcoming:
        summary_lines.append("Tasks:")
        for row in tasks_upcoming:
            summary_lines.append(f"- {row[0]} at {row[1].strftime('%H:%M')}")
    if reminders_upcoming:
        summary_lines.append("Reminders:")
        for row in reminders_upcoming:
            summary_lines.append(f"- {row[0]} at {row[1].strftime('%H:%M')}")
    if countdowns_upcoming:
        summary_lines.append("Countdowns:")
        for row in countdowns_upcoming:
            summary_lines.append(f"- {row[0]} at {row[1].strftime('%H:%M')}")
    
    if len(summary_lines) == 1:
        summary_lines.append("No items due today or upcoming in the next 30 minutes.")
    
    summary_message = "\n".join(summary_lines)
    bot.send_message(chat_id, summary_message)


def schedule_due_and_upcoming_summary(bot, user_id, chat_id, user_tz):
    """
    Schedules a job that every 30 minutes sends a summary of items due and upcoming.
    """
    # The interval trigger is independent of timezone.
    trigger = IntervalTrigger(minutes=30, timezone=pytz.utc)
    job_id = f"due_upcoming_summary_{user_id}"
    scheduler.add_job(func=send_due_and_upcoming_summary, trigger=trigger, id=job_id,
                      args=[bot, user_id, chat_id, user_tz])
    print(f"Scheduled due/upcoming summary for user {user_id} every 30 minutes")
