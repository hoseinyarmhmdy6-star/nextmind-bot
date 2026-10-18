import os
import time
from config import INSTA_USERNAME, INSTA_PASSWORD, INSTA_SESSIONID
from instagrapi import Client

SESSION_FILE = "insta_session.json"

class InstagramClientManager:
    def __init__(self):
        self.client = Client()
        self.username = INSTA_USERNAME
        self.password = INSTA_PASSWORD
        self.session_id = INSTA_SESSIONID
        self.is_logged_in = False

    def login(self):
        """ورود مستقیم و مستقل به اینستاگرام بدون نیاز به تاییدیه فیسبوک"""
        # اولویت ۱: ورود با نشست ذخیره شده (Session)
        if os.path.exists(SESSION_FILE):
            try:
                print("[Automation] Loading saved session from file...")
                self.client.load_settings(SESSION_FILE)
                # بررسی زنده بودن نشست
                self.client.get_timeline_feed()
                self.is_logged_in = True
                print(f"[Automation] Successfully authenticated session as @{self.username}")
                return True
            except Exception as e:
                print(f"[Automation] Saved session invalid or expired: {e}")

        # اولویت ۲: ورود با SessionID در صورت وجود
        if self.session_id:
            try:
                print("[Automation] Attempting login with sessionid...")
                self.client.login_by_sessionid(self.session_id)
                self.client.dump_settings(SESSION_FILE)
                self.is_logged_in = True
                print(f"[Automation] Logged in via SessionID as @{self.username}")
                return True
            except Exception as e:
                print(f"[Automation] SessionID login failed: {e}")

        # اولویت ۳: ورود با نام کاربری و پسورد
        if self.password:
            try:
                print(f"[Automation] Logging in via username and password for @{self.username}...")
                self.client.login(self.username, self.password)
                self.client.dump_settings(SESSION_FILE)
                self.is_logged_in = True
                print(f"[Automation] Successfully logged in as @{self.username}")
                return True
            except Exception as e:
                print(f"[Automation] Direct username/password login failed: {e}")
                return False

        return False

    def safe_direct_send(self, text, thread_ids=None, user_ids=None):
        """
        ارسال ایمن و پایدار دایرکت با پشتیبانی کامل از Thread ID و User ID
        """
        try:
            if thread_ids:
                tid = str(thread_ids[0])
                return self.client.direct_answer(tid, text)
            if user_ids:
                uid = int(user_ids[0])
                return self.client.direct_send(text, user_ids=[uid])
        except Exception as e:
            print(f"[safe_direct_send native error] {e}, attempting broadcast fallback...")
            try:
                import json
                token = self.client.generate_mutation_token()
                kwargs = {
                    "action": "send_item",
                    "client_context": token,
                    "mutation_token": token,
                    "offline_threading_id": token,
                    "text": text,
                }
                if thread_ids:
                    kwargs["thread_ids"] = json.dumps([str(tid) for tid in thread_ids])
                if user_ids:
                    kwargs["recipient_users"] = json.dumps([[int(uid) for uid in user_ids]])

                return self.client.private_request(
                    "direct_v2/threads/broadcast/text/",
                    data=self.client.with_default_data(kwargs),
                    with_signature=False,
                )
            except Exception as e2:
                print(f"[safe_direct_send broadcast error] {e2}")
                return False

insta_manager = InstagramClientManager()
