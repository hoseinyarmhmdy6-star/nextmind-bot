import time
import random
from database import (
    save_competitor_leads, get_pending_competitor_leads, mark_lead_followed,
    get_today_followed_count
)
from modules.automation.insta_client import insta_manager
from config import SAFETY_SETTINGS, TARGET_COMPETITORS

def get_live_target_competitors():
    """دریافت بلادرنگ لیست رقبای افزوده شده از سرور کلودفلر تا هر پیج جدیدی فوراً وارد چرخه تعامل شود"""
    try:
        import urllib.request, json
        req = urllib.request.Request(
            "https://nextmind-bot.hoseinyarmhmdy6.workers.dev/api/competitors",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        res = urllib.request.urlopen(req, timeout=4)
        comps = json.loads(res.read())
        if comps and isinstance(comps, list):
            usernames = [c["username"] for c in comps if c.get("username")]
            if usernames:
                return usernames
    except Exception:
        pass
    return TARGET_COMPETITORS

def scrape_competitor_audience(competitor_username: str, count: int = 30):
    """
    استخراج فالوورهای فعال پیج‌های رقیب در حوزه هوش مصنوعی و ذخیره در صف تعامل
    """
    client = insta_manager.client
    print(f"[Growth] بررسی پیج هدف هوش مصنوعی @{competitor_username}...")
    
    try:
        user_id = client.user_id_from_username(competitor_username)
        print(f"[Growth] در حال استخراج {count} مخاطب علاقه‌مند از @{competitor_username}...")
        followers_dict = client.user_followers(user_id, amount=count)
        
        leads = []
        for fid, fuser in followers_dict.items():
            # رد کردن اکانت‌های بدون عکس یا بدون نام کاربری مناسب
            if not fuser.is_private:
                leads.append({
                    "id": str(fid),
                    "username": fuser.username
                })
            
        save_competitor_leads(leads, competitor=competitor_username)
        print(f"[Growth] ✓ تعداد {len(leads)} مخاطب بالقوه از @{competitor_username} ذخیره شد.")
        return leads
    except Exception as e:
        print(f"[Growth Error] خطا در دریافت مخاطبان پیج @{competitor_username}: {e}")
        return []

def run_safe_growth_tick(max_targets: int = 1):
    """
    اجرای یک مرحله جذب ارگانیک و ایمن با رعایت کامل سقف روزانه اینستاگرام (Anti-Ban)
    """
    # سیاست قطعی و بدون تغییر: پیج @nextmind.hq هرگز هیچ کاربری را فالو نمی‌کند (Zero Following)
    # کنترل ایمنی صرفاً بر اساس سقف لایک و تعامل ارگانیک روزانه انجام می‌شود
    max_daily_engagements = SAFETY_SETTINGS.get("max_likes_per_day", 60)
    today_engaged = get_today_followed_count()

    if today_engaged >= max_daily_engagements:
        return 0

    pending = get_pending_competitor_leads(limit=max_targets)
    if not pending:
        # اگر صف خالی است، از لیست رقبای هدف اکانت‌های جدید اضافه شود
        live_comps = get_live_target_competitors()
        target_page = random.choice(live_comps)
        scrape_competitor_audience(target_page, count=25)
        pending = get_pending_competitor_leads(limit=max_targets)
        if not pending:
            return 0

    client = insta_manager.client
    engaged_count = 0

    for target in pending:
        username = target["username"]
        uid = target["user_id"]
        liked_count = 0
        
        try:
            print(f"[Growth] 🎯 جذب مخاطب ارگانیک: تعامل امن با @{username}...")
            
            # ۱. لایک ۱ پست اخیر برای جلب توجه ارگانیک
            try:
                medias = client.user_medias(int(uid), amount=1)
                for media in medias:
                    client.media_like(media.id)
                    liked_count += 1
                    time.sleep(3)
            except Exception:
                pass

            # ۲. مشاهده هوشمند استوری کاربر هدف برای قرارگیری نام @nextmind.hq در لیست بازدیدکنندگان (۱۰۰٪ بدون فالو)
            try:
                user_stories = client.user_stories(int(uid))
                if user_stories:
                    story_ids = [s.id for s in user_stories[:2]]
                    client.story_seen(story_ids)
                    print(f"[Growth]  👁️ استوری کاربر @{username} مشاهده شد (جذب ارگانیک بدون فالو).")
            except Exception:
                pass

            # ⛔ قانون ممنوعیت مطلق فالو: پیج @nextmind.hq هیچ کاربری را فالو نمی‌کند تا Following همیشه صفر بماند.

            mark_lead_followed(uid, liked_count=liked_count)
            engaged_count += 1

            try:
                from monitor_service import push_growth_activity
                push_growth_activity(
                    action_type="story_view",
                    title="تعامل ارگانیک بدون فالو (مشاهده استوری و لایک)",
                    desc=f"لایک محتوا و مشاهده استوری مخاطب هدف @{username} با رعایت کامل سقف ایمنی و حفظ عدد صفر فالووینگ پیج.",
                    target=f"@{username}",
                    source="موتور جذب بدون فالو"
                )
            except Exception:
                pass

            # ۳. تأخیر تصادفی شبه‌انسانی برای امنیت کامل
            insta_manager.human_delay(
                SAFETY_SETTINGS["min_delay_between_actions"],
                SAFETY_SETTINGS["max_delay_between_actions"]
            )

        except Exception as e:
            print(f"[Growth Error] خطا در پردازش @{username}: {e}")
            mark_lead_followed(uid, liked_count=0)

    return engaged_count
