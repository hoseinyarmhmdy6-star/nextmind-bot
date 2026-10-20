import os
import ssl
import json
import urllib.request
import urllib.parse
from config import GEMINI_API_KEY

# Telegram Credentials Loader (Optional alert channel)
def get_telegram_creds():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
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
- خط قرمز ما: هیچ‌وقت وقت مخاطب را با اخبار زرد، تئوری‌های خسته‌کننده کتابی یا مقدمه‌های کلیشه‌ای تلف نمی‌کنیم!

💎 دستورالعمل لحن گفتار (قانون صمیمانه ولی رسمی):
- تعادل دقیق بین «صمیمیت گرم» و «ادب و پرستیژ رسمی»: شما نماینده یک برند لوکس و پیشروی فناوری هستید. لحن شما باید همواره محترمانه، باوقار، شیک و در عین حال گرم و پرانرژی باشد.
- خط قرمز کلمات: هرگز از عبارات بیش از حد عامیانه، لاتی یا کوچه‌بازاری استفاده نکنید! (ممنوع: «دمت گرم»، «عشق منی»، «پایه‌ای»، «واست»، «بزن تو کارش»، «داش»، «رفیق جون»).
- عبارات استاندارد نکسوس:
  * «سلام و درود بر شما {author} عزیز و گرامی»
  * «بسیار متشکریم از همراهی و انرژی مثبت ارزشمندتون»
  * «خوشحالیم که این آموزش مورد توجهتون قرار گرفته»
  * «پکیج با احترام تقدیم حضورتون شد / براتون دایرکت ارسال گردید»
  * «در صورت تمایل به دریافت پکیج، خوشحال می‌شویم کلمه «کد» را ارسال فرمایید»
- ایموجی‌های مجاز و متین: حداکثر ۱ یا ۲ ایموجی باوقار مثل 🌟، ✨، 🧠، 💡، 🙏.

🚨 قانون قطعی و خط قرمز حیاتی:
- پیج @nextmind.hq در حال حاضر هیچ‌گونه وب‌سایتی ندارد!
- تمامی مشاوره‌ها، پکیج‌ها، پرامپت‌ها و آموزش‌ها مستقیماً در همین دایرکت اینستاگرام به صورت متن‌های کامل و آماده ارائه می‌شوند.
- به هیچ وجه از خود آدرس سایت (مثل nextmind.ir یا هر دامین دیگر) اختراع نکنید و هرگز کاربر را به وب‌سایت ارجاع ندهید.
- اگر کاربر اطلاعات بیشتر، پکیج یا هدیه خواست، او را راهنمایی کنید که کلمه «کد» را ارسال کند تا پکیج متنی پرامپت‌های پولساز تقدیم حضورش شود.
"""

class AIAssistant:
    def __init__(self):
        self.enabled = bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here")
        self.client = None
        self.models_cascade = [
            "models/gemini-2.5-flash",
            "models/gemini-flash-latest",
            "models/gemini-flash-lite-latest",
            "models/gemini-2.5-pro"
        ]
        if self.enabled:
            try:
                from google import genai
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                print(f"[AI Assistant Init Warning] {e}")

    def _smart_fallback_reply(self, user_message: str, username: str = "رفیق") -> str:
        """پاسخ هوشمند اقتضایی در صورت در دسترس نبودن موقت سرور هوش مصنوعی"""
        msg = (user_message or "").strip().lower()

        # احوالپرسی
        if any(w in msg for w in ["چطوری", "خوبی", "حالت", "چه خبر", "احوال"]):
            return (
                f"به لطف انرژی شما عالی، {username} عزیز! 🧠⚡\n"
                f"نکسوس اینجاست و همه‌چیز آماده‌ست تا کارهای ۱۰ ساعته رو با هوش مصنوعی تو ۱۰ دقیقه جمع کنیم! 😉\n"
                f"اگر پکیج ابزارها و پرامپت‌های پولساز رو می‌خوای، فقط کلمه «کد» رو برام بفرست 🚀"
            )

        # سلام و درود
        if any(w in msg for w in ["سلام", "درود", "صبح بخیر", "عصر بخیر", "شب بخیر", "hi", "hello"]):
            return (
                f"سلاااام {username} عزیز! روزت پر از انرژی و اتفاق‌های خفن 🌟\n"
                f"نکسوس اینجاست؛ بگو ببینم چطور می‌تونم کمکت کنم تا با هوش مصنوعی چند قدم جلوتر از بقیه باشی؟ 😉🚀\n"
                f"برای دریافت آنی پکیج پرامپت‌های پولساز، کلمه «کد» رو همین‌جا بفرست!"
            )

        # سوال در مورد گوشی / سیستم
        if any(w in msg for w in ["گوشی", "موبایل", "لپتاپ", "سیستم", "کامپیوتر", "اندروید", "آیفون"]):
            return (
                f"خیالت ۱۰۰٪ راحت باشه {username} عزیز! 📱✨\n"
                f"تمام ابزارها و تکنیک‌هایی که آموزش می‌دیم نسخه وب یا اپلیکیشن دارن و با یه گوشی معمولی هم دقیقاً همون خروجی دلاری و فوق‌العاده رو می‌دن.\n"
                f"برای اینکه همین الان شروع کنی، کلمه «کد» رو بفرست تا منابع رو برات باز کنم 🚀"
            )

        # سوال در مورد رایگان بودن یا قیمت
        if any(w in msg for w in ["رایگان", "هزینه", "پولی", "قیمت", "چنده"]):
            return (
                f"آره رفیق! اصل کار نکسوس معرفی ابزارهای کاملاً رایگان یا با سهمیه روزانه رایگانه 🎁\n"
                f"هدف اینه بدون نیاز به ویزاکارت یا هزینه اضافی، سریع‌ترین نتیجه رو بگیری.\n"
                f"همین الان کلمه «کد» رو برام بفرست تا پکیج پرامپت‌های رایگان رو تقدیمت کنم ✨"
            )

        # درخواست پشتیبان یا خرید
        if any(w in msg for w in ["خرید", "دوره", "ادمین", "پشتیبان", "مشاوره", "همکاری", "تلفن"]):
            return (
                f"سلام {username} عزیز! پیامت دریافت و برای ادمین هم علامت‌گذاری شد 📩\n"
                f"همکاران من در سریع‌ترین زمان برای راهنمایی اختصاصی کنارت هستن. ضمناً برای دریافت پکیج اولیه می‌تونی کلمه «کد» رو بفرستی 🌟"
            )

        # پیش‌فرض جذاب و انگیزشی
        return (
            f"سلام {username} عزیز و پرانرژی! 🧠⚡\n"
            f"پیامت رسید؛ نکسوس دقیقاً اینجاست تا مسیر درآمدزایی و مهارت‌های پولساز هوش مصنوعی رو برات ساده کنه.\n"
            f"برای دریافت فوری پکیج ۳۰ ابزار و پرامپت طلایی، کلمه «کد» رو بفرست تا بلافاصله برات ارسال کنم 😉🚀"
        )

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
            return self._smart_fallback_reply(user_message, username)

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
تمام ابهامات مخاطب را برطرف کنید و او را با اشتیاق به سمت اقدام (ارسال کلمه «کد» برای دریافت پکیج متنی پرامپت‌ها) راهنمایی کنید.
اگر حس کردی سوالش خیلی تخصصی یا قصد خرید جدی دارد، به او بگو پیامش را برای ادمین هم علامت‌گذاری کردی تا شخصاً پاسخ دهند.
مستقیماً به محتوای پیام کاربر پاسخ بده و لحن خودمانی، خودمانی و شاداب داشته باش.
فقط متن پیام را بنویسید.
"""
        # زنجیره چند مدلی (Multi-Model Cascading)
        for model in self.models_cascade:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                if response and response.text and response.text.strip():
                    return response.text.strip()
            except Exception as e:
                print(f"[AI DM Cascade Warning ({model})] {e}")
                continue

        # در صورت بروز خطای مقطعی در تمام مدل‌ها، پاسخ هوشمند مبتنی بر نیت ارسال می‌شود
        return self._smart_fallback_reply(user_message, username)

    def generate_comment_reply(self, comment_text: str, author: str, keyword: str = "") -> str:
        """تولید پاسخ عمومی داینامیک، باوقار، صمیمانه ولی رسمی و جذاب زیر هر کامنت بر اساس متن دقیق آن"""
        if not self.enabled or not self.client:
            if keyword:
                return f"سلام و احترام @{author} عزیز و گرامی! 🌟 پکیج اختصاصی با احترام تقدیم دایرکت شما شد 📩"
            else:
                return f"درود و سپاس فراوان @{author} گرامی، ممنون از مهر و انرژی مثبت شما 🙏✨ در صورت تمایل به دریافت پکیج پرامپت‌ها کافیه کلمه «کد» رو ارسال فرمایید."

        if keyword:
            context_instruction = f"""
کاربر کلمه کلیدی «{keyword}» را کامنت کرده تا پکیج اختصاصی را دریافت کند.
یک پاسخ بسیار محترمانه، صمیمانه ولی رسمی، باوقار و کوتاه (۱ یا نهایتاً ۲ جمله) بنویسید که زیر کامنت او ریپلای شود و با لحنی متین و شیک اعلام کند پکیج کامل هم‌اکنون در دایرکت تقدیم حضورشان شده است.
"""
        else:
            context_instruction = f"""
کاربر یک نظر عمومی (تعریف، تشکر، نظر، سوال یا ایموجی) زیر پست ما نوشته است:
یک پاسخ بسیار مودبانه، باوقار، گرم و صمیمانه-رسمی بنویسید که با احترام از توجه و انرژی مثبت ایشان سپاسگزاری کند و در صورت تمایل با متانت بگوید چنانچه تمایل به دریافت پکیج پرامپت‌ها و ابزارهای معرفی‌شده دارند، کافیست کلمه «کد» را ارسال فرمایند.
"""

        prompt = f"""
{NEXUS_PERSONA}
کاربری به نام @{author} زیر پست اینستاگرام کامنت زیر را نوشته است:
"{comment_text}"

دستورالعمل تولید پاسخ:
{context_instruction}

قوانین مهم و خط قرمز:
۱. فقط و فقط متن پیام پاسخ ریپلای را بنویسید؛ بدون هیچ عنوان، توضیح، مقدمه یا گیومه اضافی.
۲. لحن حتماً «صمیمانه ولی رسمی، باوقار و محترمانه» باشد.
۳. به هیچ وجه از کلمات عامیانه، لاتی یا جلف (مانند دمت گرم، عشق منی، پایه‌ای، واست، بزن تو کارش) استفاده نکنید.
۴. استفاده از حداکثر ۱ یا ۲ ایموجی متین (مانند 🌟، ✨، 🙏، 🧠).
"""
        for model in self.models_cascade:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                if response and response.text and response.text.strip():
                    return response.text.strip().replace('"', '')
            except Exception:
                continue
        if keyword:
            return f"سلام و درود @{author} عزیز! پکیج اختصاصی با احترام تقدیم دایرکت شما گردید 📩✨"
        return f"سلام و درود @{author} گرامی! بسیار سپاسگزاریم از توجه و همراهی ارزشمند شما 🙏🌟"

    def generate_reel_script(self, topic: str, goal: str = "جذب لید و کامنت") -> dict:
        """تولید سناریوی کامل ریلز ویدیویی ۳ مرحله‌ای + پرامپت میدجورنی برای کاور"""
        default_result = {
            "hook": "کار ۱۰ ساعته رو با این ترفند تو ۳ دقیقه تموم کن!",
            "visual_direction": "تصویرسازی با لپ‌تاپ در تاریکی و نور نئون آبی، فوکوس روی مانیتور",
            "body": "اکثر مردم برای ساخت اسلاید و محتوا ساعت‌ها وقت می‌ذارن، اما با این ابزار رایگان فقط کافیه ایده رو بدی...",
            "cta": "اگه پکیج پرامپت‌های پولساز رو می‌خوای، همین الان زیر این ویدیو کامنت کن «کد» تا دایرکت برات بفرستم!",
            "midjourney_prompt": "Cinematic futuristic AI workspace with glowing blue holographic displays, photorealistic, 8k, hyper-detailed --ar 9:16"
        }
        prompt = f"""
{NEXUS_PERSONA}
موضوع ریلز: "{topic}"
هدف: "{goal}"

یک سناریوی ۳۰ الی ۵۰ ثانیه‌ای ریلز اینستاگرام در قالب ساختار JSON زیر تولید کنید:
{{
    "hook": "جمله ۳ ثانیه اول فوق‌العاده کنجکاوکننده و متوقف‌کننده اسکرول",
    "visual_direction": "توضیح حرکات تصویر، چهره و المان‌های بصری",
    "body": "متن اصلی سناریو، ساده، کاربردی و هیجان‌انگیز",
    "cta": "دعوت به اقدام هوشمندانه برای کامنت کردن کلمه کلیدی",
    "midjourney_prompt": "پرامپت انگلیسی میدجورنی برای کاور جذاب ریلز"
}}
فقط JSON معتبر خروجی دهید.
"""
        for model in self.models_cascade:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                text = response.text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                return json.loads(text.strip())
            except Exception as e:
                continue
        return default_result

ai_assistant = AIAssistant()
