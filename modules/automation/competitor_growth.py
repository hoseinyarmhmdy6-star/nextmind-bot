import time
from database import save_competitor_leads, get_pending_competitor_leads, mark_lead_followed
from modules.automation.insta_client import insta_manager
from config import SAFETY_SETTINGS

def scrape_competitor_audience(competitor_username: str, count: int = 50):
    """
    Scrapes the most recent active followers of a target competitor page.
    Saves them to the database for gradual, safe outreach.
    """
    client = insta_manager.client
    print(f"[Growth] Finding user ID for competitor @{competitor_username}...")
    
    try:
        user_id = client.user_id_from_username(competitor_username)
        print(f"[Growth] Extracting {count} followers from competitor @{competitor_username}...")
        followers_dict = client.user_followers(user_id, amount=count)
        
        leads = []
        for fid, fuser in followers_dict.items():
            # Skip private accounts if desired, or keep all
            leads.append({
                "id": str(fid),
                "username": fuser.username
            })
            
        save_competitor_leads(leads, competitor=competitor_username)
        print(f"[Growth] Successfully saved {len(leads)} target accounts into outreach database!")
        return leads
    except Exception as e:
        print(f"[Growth Error] Failed to scrape competitor followers: {e}")
        return []

def run_safe_engagement_cycle(batch_size: int = 5, like_posts: bool = True, follow: bool = True):
    """
    Executes a controlled engagement cycle on pending competitor leads.
    Employs randomized human-like delays to protect the account reputation.
    """
    pending = get_pending_competitor_leads(limit=batch_size)
    if not pending:
        print("[Growth] No pending competitor accounts in database queue.")
        return 0

    client = insta_manager.client
    engaged_count = 0

    print(f"[Growth] Starting engagement batch for {len(pending)} targeted accounts...")

    for target in pending:
        username = target["username"]
        uid = target["user_id"]
        liked_count = 0
        
        try:
            print(f"[Growth] Engaging with @{username}...")
            
            # 1. Like recent 1-2 posts (shows genuine interest)
            if like_posts:
                try:
                    medias = client.user_medias(int(uid), amount=2)
                    for media in medias:
                        client.media_like(media.id)
                        liked_count += 1
                        time.sleep(4)
                except Exception as e:
                    print(f"[Growth Warning] Couldn't like posts of @{username}: {e}")

            # 2. Follow user
            if follow:
                client.user_follow(int(uid))
                print(f"[Growth] Followed @{username} successfully.")

            mark_lead_followed(uid, liked_count=liked_count)
            engaged_count += 1

            # 3. Safe human-like delay
            insta_manager.human_delay(
                SAFETY_SETTINGS["min_delay_between_actions"],
                SAFETY_SETTINGS["max_delay_between_actions"]
            )

        except Exception as e:
            print(f"[Growth Error] Error processing @{username}: {e}")
            time.sleep(10)

    print(f"[Growth] Engagement cycle complete. Engaged with {engaged_count} accounts.")
    return engaged_count
