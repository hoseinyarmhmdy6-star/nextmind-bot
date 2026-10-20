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

def scrape_competitor_audience(competitor_username: str, count: int = 35):
    """
    استخراج هوشمند و داغ مخاطبان فعال رقیب:
    ۱. کامنت‌گذاران آخرین ریلزها و پست‌ها (علاقه‌مندترین مخاطبان فعال هوش مصنوعی)
    ۲. لایک‌کنندگان ریلزهای پربازدید
    ۳. فالوورهای تازه و پابلیک
    """
    client = insta_manager.client
    print(f"[Growth] 🔍 بررسی عمیق پیج رقیب هوش مصنوعی @{competitor_username}...")
    
    try:
        user_id = client.user_id_from_username(competitor_username)
        leads = []
        seen_lead_ids = set()

        # ۱. استخراج کامنت‌گذاران ریلزهای اخیر (طلایی‌ترین مخاطبان که فعالانه به دنبال پرامپت و ابزار هستند)
        try:
            print(f"[Growth] 🎯 استخراج کامنت‌گذاران ریلزهای پربازدید @{competitor_username}...")
            clips = client.user_clips(user_id, amount=2)
            for clip in clips:
                try:
                    comments = client.media_comments(clip.id, amount=20)
                    for c in comments:
                        u = c.user
                        uid_str = str(u.pk)
                        if uid_str not in seen_lead_ids and u.username != competitor_username and not u.is_private:
                            seen_lead_ids.add(uid_str)
                            leads.append({"id": uid_str, "username": u.username})
                except Exception:
                    pass
        except Exception as e_clips:
            print(f"[Growth Note] ریلزهای رقیب: {e_clips}")

        # ۲. استخراج کامنت‌گذاران پست‌های اخیر (در صورت وجود پست‌های اسلایدی/آموزشی)
        try:
            if len(leads) < count:
                medias = client.user_medias(user_id, amount=2)
                for media in medias:
                    try:
                        comments = client.media_comments(media.id, amount=15)
                        for c in comments:
                            u = c.user
                            uid_str = str(u.pk)
                            if uid_str not in seen_lead_ids and u.username != competitor_username and not u.is_private:
                                seen_lead_ids.add(uid_str)
                                leads.append({"id": uid_str, "username": u.username})
                    except Exception:
                        pass
        except Exception:
            pass

        # ۳. استخراج فالوورهای تازه و عمومی (تکمیل صف)
        if len(leads) < count:
            try:
                needed = count - len(leads)
                followers_dict = client.user_followers(user_id, amount=min(needed + 20, 50))
                for fid, fuser in followers_dict.items():
                    fid_str = str(fid)
                    if fid_str not in seen_lead_ids and not fuser.is_private:
                        seen_lead_ids.add(fid_str)
                        leads.append({"id": fid_str, "username": fuser.username})
                    if len(leads) >= count:
                        break
            except Exception:
                pass

        save_competitor_leads(leads, competitor=competitor_username)
        print(f"[Growth] ✓ تعداد {len(leads)} مخاطب بالقوه، زنده و فعال از @{competitor_username} ذخیره شد.")
        return leads
    except Exception as e:
        print(f"[Growth Error] خطا در دریافت مخاطبان پیج @{competitor_username}: {e}")
        return []

def run_safe_growth_tick(max_targets: int = 1):
    """
    اجرای یک مرحله جذب ارگانیک قدرتمند، سریع و ایمن با رعایت کامل سقف ایمنی (Anti-Ban)
    """
    # قانون بدون تغییر: پیج @nextmind.hq هرگز هیچ کاربری را فالو نمی‌کند (Zero Following)
    max_daily_engagements = SAFETY_SETTINGS.get("max_likes_per_day", 80)
    today_engaged = get_today_followed_count()

    if today_engaged >= max_daily_engagements:
        return 0

    pending = get_pending_competitor_leads(limit=max_targets)
    if not pending or len(pending) < 3:
        # اگر صف کم است، فوراً از لیست رقبای هدف مخاطبان داغ استخراج شود
        live_comps = get_live_target_competitors()
        target_page = random.choice(live_comps)
        scrape_competitor_audience(target_page, count=30)
        pending = get_pending_competitor_leads(limit=max_targets)
        if not pending:
            return 0

    client = insta_manager.client
    engaged_count = 0

    for target in pending:
        username = target["username"]
        uid = target["user_id"]
        source_comp = target.get("competitor_source", "پیج‌های رقیب")
        liked_count = 0
        saw_story = False
        
        try:
            print(f"[Growth] 🎯 جذب مخاطب ارگانیک: تعامل امن با @{username} (از {source_comp})...")
            
            # ۱. مشاهده هوشمند استوری کاربر هدف برای قرارگیری نام و لوگوی شیک @nextmind.hq در لیست بازدیدکنندگان (۱۰۰٪ بدون فالو)
            try:
                user_stories = client.user_stories(int(uid))
                if user_stories:
                    story_ids = [s.id for s in user_stories[:3]]
                    client.story_seen(story_ids)
                    saw_story = True
                    print(f"[Growth]  👁️ استوری کاربر @{username} مشاهده شد (جذب هوشمند ارگانیک).")
            except Exception:
                pass

            # ۲. لایک ۱ پست یا ریلز اخیر برای جلب توجه و ارسال نوتیفیکیشن روی گوشی کاربر
            try:
                medias = client.user_medias(int(uid), amount=1)
                if not medias:
                    medias = client.user_clips(int(uid), amount=1)
                for media in medias:
                    client.media_like(media.id)
                    liked_count += 1
                    time.sleep(2)
            except Exception:
                pass

            # ⛔ قانون ممنوعیت مطلق فالو: پیج @nextmind.hq هیچ کاربری را فالو نمی‌کند تا Following همیشه صفر بماند.

            mark_lead_followed(uid, liked_count=liked_count)
            engaged_count += 1

            # ارسال گزارش به داشبورد کلودفلر
            try:
                from monitor_service import push_growth_activity
                action_title = "مشاهده استوری و لایک پست" if (saw_story and liked_count > 0) else ("مشاهده استوری" if saw_story else "لایک محتوای هدف")
                push_growth_activity(
                    action_type="story_view",
                    title=f"تعامل ارگانیک: {action_title}",
                    desc=f"تعامل هوشمند با مخاطب علاقه‌مند @{username} برگرفته از رقیب {source_comp} بدون فالو کردن (Following: 0 محفوظ).",
                    target=f"@{username}",
                    source=f"رقیب: @{source_comp}"
                )
            except Exception:
                pass

            # تاخیر تصادفی شبه‌انسانی برای امنیت کامل اکانت
            insta_manager.human_delay(
                SAFETY_SETTINGS.get("min_delay_between_actions", 4),
                SAFETY_SETTINGS.get("max_delay_between_actions", 8)
            )

        except Exception as e:
            print(f"[Growth Error] خطا در پردازش @{username}: {e}")
            mark_lead_followed(uid, liked_count=0)

    return engaged_count
