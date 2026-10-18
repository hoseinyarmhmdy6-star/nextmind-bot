import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Instagram Automation Configuration
INSTA_USERNAME = os.getenv("INSTA_USERNAME", "nextmind.hq")
INSTA_PASSWORD = os.getenv("INSTA_PASSWORD", "")
INSTA_SESSIONID = os.getenv("INSTA_SESSIONID", "")
INSTA_SESSION_FILE = str(BASE_DIR / os.getenv("INSTA_SESSION_FILE", "insta_session.json"))
INSTA_PROXY = os.getenv("INSTA_PROXY", None)

# Meta Official Graph API Configuration
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "nextmind_secure_token_12345")
META_PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN", "")
META_INSTAGRAM_ACCOUNT_ID = os.getenv("META_INSTAGRAM_ACCOUNT_ID", "")
META_GRAPH_API_URL = "https://graph.facebook.com/v19.0"

# AI Configuration (Gemini)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Webhook Server
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8000))

# Database
DB_PATH = str(BASE_DIR / "bot_database.db")

# -------------------------------------------------------------
# Trigger Rules & Auto-Replies (Customizable for nextmind.hq)
# -------------------------------------------------------------
COMMENT_REPLY_VARIATIONS = [
    "سلام! جزئیات کامل براتون دایرکت ارسال شد 🚀",
    "درود! اطلاعات مورد نیاز براتون دایرکت شد 📩",
    "سلام، براتون دایرکت فرستادم، لطفاً چک بفرمایید ✨",
    "برات دایرکت فرستادم رفیق! پیام‌هات رو چک کن 😉",
]

# Keyword Triggers: If comment contains keyword -> Send corresponding DM
KEYWORD_TRIGGERS = {
    "لینک": {
        "reply_text": "سلام و درود از طرف تیم NextMind! 🌟\nلینکی که خواسته بودید:\nhttps://nextmind.ir/resources\n\nهر سوالی داشتی همین‌جا بپرس در خدمتیم!",
        "require_follow": True,
    },
    "کتاب": {
        "reply_text": "درود! 📚 کتابچه راهنمای اختصاصی NextMind براتون آماده شده:\nدانلود: https://nextmind.ir/ebook\n\nموفق باشید!",
        "require_follow": True,
    },
    "هوش مصنوعی": {
        "reply_text": "سلام رفیق! به دنیای هوش مصنوعی NextMind خوش اومدی 🤖\nدوره رایگان و منابع هوش مصنوعی رو از اینجا ببین:\nhttps://nextmind.ir/ai-tools\n\nاگه راهنمایی بیشتری خواستی بگو تا کمکت کنم!",
        "require_follow": True,
    },
    "تخفیف": {
        "reply_text": "تبریک! کد تخفیف ویژه شما: 🎉 NEXTMIND20\n(۲۰٪ تخفیف روی تمام خدمات)\nاستفاده در: https://nextmind.ir",
        "require_follow": False,
    },
    "کد": {
        "reply_text": "درود دوست عزیز! 🎁 پکیج اختصاصی پرامپت‌های پولساز هوش مصنوعی NextMind براتون آماده شد:\nمشاهده و دانلود: https://nextmind.ir/prompts\n\nهر سوالی داشتی همین‌جا بپرس!",
        "require_follow": True,
    },
    "پرامپت": {
        "reply_text": "سلام رفیق! 🔥 پرامپت‌های تخصصی هوش مصنوعی خدمت شما:\nhttps://nextmind.ir/prompts\n\nموفق و پیروز باشید!",
        "require_follow": True,
    },
}

FOLLOW_GATE_MESSAGE = (
    "سلام دوست عزیز! 👋\n"
    "برای دریافت این هدیه/لینک اختصاصی، لطفاً ابتدا پیج ما (@nextmind.hq) را فالو کنید.\n"
    "به محض فالو کردن، روی دکمه زیر کلیک کنید یا یک پیام بدید تا بلافاصله براتون ارسال بشه! ❤️"
)

# -------------------------------------------------------------
# Safety & Rate Limits for Competitor Growth (Safe Automation)
# -------------------------------------------------------------
SAFETY_SETTINGS = {
    "max_follows_per_day": 40,
    "max_likes_per_day": 60,
    "min_delay_between_actions": 35,  # seconds
    "max_delay_between_actions": 95,  # seconds
    "unfollow_after_days": 3,
}
