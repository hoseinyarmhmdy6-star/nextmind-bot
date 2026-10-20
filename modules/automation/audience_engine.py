import re
import random
from config import (
    KEYWORD_TRIGGERS, KEYWORD_ALIASES, FOLLOW_CONFIRMATION_PATTERNS,
    COMMENT_REPLY_VARIATIONS, INSTA_USERNAME, TARGET_COMPETITORS, SAFETY_SETTINGS
)

def normalize_persian(text: str) -> str:
    """
    استانداردسازی و پاکسازی دقیق متن فارسی برای شکار ۱۰۰٪ کلمات کلیدی،
    اصلاح حروف عربی، حذف کشیدگی‌ها، اعراب‌زدایی و فشرده‌سازی حروف تکراری
    """
    if not text:
        return ""
    
    # ۱. تبدیل حروف عربی به فارسی
    t = text.replace("ي", "ی").replace("ك", "ک").replace("ة", "ه").replace("ؤ", "و")
    t = re.sub(r"[إأآ]", "ا", t)
    
    # ۲. حذف تنوین، اعراب و کشیدگی (تطویل)
    t = re.sub(r"[\u064B-\u065F\u0640]", "", t)
    
    # ۳. فشرده‌سازی کاراکترهای مکرر (مثلاً: «کددددد» -> «کد»، «فالووووو» -> «فالو»)
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)
    
    # ۴. حروف کوچک و حذف فاصله‌های اضافی
    return t.strip().lower()

def match_keyword_intent(text: str) -> tuple:
    """
    تشخیص قصد مخاطب و استخراج کلمه کلیدی با انعطاف‌پذیری نسبت به غلط‌های املایی،
    اصطلاحات عامیانه و مترادف‌های انگلیسی و فارسی
    """
    if not text:
        return None, None
        
    norm_text = normalize_persian(text)
    tokens = re.findall(r"[\w\u0600-\u06FF]+", norm_text)

    # اولویت ۱: جستجوی نام‌های مستعار و کلمات کلیدی
    for canon_kw, aliases in KEYWORD_ALIASES.items():
        for alias in aliases:
            norm_alias = normalize_persian(alias)
            # بررسی به عنوان کلمه مجزا یا زیررشته
            if norm_alias in norm_text or any(norm_alias == tok for tok in tokens):
                rule = KEYWORD_TRIGGERS.get(canon_kw)
                if rule:
                    return canon_kw, rule

    # اولویت ۲: جستجوی مستقیم در کلیدهای اصلی
    for kw, rule in KEYWORD_TRIGGERS.items():
        norm_kw = normalize_persian(kw)
        if norm_kw in norm_text:
            return kw, rule

    return None, None

def is_follow_confirmation(text: str) -> bool:
    """
    بررسی هوشمند پیام کاربر برای تایید فالو کردن پیج
    پشتیبانی از اصطلاحات عامیانه («فالوت کردم»، «دنبال شدید»، «done»، «انجام شد»، «+»)
    """
    if not text:
        return False
        
    norm_text = normalize_persian(text)

    # ۱. بررسی الگوهای ثابت
    for p in FOLLOW_CONFIRMATION_PATTERNS:
        if normalize_persian(p) in norm_text:
            return True

    # ۲. بررسی عبارات با Regex (مثل «فالو کردمت»، «فالو شدی داداش»، «فالوتون کردیم»)
    regex_pattern = r"(فالو|دنبال).*(کرد|شد|کن|کردم|شدی|کردیم|کردمت|شدید)"
    if re.search(regex_pattern, norm_text):
        return True

    # ۳. تاییدهای کوتاه
    if norm_text.strip() in ["done", "انجام شد", "حل شد", "اوکی شد", "اوکیه", "+", "yes"]:
        return True

    return False

GENERAL_COMMENT_REPLIES = [
    "مرسی از انرژی زیبات @{username} جان! ❤️ خوشحالیم که کنار مایی ✨",
    "عشق منی @{username} عزیز! 🌟 اگه پکیج پرامپت‌های پولساز رو می‌خوای کلمه «کد» رو بنویس تا برات دایرکت بفرستم 😉🚀",
    "خیلی مخلصی رفیق! 🔥 پرانرژی باشی همیشه 🧠⚡",
    "دمت گرم @{username} عزیز! مرسی از نگاه قشنگت ❤️ با ما همراه باش که کلی تکنیک خفن تو راهه 🚀",
    "ممنون از همراهیت @{username} گل! 💎 برای دریافت ابزارهای معرفی‌شده کافیه کلمه «کد» رو کامنت کنی 😉✨",
    "انرژیت فوق‌العادست @{username}! ⚡️ امیدوارم به دردت بخوره و بهترین استفاده رو ازش ببری 🧠",
]

def get_viral_comment_reply(username: str, comment_text: str = "", keyword: str = None) -> str:
    """
    تولید پاسخ‌های پرانرژی، متغیر و بهینه‌شده برای الگوریتم اکسپلور اینستاگرام
    """
    template = random.choice(COMMENT_REPLY_VARIATIONS)
    reply = template.format(username=f"@{username}" if username else "دوست")
    return reply

def get_general_comment_reply(username: str, comment_text: str = "") -> str:
    """
    تولید پاسخ صمیمی، قدردان و خودمانی به کامنت‌های عمومی کاربران
    """
    template = random.choice(GENERAL_COMMENT_REPLIES)
    return template.format(username=f"{username}" if username else "دوست")

def generate_follow_gate_message(author: str, keyword: str) -> str:
    """
    پیام جذاب و ترغیب‌کننده برای قفل فالوور (Follow-Gate) با بیشترین نرخ تبدیل به فالو
    """
    return (
        f"سلام {author} عزیز! 🌟\n\n"
        f"پکیج اختصاصی و کاربردی «{keyword}» برات آماده شد! 🎁\n\n"
        f"برای دریافت فوری این پکیج ارزشمند، لطفاً ابتدا پیج ما (@{INSTA_USERNAME}) رو فالو کن:\n\n"
        f"۱. دکمه Follow رو بالای پیج (@{INSTA_USERNAME}) بزن.\n"
        f"۲. بعد همین‌جا بفرست: «فالو کردم» تا بلافاصله پکیج متنی کامل برات ارسال بشه! ❤️🚀"
    )

def generate_reward_unlocked_message(author: str, reply_text: str, keyword: str = "") -> str:
    """
    پیام تحویل هدیه بعد از تایید فالو با کال‌تواکشن هوشمند برای ادامه گفتگو و ایجاد وفاداری
    """
    kw_title = f" «{keyword}»" if keyword else ""
    return (
        f"خیلی خوش اومدی {author} عزیز! همراهیت با NextMind باعث افتخاره ❤️\n"
        f"پکیج اختصاصی{kw_title} تقدیم شما:\n\n"
        f"{reply_text}\n\n"
        f"📌 راستی رفیق، هر سوالی درباره اجرای این تکنیک‌ها یا پرامپت‌ها داشتی، همین‌جا مستقیم از من بپرس تا کمکت کنم! 😉⚡"
    )
