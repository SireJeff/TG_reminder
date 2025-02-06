"""
modules/summaries.py

This module implements the Summaries & Reports functionality.
It generates a summary report for the user that includes:
  - Pending Tasks (with due dates)
  - Goals in progress (with frequency and next check date)
  - Upcoming Reminders (in the next 24 hours)
  - Countdowns (with computed time left until the event)
  - Optionally, a random quote (if any exists for the user)

Key functions:
  - generate_summary(user_id): Returns a formatted summary string.
  - send_summary(bot, chat_id, user_id): Sends the summary to the user.
  - get_random_quote(user_id): Retrieves a random quote from the database.
"""

from datetime import datetime, timedelta
from database import get_db_connection

def generate_summary(user_id):
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
        summary_lines.append("**Pending Tasks:**")
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
                due_str = "No due date"
            summary_lines.append(f"- {title} (Due: {due_str})")
    else:
        summary_lines.append("No pending tasks.")
    
    # --- Active Goals ---
    cursor.execute("""
        SELECT title, frequency, next_check_date 
        FROM goals 
        WHERE user_id = ? AND status = 'in_progress' 
        ORDER BY created_at DESC
    """, (user_id,))
    goals = cursor.fetchall()
    if goals:
        summary_lines.append("\n**Goals in Progress:**")
        for goal in goals:
            title = goal["title"]
            frequency = goal["frequency"]
            next_check_date = goal["next_check_date"]
            if next_check_date:
                try:
                    next_check_dt = datetime.strptime(next_check_date, "%Y-%m-%d %H:%M:%S")
                    next_check_str = next_check_dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    next_check_str = next_check_date
            else:
                next_check_str = "N/A"
            summary_lines.append(f"- {title} ({frequency.capitalize()} | Next: {next_check_str})")
    else:
        summary_lines.append("\nNo active goals.")
    
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
        summary_lines.append("\n**Upcoming Reminders (next 24 hours):**")
        for rem in reminders:
            title = rem["title"]
            trigger_time = rem["next_trigger_time"]
            try:
                trigger_dt = datetime.strptime(trigger_time, "%Y-%m-%d %H:%M:%S")
                trigger_str = trigger_dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                trigger_str = trigger_time
            summary_lines.append(f"- {title} (At: {trigger_str})")
    else:
        summary_lines.append("\nNo reminders in the next 24 hours.")
    
    # --- Countdowns ---
    cursor.execute("""
        SELECT title, event_datetime 
        FROM countdowns 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (user_id,))
    countdowns = cursor.fetchall()
    if countdowns:
        summary_lines.append("\n**Countdowns:**")
        for cd in countdowns:
            title = cd["title"]
            event_datetime = cd["event_datetime"]
            try:
                event_dt = datetime.strptime(event_datetime, "%Y-%m-%d %H:%M:%S")
                delta = event_dt - now
                if delta.total_seconds() < 0:
                    time_left = "Event passed"
                else:
                    days = delta.days
                    hours, rem = divmod(delta.seconds, 3600)
                    minutes, _ = divmod(rem, 60)
                    time_left = f"{days}d {hours}h {minutes}m left"
            except Exception:
                time_left = event_datetime
            summary_lines.append(f"- {title}: {time_left}")
    else:
        summary_lines.append("\nNo active countdowns.")
    
    conn.close()
    
    # --- Optional Random Quote ---
    quote = get_random_quote(user_id)
    if quote:
        summary_lines.append("\n**Quote of the Day:**")
        summary_lines.append(f"_{quote}_")
    
    return "\n".join(summary_lines)

def send_summary(bot, chat_id, user_id):
    """
    Generates and sends the summary report to the user.
    """
    summary_text = generate_summary(user_id)
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
