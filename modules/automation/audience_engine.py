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

def match_keyword_intent(text: str, media_id: str = None) -> tuple:
    """
    تشخیص قصد مخاطب و استخراج کلمه کلیدی با پشتیبانی از کلمات طلایی دینامیک ریلزها و استوری‌ها،
    انعطاف‌پذیری نسبت به غلط‌های املایی، اصطلاحات عامیانه و مترادف‌های انگلیسی و فارسی
    """
    if not text:
        return None, None
        
    norm_text = normalize_persian(text)
    tokens = re.findall(r"[\w\u0600-\u06FF]+", norm_text)

    # اولویت ۰: بررسی کلمه طلایی اختصاصی این پست/ریلز خاص (در صورت وجود media_id)
    try:
        from database import get_dynamic_trigger_by_media, get_all_dynamic_triggers
        if media_id:
            dyn = get_dynamic_trigger_by_media(media_id)
            if dyn and dyn.get("keyword"):
                dkw = normalize_persian(dyn["keyword"])
                aliases = [normalize_persian(a) for a in dyn.get("aliases", "").split(",") if a]
                if dkw in norm_text or any(dkw == tok for tok in tokens) or any(a in norm_text for a in aliases):
                    rule = {
                        "reply_text": dyn.get("package_text") or KEYWORD_TRIGGERS.get("کد", {}).get("reply_text"),
                        "require_follow": True
                    }
                    return dyn["keyword"], rule

        # اولویت ۰.۵: بررسی تمامی کلمات طلایی استخراج‌شده از سایر ریلزها و استوری‌ها
        all_dyn = get_all_dynamic_triggers()
        for dyn in all_dyn:
            dkw = normalize_persian(dyn.get("keyword", ""))
            if not dkw:
                continue
            aliases = [normalize_persian(a) for a in dyn.get("aliases", "").split(",") if a]
            if dkw in norm_text or any(dkw == tok for tok in tokens) or any(a in norm_text for a in aliases):
                rule = {
                    "reply_text": dyn.get("package_text") or KEYWORD_TRIGGERS.get("کد", {}).get("reply_text"),
                    "require_follow": True
                }
                return dyn["keyword"], rule
    except Exception:
        pass

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
    "سلام و درود خدمت شما {username} گرامی، بسیار سپاسگزاریم از توجه و انرژی مثبت شما 🙏✨",
    "درود و احترام {username} عزیز! خوشحالیم که این محتوا مورد توجهتون قرار گرفته 🌟 در صورت تمایل به دریافت پکیج پرامپت‌ها، کافیه کلمه «کد» رو ارسال فرمایید.",
    "ارادتمندیم {username} گرامی، همراهی ارزشمند شما با مجموعه NextMind مایه افتخار است 🧠✨",
    "سلام و احترام {username} بزرگوار، از مهر و لطف شما بی‌نهایت سپاسگزاریم 🙏 همیشه پیروز و سربلند باشید.",
    "درود بر شما! سپاس از نگاه زیباتون 💡 چنانچه تمایل به دسترسی به ابزارهای معرفی‌شده دارید، کلمه «کد» رو ارسال فرمایید تا تقدیم حضورتون بشه.",
    "بسیار متشکریم از انگیزه و انرژی فوق‌العادتون {username} عزیز! امیدواریم این نکات به بهترین شکل براتون کاربردی واقع بشه 🌟",
]

def get_viral_comment_reply(username: str, comment_text: str = "", keyword: str = None) -> str:
    """
    تولید پاسخ‌های محترمانه، صمیمانه و متین برای بخش کامنت‌ها
    """
    template = random.choice(COMMENT_REPLY_VARIATIONS)
    reply = template.format(username=f"@{username}" if username else "دوست")
    return reply

def get_general_comment_reply(username: str, comment_text: str = "") -> str:
    """
    تولید پاسخ صمیمانه ولی رسمی و باوقار به کامنت‌های عمومی کاربران
    """
    template = random.choice(GENERAL_COMMENT_REPLIES)
    return template.format(username=f"{username}" if username else "گرامی")

def generate_follow_gate_message(author: str, keyword: str) -> str:
    """
    پیام جذاب و محترمانه برای قفل فالوور (Follow-Gate) با حفظ پرستیژ کامل برند
    """
    return (
        f"سلام و درود خدمت شما {author} عزیز و گرامی! 🌟\n\n"
        f"پکیج اختصاصی و کاربردی «{keyword}» برای شما آماده گردیده است. 🎁\n\n"
        f"جهت دریافت فوری این محتوای ارزشمند، لطفاً ابتدا پیج رسمی ما (@{INSTA_USERNAME}) را دنبال فرمایید:\n\n"
        f"۱. دکمه Follow را در بالای پیج (@{INSTA_USERNAME}) لمس نمایید.\n"
        f"۲. سپس در همین دایرکت عبارت «فالو کردم» را ارسال فرمایید تا پکیج بلافاصله تقدیم حضورتان شود. سپاس از همراهی شما 🙏✨"
    )

def generate_reward_unlocked_message(author: str, reply_text: str, keyword: str = "") -> str:
    """
    پیام تحویل هدیه بعد از تایید فالو با لحن صمیمانه ولی رسمی و محترمانه
    """
    kw_title = f" «{keyword}»" if keyword else ""
    return (
        f"بسیار خوش آمدید {author} گرامی، همراهی شما با مجموعه NextMind مایه افتخار است 🌟\n"
        f"پکیج اختصاصی{kw_title} با احترام تقدیم حضورتان می‌گردد:\n\n"
        f"{reply_text}\n\n"
        f"📌 در صورت وجود هرگونه پرسش درباره نحوه اجرای این پرامپت‌ها و ابزارها، با کمال میل در همین بخش پاسخگوی شما بزرگوار هستیم. 🙏✨"
    )
