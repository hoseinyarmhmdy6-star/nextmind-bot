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

class InstagramDirectMonitor:
    def __init__(self):
        self.client = insta_manager.client

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
                
                # 1. پایش پیام‌های دایرکت جدید (سریع، بلادرنگ و پرسرعت در هر دور)
                self.check_direct_messages()

                # 2. پایش کامنت‌های آخرین پست‌ها (هر ۳ دور یک‌بار، حدود هر ۳۵ الی ۵۰ ثانیه)
                if loop_count % 3 == 0:
                    self.check_latest_comments()

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

    def check_latest_comments(self):
        """بررسی پست‌های اخیر برای کامنت‌های جدید حاوی کلمات کلیدی"""
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

                    # بررسی کلمات کلیدی
                    matched_key = None
                    target_rule = None
                    for kw, rule in KEYWORD_TRIGGERS.items():
                        if kw.lower() in text:
                            matched_key = kw
                            target_rule = rule
                            break

                    if not matched_key:
                        continue

                    print(Fore.MAGENTA + f"\n🎯 کامنت جدید با کلمه «{matched_key}» از @{author}: \"{c.text}\"")

                    # ۱. پاسخ عمومی زیر کامنت با هوش مصنوعی نکسوس
                    try:
                        reply_text = ai_assistant.generate_comment_reply(c.text, author, keyword=matched_key)
                    except Exception:
                        reply_text = random.choice(COMMENT_REPLY_VARIATIONS)

                    try:
                        self.client.media_comment(media.id, reply_text, replied_to_comment_id=int(cid))
                        print(Fore.GREEN + f"  ✓ پاسخ هوشمند زیر کامنت ارسال شد: \"{reply_text}\"")
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
                        dm_msg = (
                            f"سلام {author} عزیز! 🌟\n\n"
                            f"برای دریافت محتوای اختصاصی «{matched_key}»، لطفاً ابتدا پیج ما (@{INSTA_USERNAME}) رو فالو کن.\n\n"
                            f"بعد از فالو کردن، همین‌جا بفرست «فالو کردم» یا دوباره کلمه «{matched_key}» رو بفرست تا برات باز بشه! ❤️"
                        )
                        insta_manager.safe_direct_send(dm_msg, user_ids=[int(author_id)])
                        update_user_status(author_id, author, is_following=False, keyword=matched_key, delivered=False)
                        print(Fore.YELLOW + f"  🔒 پیام شرط فالو برای @{author} ارسال شد.")
                    else:
                        dm_msg = target_rule["reply_text"]
                        insta_manager.safe_direct_send(dm_msg, user_ids=[int(author_id)])
                        update_user_status(author_id, author, is_following=True, keyword=matched_key, delivered=True)
                        print(Fore.GREEN + f"  🚀 هدیه اختصاصی برای @{author} در دایرکت تحویل داده شد.")

                    log_comment(cid, str(media.id), author_id, author, c.text, matched_key, dm_sent=True)
                    time.sleep(random.randint(4, 9))

        except Exception as e:
            print(Fore.RED + f"[خطا در پایش کامنت‌ها] {e}")

    def check_direct_messages(self):
        """پایش صندوق دایرکت برای پاسخ به سوالات با هوش مصنوعی و تایید فالو"""
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

                # حالت ۱: تایید فالو
                if any(k in msg_text_lower for k in ["فالو کردم", "دنبال کردم", "فالو شد", "انجام شد", "done"]):
                    if lead and lead.get("last_keyword"):
                        kw = lead["last_keyword"]
                        rule = KEYWORD_TRIGGERS.get(kw)
                        if rule:
                            res = f"خیلی ممنون از همراهیتون @{author} عزیز! ❤️\nهدیه شما آماده شد:\n\n{rule['reply_text']}"
                            insta_manager.safe_direct_send(res, thread_ids=[thread_id])
                            update_user_status(author_id, author, is_following=True, keyword=kw, delivered=True)
                            log_processed_dm(msg_id, thread_id, author_id, author, msg_text, res)
                            sync_to_worker_inbox(author, msg_text, res)
                            print(Fore.GREEN + f"  ✓ کاربر @{author} با تایید فالو قفل محتوای «{kw}» را باز کرد!")
                            time.sleep(random.randint(1, 3))
                            continue

                # حالت ۲: ارسال مستقیم کلمه کلیدی (مانند «کد»، «پرامپت»)
                matched_kw = None
                matched_rule = None
                for kw, rule in KEYWORD_TRIGGERS.items():
                    if kw.lower() in msg_text_lower:
                        matched_kw = kw
                        matched_rule = rule
                        break

                if matched_rule:
                    res = matched_rule["reply_text"]
                    insta_manager.safe_direct_send(res, thread_ids=[thread_id])
                    update_user_status(author_id, author, is_following=True, keyword=matched_kw, delivered=True)
                    log_processed_dm(msg_id, thread_id, author_id, author, msg_text, res)
                    sync_to_worker_inbox(author, msg_text, res)
                    print(Fore.GREEN + f"  ✓ پاسخ مستقیم کلمه «{matched_kw}» به @{author} در دایرکت ارسال شد.")
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
