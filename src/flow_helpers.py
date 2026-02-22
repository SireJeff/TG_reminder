# flow_helpers.py
import logging

logger = logging.getLogger(__name__)

# Global variables to track messages.
flow_messages = {}       # { user_id: [msg_id, msg_id, ...] }
flow_user_messages = {}  # { user_id: [msg_id, msg_id, ...] }

# Global bot instance—must be set at startup.
BOT = None

def set_bot(bot_instance):
    """
    Set the global bot instance.
    Call this once in your bot.py after creating the bot.
    """
    global BOT
    BOT = bot_instance

def tracked_send_message(chat_id, user_id, text, **kwargs):
    """
    Sends a message using the global BOT instance and stores its message_id.
    This function does not require the bot parameter now.
    """
    global BOT
    if BOT is None:
        raise Exception("BOT instance not set in flow_helpers. Call set_bot(bot) first.")
    msg = BOT.send_message(chat_id, text, **kwargs)
    flow_messages.setdefault(user_id, []).append(msg.message_id)
    return msg

def tracked_user_message(message):
    """
    Tracks a user-sent message for later deletion.
    """
    user_id = message.from_user.id
    flow_user_messages.setdefault(user_id, []).append(message.message_id)

def clear_flow_messages(chat_id, user_id):
    """
    Deletes all tracked bot and user messages for the given user.
    """
    global BOT
    if BOT is None:
        raise Exception("BOT instance not set in flow_helpers. Call set_bot(bot) first.")
    if user_id in flow_messages:
        for msg_id in flow_messages[user_id]:
            try:
                BOT.delete_message(chat_id, msg_id)
            except Exception as e:
                logger.error(f"Failed to delete bot message {msg_id} for user {user_id}: {e}")
        flow_messages[user_id] = []
    if user_id in flow_user_messages:
        for msg_id in flow_user_messages[user_id]:
            try:
                BOT.delete_message(chat_id, msg_id)
            except Exception as e:
                logger.error(f"Failed to delete user message {msg_id} for user {user_id}: {e}")
        flow_user_messages[user_id] = []
