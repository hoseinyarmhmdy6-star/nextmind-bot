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
    "سلام {username} عزیز! 🚀 برات دایرکت فرستادم، چک کن تا داغه!",
    "درود بر شما! 📩 اطلاعات اختصاصی همین الان به دایرکتت پرواز کرد ✨",
    "سلام رفیق! 😉 پیام‌هات رو چک کن، برات کامل فرستادم 🚀",
    "درود! 🎁 هدیه این پست رو مستقیم توی دایرکت برات ارسال کردم 🧠",
    "سلام {username} جان! 🌟 لینک دسترسی با عشق برات دایرکت شد، موفق باشی!",
    "چک کن رفیق! 📩 یک پیام خفن توی دایرکت منتظرته 😉⚡",
    "سلام! ⚡️ کامل‌ترین راهنما به همراه دسترسی برات دایرکت شد، ببینش!",
    "درود {username} عزیز! 💎 برات ارسال شد، اگر ندیدی پوشه ریکوئست‌ها رو چک کن!",
    "سلام رفیق پرانرژی! 🚀 برات دایرکت فرستادم، از کار باهاش لذت ببر!",
    "درود! 💌 تقدیمت شد دوست من، سریع چکش کن و نظرت رو بگو!",
]

# Keyword Triggers: If comment/DM matches keyword -> Send corresponding DM
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
    "استارت": {
        "reply_text": "درود رفیق! 🎁 تقلب‌نامه ۱۵ ابزار مخفی و پولساز هوش مصنوعی خدمت شما:\nhttps://nextmind.ir/cheatsheet\n\nهر سوالی درباره روش کار با این ابزارها داشتی همین‌جا بپرس تا راهنماییت کنم! 🚀",
        "require_follow": True,
    },
    "جزوه": {
        "reply_text": "سلام رفیق! 🚀 لینک و آموزش استفاده از ابزار خلاصه‌ساز ویدیوی یوتیوب و پادکست (NoteGPT):\nhttps://notegpt.io\n\nویدیوی ۲ ساعته رو تو ۳۰ ثانیه جزوه و نقشه ذهنی کن! هر سوالی داشتی من اینجام 🧠",
        "require_follow": True,
    },
    "اسلاید": {
        "reply_text": "سلام دوست عزیز! 🎨 قالب‌ها و لینک دسترسی به ارائه‌ساز سریع Gamma AI:\nhttps://gamma.app\n\nدیگه برای اسلاید و پرزنتیشن وقت تلف نکن! موفق باشی ✨",
        "require_follow": True,
    },
}

# نقشه‌برداری هوشمند کلمات کلیدی، مترادف‌ها و اشتباهات تایپی برای شکار ۱۰۰٪ لیدها
KEYWORD_ALIASES = {
    "کد": [
        "کد", "کدد", "کددد", "کدها", "کدهارو", "کدو", "کد رو", "پرامپت", "پرامپتها", "پرامپت‌ها",
        "پکیج", "code", "prompt", "prompts", "cod", "prampt", "promt"
    ],
    "جزوه": [
        "جزوه", "جزوهه", "جزوهرو", "جزوه رو", "خلاصه", "خلاصه‌ساز", "یوتیوب", "نوت", "notegpt",
        "note", "jozve", "jozveh", "jazveh", "خلاصه ساز"
    ],
    "استارت": [
        "استارت", "استارتت", "شروع", "تقلب", "تقلب‌نامه", "تقلبنامه", "چیت‌شیت", "چیت شیت",
        "start", "cheatsheet", "cheat", "ابزارها", "15"
    ],
    "اسلاید": [
        "اسلاید", "اسلایدها", "ارائه", "پرزنتیشن", "گاما", "اسلایدشو", "slide", "slides",
        "gamma", "presentation", "powerpoint"
    ],
    "لینک": [
        "لینک", "لینکو", "لینک رو", "سایت", "منبع", "link", "links", "site", "url"
    ],
    "کتاب": [
        "کتاب", "کتابچه", "ایبوک", "پی دی اف", "book", "ebook", "pdf"
    ],
    "هوش مصنوعی": [
        "هوش مصنوعی", "هوشمصنوعی", "هوش", "ai", "artificial intelligence"
    ],
    "تخفیف": [
        "تخفیف", "تخفیفو", "کد تخفیف", "off", "discount", "offer"
    ],
}

# الگوهای هوشمند تایید فالو در پیام مخاطب
FOLLOW_CONFIRMATION_PATTERNS = [
    "فالو کردم", "فالوت کردم", "فالو شدید", "فالو شد", "فالوتونم کردم", "فالوت کردم داداش",
    "دنبال کردم", "دنبال شدید", "دنبالت کردم", "done", "انجام شد", "اوکی شد", "فالو کردی",
    "فالو کردم بفرست", "فالو کردم مرسی", "فالو کردم بفرستین", "فالو کردم لینک بده",
    "فالو کردمت", "فالوو کردم", "فالووو", "فالوتم", "من فالو کردم", "+", "فالو"
]

FOLLOW_GATE_MESSAGE = (
    "سلام دوست عزیز! 👋\n"
    "برای دریافت این هدیه/لینک اختصاصی، لطفاً ابتدا پیج ما (@nextmind.hq) را فالو کنید.\n"
    "به محض فالو کردن، همین‌جا بفرستید «فالو کردم» تا بلافاصله قفل براتون باز بشه! ❤️"
)

# -------------------------------------------------------------
# پیج‌های هدف برای جذب مخاطب فعال هوش مصنوعی (Competitor Growth)
# -------------------------------------------------------------
TARGET_COMPETITORS = [
    "amir.technology",
    "shikhesabi",
    "ai_irani",
    "python.hub"
]

SAFETY_SETTINGS = {
    "max_follows_per_day": 30,
    "max_likes_per_day": 50,
    "min_delay_between_actions": 45,  # seconds
    "max_delay_between_actions": 110,  # seconds
    "unfollow_after_days": 3,
}
