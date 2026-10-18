import os
import ssl
import json
import urllib.request
import urllib.parse
from config import GEMINI_API_KEY

# Telegram Credentials Loader
def get_telegram_creds():
    env_path = r'C:\Users\ark\.gemini\config\credentials.env'
    token = None
    chat_id = None
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('TELEGRAM_BOT_TOKEN_AETHER'):
                    token = line.split('=', 1)[1].strip().strip('"').strip("'")
                if line.startswith('TELEGRAM_CHAT_ID_AETHER'):
                    chat_id = line.split('=', 1)[1].strip().strip('"').strip("'")
    return token, chat_id

TG_TOKEN, TG_CHAT_ID = get_telegram_creds()

def send_telegram_alert(title: str, body: str, username: str = None):
    """ارسال نوتیفیکیشن فوری به بات تلگرام ادمین در صورت پیام‌های حساس یا لیدهای خرید"""
    if not TG_TOKEN or not TG_CHAT_ID:
        return
    try:
        ctx = ssl._create_unverified_context()
        text = f"🚨 *{title}*\n\n"
        if username:
            text += f"👤 کاربر اینستاگرام: @{username}\n🔗 لینک دایرکت: [ورود به چت](https://ig.me/m/{username})\n\n"
        text += f"💬 پیام: {body}\n\n📱 پیج: @nextmind.hq"
        
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": TG_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": "true"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, context=ctx, timeout=8)
    except Exception as e:
        print(f"[Telegram Alert Error] {e}")

NEXUS_PERSONA = """
شما «نکسوس» (Nexus) هستید؛ صدای رسمی، استراتژیست ارشد و فروشنده نخبه پیج اینستاگرام NextMind (@nextmind.hq).

🎯 هویت، رسالت و مسیر پیج:
- ماموریت اصلی: آموزش کاربردی و بی‌واسطه هوش مصنوعی؛ تبدیل کارهای ۱۰ ساعته به ۱۰ دقیقه و درآمدزایی از ابزارهای هوش مصنوعی.
- خط قرمز ما: هیچ‌وقت وقت مخاطب را با اخبار زرد، تئوری‌های خسته‌کننده کتابی یا مقدمه‌های کلیشه‌ای («در دنیای مدرن امروز...») تلف نمی‌کنیم!
- لحن گفتار: فوق‌العاده صمیمی، رک، پرانرژی، کاریزماتیک، ریتمیک، همراه با ایموجی‌های هوشمندانه (🧠⚡🚀😉).
- تکنیک فروش و مذاکره (Sales Closer):
  اگر مخاطب سوال یا تردیدی داشت (مثلاً گفت با گوشی میشه؟ سخته؟ یا قیمتش چنده؟)، با اعتمادبه‌نفس بالا، همدلی و صمیمیت کامل راهنماییش کن. بهش اطمینان بده که همه ابزارها تست‌شده، ساده و پولساز هستن و دعوتش کن برای دریافت پکیج پرامپت‌ها یا شروع یادگیری کلمه «کد» رو بفرسته.
"""

class AIAssistant:
    def __init__(self):
        self.enabled = bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here")
        self.client = None
        self.model_name = "models/gemini-3.8-flash"
        if self.enabled:
            try:
                from google import genai
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                print(f"[AI Assistant Init Warning] {e}")

    def generate_reply(self, user_message: str, username: str = "عزیز", conversation_history: list = None) -> str:
        """پاسخ چندمرحله‌ای (Multi-turn) هوشمند به عنوان فروشنده نخبه در دایرکت اینستاگرام"""
        # تشخیص کلمات خرید یا نیاز به ادمین برای هشدار فوری تلگرام
        buy_keywords = ["خرید", "قیمت", "هزینه", "مشاوره", "ادمین", "پشتیبان", "شماره", "دوره", "همکاری", "تلفن", "کارت"]
        if any(kw in user_message for kw in buy_keywords):
            send_telegram_alert(
                title="🔥 لید داغ اینستاگرام / درخواست خرید یا ادمین",
                body=user_message,
                username=username
            )

        if not self.enabled or not self.client:
            return f"سلام {username} عزیز! 🌸 پیام شما دریافت شد. برای دریافت رایگان پکیج پرامپت‌ها کلمه «کد» رو بفرستید!"

        try:
            history_text = ""
            if conversation_history:
                history_text = "\nسوابق پیام‌های قبلی این گفتگو:\n" + "\n".join([f"- {msg}" for msg in conversation_history[-4:]]) + "\n"

            prompt = f"""
{NEXUS_PERSONA}
{history_text}
کاربر @{username} در دایرکت پیام زیر را ارسال کرده است:
"{user_message}"

وظیفه شما:
به عنوان «نکسوس»، یک پاسخ جذاب، کاریزماتیک، کوتاه (۲ الی ۴ خط)، بسیار صمیمی و هدایت‌کننده بنویسید.
تمام ابهامات مخاطب را برطرف کنید و او را با اشتیاق به سمت اقدام (ارسال کلمه «کد» یا بررسی لینک هدیه) راهنمایی کنید.
اگر حس کردی سوالش خیلی تخصصی یا قصد خرید جدی دارد، به او بگو پیامش را برای ادمین هم علامت‌گذاری کردی تا شخصاً پاسخ دهند.
فقط متن پیام را بنویسید (بدون سلام و احوالپرسی‌های کش‌دار و کلیشه‌ای).
"""
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip() if response and response.text else f"سلام {username} عزیز! پیام قشنگت رسید ✨ جزئیات رو برات فرستادم، حتما چکش کن!"
        except Exception as e:
            print(f"[AI DM Error] {e}")
            return "درود! ممنون از پیامت رفیق، نکسوس همیشه کنارتونه 🚀"

    def generate_comment_reply(self, comment_text: str, author: str, keyword: str = "") -> str:
        """تولید پاسخ عمومی داینامیک، خلاقانه و طنزآمیز زیر هر کامنت بر اساس متن دقیق آن"""
        if not self.enabled or not self.client:
            return f"سلام @{author} عزیز! جزئیات کامل براتون دایرکت ارسال شد 🚀"

        try:
            prompt = f"""
{NEXUS_PERSONA}
کاربری به نام @{author} زیر پست اینستاگرام کامنت زیر را نوشته است:
"{comment_text}"
کلمه کلیدی مرتبط: "{keyword}"

یک پاسخ عمومی کوتاه (۱ یا حداکثر ۲ جمله)، شوخ‌طبع، انرژی‌بخش و متناسب با متن کامنت بنویسید که زیر کامنت او ریپلای شود.
در پایان به او بگویید که دایرکتش رو چک کنه چون هدیه یا اطلاعات براش ارسال شده 😉.
فقط متن پاسخ را بنویسید، بدون گیومه یا توضیحات اضافی.
"""
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip().replace('"', '') if response and response.text else f"درود بر شما! اطلاعات براتون دایرکت شد 📩"
        except Exception:
            return f"درود! اطلاعات مورد نیاز براتون دایرکت شد 📩"

    def generate_reel_script(self, topic: str, goal: str = "جذب لید و کامنت") -> dict:
        """تولید سناریوی کامل ریلز ویدیویی ۳ مرحله‌ای + پرامپت میدجورنی برای کاور"""
        default_result = {
            "hook": "کار ۱۰ ساعته رو با این ترفند تو ۳ دقیقه تموم کن!",
            "visual_direction": "تصویرسازی با لپ‌تاپ در تاریکی و نور نئون آبی، فوکوس روی مانیتور",
            "body": "اکثر مردم برای ساخت اسلاید و محتوا ساعت‌ها وقت می‌ذارن، اما با این ابزار رایگان فقط کافیه ایده رو بدی...",
            "cta": "اگه پکیج پرامپت‌های پولساز رو می‌خوای، همین الان زیر این ویدیو کامنت کن «کد» تا دایرکت برات بفرستم!",
            "midjourney_prompt": "Cinematic futuristic AI workspace with glowing blue holographic displays, photorealistic, 8k, hyper-detailed --ar 9:16"
        }
        if not self.enabled or not self.client:
            return default_result

        try:
            prompt = f"""
{NEXUS_PERSONA}
وظیفه: نگارش سناریوی یک ریلز اینستاگرام وایرال و جذاب در حوزه هوش مصنوعی.
موضوع ویدیو: "{topic}"
هدف اصلی: "{goal}"

خروجی را دقیقاً در قالب فرمت JSON معتبر زیر برگردانید (هیچ متن دیگری قبل یا بعد از JSON نباشد):
{{
  "hook": "متن جذاب قلاب ثانیه ۰ تا ۳ که توجه مخاطب را قفل کند و متن روی تصویر (Text-on-screen)",
  "visual_direction": "توصیف بصری زاویه دوربین، اکت گوینده یا ابزاری که باید روی مانیتور باز باشد",
  "body": "دیالوگ‌های اصلی گوینده بین ثانیه ۳ تا ۳۵ (سریع، ریتمیک، بدون حاشیه و کاملاً کاربردی)",
  "cta": "دعوت به اقدام پایانی ریلز که بگوید زیر ریلز کلمه «کد» را بنویسند تا پکیج پرامپت ارسال شود",
  "midjourney_prompt": "English Midjourney / Flux prompt to generate the high-CTR reel cover image (9:16 aspect ratio)"
}}
"""
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except Exception as e:
            print(f"[AI Reel Error] {e}")
            return default_result

ai_assistant = AIAssistant()
