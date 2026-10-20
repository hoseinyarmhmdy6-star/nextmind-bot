import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import random
from colorama import Fore, Style, init
from config import INSTA_USERNAME, INSTA_PASSWORD, INSTA_SESSIONID, KEYWORD_TRIGGERS, COMMENT_REPLY_VARIATIONS, FOLLOW_GATE_MESSAGE
from database import (
    is_comment_processed, log_comment, get_user_lead, update_user_status,
    log_dm, get_stats, is_dm_processed, log_processed_dm
)
from modules.automation.insta_client import insta_manager
from modules.ai_assistant.gemini_bot import ai_assistant
from modules.automation.audience_engine import (
    match_keyword_intent, is_follow_confirmation, get_viral_comment_reply,
    generate_follow_gate_message, generate_reward_unlocked_message
)
from modules.automation.competitor_growth import run_safe_growth_tick

init(autoreset=True)

def sync_to_worker_inbox(username, user_message, bot_reply):
    """همگام‌سازی بلادرنگ پیام‌های رد و بدل شده با پنل کلودفلر ورکر"""
    try:
        import urllib.request
        import json
        payload = json.dumps({
            "username": username,
            "user_message": user_message,
            "bot_reply": bot_reply,
            "time": time.strftime('%H:%M')
        }).encode('utf-8')
        req = urllib.request.Request(
            "https://nextmind-bot.hoseinyarmhmdy6.workers.dev/api/inbox/push",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

def sync_session_to_worker():
    """همگام‌سازی نشست لاگین اینستاگرام با سرور ابری کلودفلر برای کارکرد ۲۴ ساعته دکمه‌ها حتی هنگام خاموش بودن لپ‌تاپ"""
    try:
        import os
        import json
        import urllib.request
        session_path = os.path.join(os.path.dirname(__file__), "insta_session.json")
        if os.path.exists(session_path):
            with open(session_path, "r", encoding="utf-8") as f:
                sess_data = json.load(f)
            req = urllib.request.Request(
                "https://nextmind-bot.hoseinyarmhmdy6.workers.dev/api/sync-session",
                data=json.dumps(sess_data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
            )
            urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

def sync_to_worker_stats(followers: int, posts: int = 3, following: int = 0):
    """همگام‌سازی بلادرنگ آمار زنده پیج با کلودفلر ورکر"""
    try:
        import urllib.request
        import json
        payload = json.dumps({
            "followers_count": followers,
            "media_count": posts,
            "following_count": following
        }).encode('utf-8')
        req = urllib.request.Request(
            "https://nextmind-bot.hoseinyarmhmdy6.workers.dev/api/account",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

def push_growth_activity(action_type: str, title: str, desc: str, target: str, source: str = "پایشگر زنده اینستاگرام"):
    """ارسال یک اقدام ثبت‌شده جذب مخاطب به ژورنال روزانه در کلادفلر"""
    try:
        import urllib.request
        import json
        payload = json.dumps({
            "type": action_type,
            "title": title,
            "desc": desc,
            "target": target,
            "source": source
        }).encode('utf-8')
        req = urllib.request.Request(
            "https://nextmind-bot.hoseinyarmhmdy6.workers.dev/api/growth-journal",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

class InstagramDirectMonitor:
    def __init__(self):
        self.client = insta_manager.client
        self.last_followers = None

    def start(self):
        print(Fore.CYAN + """
=============================================================
   🚀 NextMind HQ - ربات اختصاصی و مستقیم اینستاگرام 🚀
   بدون نیاز به فیسبوک • اتوماسیون کامل کامنت، دایرکت و هوش مصنوعی
=============================================================
        """)
        
        if not INSTA_PASSWORD and not INSTA_SESSIONID:
            print(Fore.RED + "[خطا] رمز عبور یا SessionID اینستاگرام در فایل .env وارد نشده است.")
            print(Fore.YELLOW + "لطفاً فایل .env را باز کنید و جلوی INSTA_PASSWORD یا INSTA_SESSIONID مقدار مربوطه را وارد کنید.\n")
            return

        print(Fore.YELLOW + f"[*] در حال ورود به حساب @{INSTA_USERNAME}...")
        logged_in = insta_manager.login()
        if not logged_in:
            print(Fore.RED + "[-] ورود ناموفق بود. لطفاً نام کاربری و رمز را بررسی کنید.")
            return

        print(Fore.GREEN + f"[+] ورود با موفقیت انجام شد! حساب @{INSTA_USERNAME} آماده فعالیت است.")
        print(Fore.GREEN + "[+] پایش لحظه‌ای کامنت‌ها، دایرکت‌ها و هوش مصنوعی آغاز شد...\n")

        self.run_loop()

    def run_loop(self):
        loop_count = 0
        while True:
            try:
                loop_count += 1
                
                # 0. پایش و همگام‌سازی آمار زنده پیج با داشبورد کلودفلر (فالوورها و پست‌ها)
                if loop_count % 2 == 1:
                    self.sync_live_profile()

                # 1. پایش پیام‌های دایرکت جدید (سریع، بلادرنگ و پرسرعت در هر دور)
                self.check_direct_messages()

                # 2. پایش کامنت‌های آخرین پست‌ها (هر ۳ دور یک‌بار، حدود هر ۳۵ الی ۵۰ ثانیه)
                if loop_count % 3 == 0:
                    self.check_latest_comments()

                # 3. جذب ارگانیک و تعامل مداوم با مخاطبان هدف هوش مصنوعی (هر ۱۵ دور یک‌بار، حدود ۲.۵ دقیقه)
                if loop_count % 15 == 0:
                    try:
                        run_safe_growth_tick(max_targets=1)
                    except Exception as eg:
                        print(Fore.RED + f"[خطای جذب ارگانیک] {eg}")

                # تأخیر سریع و بهینه (۸ تا ۱۴ ثانیه) برای پاسخگویی فوق‌العاده سریع به کاربران در دایرکت
                sleep_time = random.randint(8, 14)
                print(Fore.BLACK + Style.BRIGHT + f"[{time.strftime('%H:%M:%S')}] پایش بلادرنگ فعال است. بررسی بعدی تا {sleep_time} ثانیه دیگر...")
                time.sleep(sleep_time)

            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n[!] ربات با دستور شما متوقف شد.")
                break
            except Exception as e:
                print(Fore.RED + f"[خطای حلقه اصلی] {e}")
                time.sleep(10)

    def sync_live_profile(self):
        """استعلام و همگام‌سازی مستقیم آمار زنده پیج (فالوورها و پست‌ها) با داشبورد کلودفلر بدون کش"""
        try:
            if hasattr(self.client, '_user_cache'):
                self.client._user_cache.clear()
            user = self.client.user_info_by_username(INSTA_USERNAME, use_cache=False)
            if self.last_followers is not None and user.follower_count > self.last_followers:
                diff = user.follower_count - self.last_followers
                push_growth_activity(
                    action_type="follow",
                    title="فالوور هدف جدید جذب شد!",
                    desc=f"افزایش ارگانیک {diff} فالوور جدید (مجموع: {user.follower_count} فالوور) شناسایی و ثبت شد.",
                    target=f"فالوور جدید @nextmind.hq",
                    source="پایشگر زنده اینستاگرام"
                )
            self.last_followers = user.follower_count
            sync_to_worker_stats(user.follower_count, user.media_count, user.following_count)
            sync_session_to_worker()
            print(Fore.CYAN + f"  [Live Sync] آمار زنده پیج با موفقیت همگام شد: {user.follower_count} فالوور، {user.media_count} پست")
        except Exception as e:
            print(Fore.RED + f"  [Live Sync Error] {e}")

    def check_latest_comments(self):
        """بررسی پست‌های اخیر برای کامنت‌های جدید حاوی کلمات کلیدی با موتور جذب مخاطب"""
        try:
            user_id = self.client.user_id
            medias = self.client.user_medias(user_id, amount=3) # ۳ پست آخر
            
            for media in medias:
                comments = self.client.media_comments(media.id, amount=15)
                for c in comments:
                    cid = str(c.pk)
                    text = c.text.strip().lower()
                    author = c.user.username
                    author_id = str(c.user.pk)

                    # رد کردن کامنت‌های خود پیج
                    if author == INSTA_USERNAME:
                        continue

                    # اگر قبلاً پردازش شده، رد شود
                    if is_comment_processed(cid):
                        continue

                    # بررسی هوشمند کلمات کلیدی، نام‌های مستعار و غلط‌های املایی
                    matched_key, target_rule = match_keyword_intent(c.text)
                    if not matched_key:
                        continue

                    print(Fore.MAGENTA + f"\n🎯 کامنت جدید با کلمه «{matched_key}» از @{author}: \"{c.text}\"")

                    # ۱. پاسخ عمومی زیر کامنت با هوش مصنوعی یا متغیرهای وایرال
                    try:
                        reply_text = ai_assistant.generate_comment_reply(c.text, author, keyword=matched_key)
                    except Exception:
                        reply_text = get_viral_comment_reply(author, c.text, keyword=matched_key)

                    try:
                        self.client.media_comment(media.id, reply_text, replied_to_comment_id=int(cid))
                        print(Fore.GREEN + f"  ✓ پاسخ وایرال زیر کامنت ارسال شد: \"{reply_text}\"")
                    except Exception as e:
                        print(Fore.RED + f"  [خطا در ارسال کامنت] {e}")

                    # ۲. بررسی شرط فالو
                    is_following = False
                    try:
                        friendship = self.client.user_friendship_v1(author_id)
                        is_following = bool(friendship.followed_by)
                    except Exception as e:
                        lead = get_user_lead(author_id)
                        is_following = lead["is_following"] if lead else False

                    # ۳. ارسال دایرکت
                    if target_rule.get("require_follow", True) and not is_following:
                        dm_msg = generate_follow_gate_message(author, matched_key)
                        insta_manager.safe_direct_send(dm_msg, user_ids=[int(author_id)])
                        update_user_status(author_id, author, is_following=False, keyword=matched_key, delivered=False)
                        print(Fore.YELLOW + f"  🔒 پیام Follow-Gate برای @{author} ارسال شد.")
                    else:
                        dm_msg = generate_reward_unlocked_message(author, target_rule["reply_text"], keyword=matched_key)
                        insta_manager.safe_direct_send(dm_msg, user_ids=[int(author_id)])
                        update_user_status(author_id, author, is_following=True, keyword=matched_key, delivered=True)
                        print(Fore.GREEN + f"  🚀 هدیه اختصاصی برای @{author} در دایرکت تحویل داده شد.")

                    log_comment(cid, str(media.id), author_id, author, c.text, matched_key, dm_sent=True)
                    time.sleep(random.randint(4, 9))

        except Exception as e:
            print(Fore.RED + f"[خطا در پایش کامنت‌ها] {e}")

    def check_direct_messages(self):
        """پایش صندوق دایرکت برای پاسخ به سوالات با هوش مصنوعی، تایید فالو و ارسال کلمات کلیدی"""
        try:
            threads = self.client.direct_threads(amount=8)
            for t in threads:
                if not t.messages:
                    continue
                last_msg = t.messages[0]
                
                # فقط پیام‌هایی که مخاطب فرستاده و ما نفرستادیم
                if str(last_msg.user_id) == str(self.client.user_id):
                    continue

                msg_text = (last_msg.text or "").strip()
                if not msg_text:
                    continue

                msg_text_lower = msg_text.lower()
                author_id = str(last_msg.user_id)
                author = t.users[0].username if t.users else "کاربر"
                msg_id = str(last_msg.id)
                thread_id = str(t.id)

                # جلوگیری از پاسخ تکراری به یک پیام
                if is_dm_processed(msg_id):
                    continue

                lead = get_user_lead(author_id)
                is_following = lead["is_following"] if lead else False

                # حالت ۱: تایید فالو با بررسی هوشمند تمامی الگوهای عامیانه
                if is_follow_confirmation(msg_text):
                    kw = lead.get("last_keyword") if (lead and lead.get("last_keyword")) else "کد"
                    rule = KEYWORD_TRIGGERS.get(kw, KEYWORD_TRIGGERS.get("کد"))
                    if rule:
                        res = generate_reward_unlocked_message(author, rule['reply_text'], keyword=kw)
                        insta_manager.safe_direct_send(res, thread_ids=[thread_id])
                        update_user_status(author_id, author, is_following=True, keyword=kw, delivered=True)
                        log_processed_dm(msg_id, thread_id, author_id, author, msg_text, res)
                        sync_to_worker_inbox(author, msg_text, res)
                        print(Fore.GREEN + f"  ✓ کاربر @{author} با تایید هوشمند فالو قفل محتوای «{kw}» را باز کرد!")
                        time.sleep(random.randint(1, 3))
                        continue

                # حالت ۲: ارسال مستقیم کلمه کلیدی، مترادف‌ها یا غلط‌های املایی در دایرکت
                matched_kw, matched_rule = match_keyword_intent(msg_text)
                if matched_rule:
                    if matched_rule.get("require_follow", True) and not is_following:
                        res = generate_follow_gate_message(author, matched_kw)
                        update_user_status(author_id, author, is_following=False, keyword=matched_kw, delivered=False)
                        print(Fore.YELLOW + f"  🔒 ارسال Follow-Gate در دایرکت به @{author}.")
                    else:
                        res = generate_reward_unlocked_message(author, matched_rule["reply_text"], keyword=matched_kw)
                        update_user_status(author_id, author, is_following=True, keyword=matched_kw, delivered=True)
                        print(Fore.GREEN + f"  ✓ پاسخ مستقیم کلمه «{matched_kw}» به @{author} در دایرکت ارسال شد.")

                    insta_manager.safe_direct_send(res, thread_ids=[thread_id])
                    log_processed_dm(msg_id, thread_id, author_id, author, msg_text, res)
                    sync_to_worker_inbox(author, msg_text, res)
                    time.sleep(random.randint(1, 3))
                    continue

                # حالت ۳: پیام‌های عمومی، احوالپرسی (مثل «سلام»)، سوالات تخصصی و پرزنت فروش با جمینای
                print(Fore.YELLOW + f"\n💬 پیام دایرکت جدید از @{author}: \"{msg_text}\"")
                print(Fore.CYAN + f"  [*] در حال تولید پاسخ هوشمند توسط نکسوس (Gemini)...")

                history = []
                for m in reversed(t.messages[1:5]):
                    if m.text:
                        s = "کاربر" if str(m.user_id) != str(self.client.user_id) else "نکسوس"
                        history.append(f"{s}: {m.text.strip()}")

                reply_text = ai_assistant.generate_reply(msg_text, username=author, conversation_history=history)
                insta_manager.safe_direct_send(reply_text, thread_ids=[thread_id])
                log_processed_dm(msg_id, thread_id, author_id, author, msg_text, reply_text)
                sync_to_worker_inbox(author, msg_text, reply_text)
                print(Fore.GREEN + f"  ✓ پاسخ هوشمند به @{author} ارسال شد:\n\"{reply_text}\"\n")
                time.sleep(random.randint(1, 3))

        except Exception as e:
            print(Fore.RED + f"[خطا در پایش دایرکت‌ها] {e}")

if __name__ == "__main__":
    monitor = InstagramDirectMonitor()
    monitor.start()
