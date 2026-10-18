from config import KEYWORD_TRIGGERS
from database import get_user_lead, update_user_status, log_dm
from modules.official_api.meta_api import meta_api
from modules.ai_assistant.gemini_bot import ai_assistant

FOLLOW_CONFIRMATION_KEYWORDS = ["فالو کردم", "دنبال کردم", "فالو شد", "انجام شد", "done", "followed"]

def process_dm_event(sender_id: str, message_text: str, username: str = "عزیز"):
    """
    Processes incoming Direct Message from Instagram user.
    """
    text_clean = message_text.strip().lower()
    log_dm(sender_id, username, "user", message_text)

    # 1. Check if user is confirming they followed (Unlocking gated content)
    if any(k in text_clean for k in FOLLOW_CONFIRMATION_KEYWORDS):
        lead = get_user_lead(sender_id)
        if lead and lead.get("last_keyword"):
            kw = lead["last_keyword"]
            rule = KEYWORD_TRIGGERS.get(kw)
            if rule:
                response = f"خیلی ممنون از همراهیتون! ❤️\nهدیه شما:\n\n{rule['reply_text']}"
                meta_api.send_dm(sender_id, response)
                update_user_status(sender_id, username, is_following=True, keyword=kw, delivered=True)
                log_dm(sender_id, username, "bot", response)
                return

    # 2. Check direct keyword triggers in DM
    for keyword, rule in KEYWORD_TRIGGERS.items():
        if keyword.lower() in text_clean:
            response = rule["reply_text"]
            meta_api.send_dm(sender_id, response)
            update_user_status(sender_id, username, is_following=True, keyword=keyword, delivered=True)
            log_dm(sender_id, username, "bot", response)
            return

    # 3. If no static keyword matched: Delegate to AI Assistant (Gemini)
    ai_reply = ai_assistant.generate_reply(message_text, username=username)
    meta_api.send_dm(sender_id, ai_reply)
    log_dm(sender_id, username, "ai", ai_reply)
