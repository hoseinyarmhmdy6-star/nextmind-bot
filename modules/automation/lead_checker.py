from modules.automation.insta_client import insta_manager
from config import INSTA_USERNAME

def check_user_follows_us(target_username: str) -> bool:
    """
    Checks if a target username is actively following our page.
    """
    client = insta_manager.client
    try:
        target_uid = client.user_id_from_username(target_username)
        # Check friendship status
        status = client.user_friendship(target_uid)
        # status.followed_by indicates if they follow us
        return bool(status.followed_by)
    except Exception as e:
        print(f"[Lead Checker Error] Could not verify friendship with @{target_username}: {e}")
        return False
