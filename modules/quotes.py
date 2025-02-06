"""
modules/quotes.py

This module implements the Quotes functionality.
It allows users to add personal quotes, list all their quotes,
and retrieve a random quote (for inclusion in summaries or check-ins).

Quote Addition Flow:
1. The bot initiates the add-quote conversation when the user selects the Quotes option.
2. The bot asks: "Please enter the quote you want to add:"
3. The user sends the quote text.
4. The quote is saved in the database with the current timestamp.
5. Confirmation is sent back to the user.

Additional Helper Functions:
- list_quotes(user_id): Returns all quotes for the user.
- delete_quote(user_id, quote_id): Deletes a specified quote.
- get_random_quote(user_id): Retrieves a random quote from the database.
"""

from datetime import datetime
from telebot import types
from database import get_db_connection

# Global dictionary to track the quote addition conversation state per user.
# Structure: { user_id: { 'state': <state>, 'data': { ... } } }
quotes_states = {}

def start_add_quote(bot, chat_id, user_id):
    """
    Initiates the add-quote conversation.
    Call this when the user selects the "Quotes" option in the Main Menu.
    """
    quotes_states[user_id] = {
        'state': 'awaiting_quote_text',
        'data': {}
    }
    bot.send_message(chat_id, "Please enter the quote you want to add:")

def handle_quote_messages(bot, message):
    """
    Handles text messages for the add-quote conversation.
    This should be registered as a message handler for users in the quotes_states.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in quotes_states:
        return  # Not in an active quote conversation

    current_state = quotes_states[user_id]['state']
    text = message.text.strip()

    if current_state == 'awaiting_quote_text':
        # Save the provided quote in the database.
        save_quote_in_db(user_id, text)
        bot.send_message(chat_id, "Quote added successfully!")
        # Clear the conversation state.
        quotes_states.pop(user_id, None)
    else:
        bot.send_message(chat_id, "Unexpected input. Please follow the instructions.")

def save_quote_in_db(user_id, quote_text):
    """
    Saves a quote in the database under the user's record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO quotes (user_id, quote_text, created_at)
        VALUES (?, ?, ?)
    """, (user_id, quote_text, now))
    conn.commit()
    conn.close()

def list_quotes(user_id):
    """
    Retrieves a list of quotes for the given user.
    Returns a list of sqlite3.Row objects.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotes WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    quotes = cursor.fetchall()
    conn.close()
    return quotes

def delete_quote(user_id, quote_id):
    """
    Deletes a specific quote from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quotes WHERE id = ? AND user_id = ?", (quote_id, user_id))
    conn.commit()
    conn.close()

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
