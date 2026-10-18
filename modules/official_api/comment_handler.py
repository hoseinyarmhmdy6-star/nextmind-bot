import random
from config import KEYWORD_TRIGGERS, COMMENT_REPLY_VARIATIONS, FOLLOW_GATE_MESSAGE
from database import is_comment_processed, log_comment, update_user_status, get_user_lead
from modules.official_api.meta_api import meta_api

def process_comment_event(event_data: dict):
    """
    Processes a webhook comment event.
    Event data structure from Meta Graph API:
    {
        "id": "comment_id_123",
        "text": "کتاب رو بفرستید",
        "from": {"id": "user_ig_id", "username": "user123"},
        "media": {"id": "post_id_456"}
    }
    """
    comment_id = event_data.get("id")
    text = event_data.get("text", "").strip().lower()
    user_info = event_data.get("from", {})
    user_id = str(user_info.get("id", ""))
    username = user_info.get("username", "مخاطب عزیز")
    post_id = str(event_data.get("media", {}).get("id", ""))

    if not comment_id or not user_id:
        return

    # 1. Deduplication check: Avoid double replies
    if is_comment_processed(comment_id):
        print(f"[Comment Handler] Comment {comment_id} was already processed. Skipping.")
        return

    # 2. Check for matching keywords
    matched_keyword = None
    target_rule = None
    for keyword, rule in KEYWORD_TRIGGERS.items():
        if keyword.lower() in text:
            matched_keyword = keyword
            target_rule = rule
            break

    if not matched_keyword:
        print(f"[Comment Handler] No trigger keyword found in: '{text}'.")
        return

    print(f"[Comment Handler] Matched keyword '{matched_keyword}' from @{username}")

    # 3. Post a public reply to the comment
    reply_comment = random.choice(COMMENT_REPLY_VARIATIONS)
    meta_api.reply_to_comment(comment_id, reply_comment)

    # 4. Check Follow Gate condition
    existing_lead = get_user_lead(user_id)
    is_following = existing_lead["is_following"] if existing_lead else False

    if target_rule.get("require_follow", False) and not is_following:
        # Prompt user to follow first
        dm_text = (
            f"سلام {username} عزیز! 🌟\n\n"
            f"برای دریافت محتوای اختصاصی «{matched_keyword}»، لطفاً ابتدا پیج @nextmind.hq رو فالو کن.\n\n"
            f"بعد از فالو کردن، همین‌جا کلمه «فالو کردم» یا مجدداً «{matched_keyword}» رو بفرست تا لینک بلافاصله باز بشه! ❤️"
        )
        meta_api.send_dm(user_id, dm_text)
        update_user_status(user_id, username, is_following=False, keyword=matched_keyword, delivered=False)
    else:
        # User already follows or no follow requirement: Deliver lead magnet directly
        dm_text = target_rule["reply_text"]
        meta_api.send_dm(user_id, dm_text)
        update_user_status(user_id, username, is_following=True, keyword=matched_keyword, delivered=True)

    # 5. Log processed comment
    log_comment(comment_id, post_id, user_id, username, text, matched_keyword, dm_sent=True)
