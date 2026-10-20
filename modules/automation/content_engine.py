import os
import sys
import time
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

from modules.automation.insta_client import insta_manager
from modules.ai_assistant.gemini_bot import ai_assistant

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORIES_DIR = BASE_DIR / "generated_stories"
STORIES_DIR.mkdir(exist_ok=True)
REELS_DIR = BASE_DIR / "reels_queue"
REELS_DIR.mkdir(exist_ok=True)
REELS_PUBLISHED_DIR = REELS_DIR / "published"
REELS_PUBLISHED_DIR.mkdir(exist_ok=True)

FONT_PATH = "C:\\Windows\\Fonts\\tahoma.ttf"

import re

def clean_persian_text(text: str) -> str:
    """حذف کاراکترهای ایموجی برای جلوگیری از نمایش مربع در فونت‌های ویندوز"""
    if not text:
        return ""
    # حذف ایموجی‌ها
    clean = re.sub(r'[\U00010000-\U0010ffff]|[\u2600-\u27ff]', '', text)
    return clean.strip()

def reshape_text(text: str) -> str:
    """اصلاح و اتصال صحیح حروف فارسی برای رندر روی عکس"""
    if not text:
        return ""
    cleaned = clean_persian_text(text)
    reshaped = arabic_reshaper.reshape(cleaned)
    return get_display(reshaped)

def create_story_card(
    category: str,
    headline: str,
    bullets: list,
    cta_text: str = "زیر آخرین ریلز بنویس «کد» تا لینک برات ارسال بشه 🚀",
    filename: str = "story_latest.jpg"
) -> str:
    """
    تولید استوری استاندار با ابعاد 1080x1920 با گرافیک مدرن هوش مصنوعی و تایپوگرافی فارسی
    """
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), color="#070913")
    draw = ImageDraw.Draw(img)

    # پس‌زمینه گرادیانت مدرن (Dark Indigo & Cyan Cyberpunk)
    for y in range(height):
        ratio = y / height
        r = int(7 + ratio * 18)
        g = int(9 + ratio * 20)
        b = int(19 + ratio * 60)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # دایره‌های نئونی تزئینی در بک‌گراند
    draw.ellipse([700, -100, 1200, 400], fill=(28, 42, 100, 80))
    draw.ellipse([-150, 1300, 450, 1900], fill=(16, 68, 120, 80))

    try:
        font_brand = ImageFont.truetype(FONT_PATH, 34)
        font_badge = ImageFont.truetype(FONT_PATH, 28)
        font_headline = ImageFont.truetype(FONT_PATH, 54)
        font_bullet_title = ImageFont.truetype(FONT_PATH, 36)
        font_bullet_desc = ImageFont.truetype(FONT_PATH, 28)
        font_cta = ImageFont.truetype(FONT_PATH, 34)
    except Exception:
        font_brand = font_badge = font_headline = font_bullet_title = font_bullet_desc = font_cta = ImageFont.load_default()

    # 1. هدر برندینگ بالای استوری
    draw.rectangle([90, 140, 990, 230], fill="#0f172a", outline="#334155", width=2)
    brand_text = reshape_text("NextMind HQ | @nextmind.hq")
    draw.text((540, 185), brand_text, fill="#38bdf8", font=font_brand, anchor="mm")

    # 2. بج دسته‌بندی
    cat_text = reshape_text(f"🔥 {category}")
    draw.rounded_rectangle([390, 290, 690, 350], radius=30, fill="#1e293b", outline="#0284c7", width=2)
    draw.text((540, 320), cat_text, fill="#e0f2fe", font=font_badge, anchor="mm")

    # 3. عنوان اصلی و قلاب (Headline)
    hl_text = reshape_text(headline)
    draw.text((540, 450), hl_text, fill="#ffffff", font=font_headline, anchor="mm")

    # 4. باکس‌های محتوایی (Bullets)
    box_y = 570
    colors = ["#0284c7", "#6366f1", "#8b5cf6"]
    for i, b in enumerate(bullets[:3]):
        b_title = b.get("title", "")
        b_desc = b.get("desc", "")
        
        # کارت شیشه‌ای
        draw.rounded_rectangle([90, box_y, 990, box_y + 240], radius=24, fill="#0f172a", outline=colors[i % len(colors)], width=2)
        
        # شماره مرحله
        num_str = reshape_text(f"تکنیک ۰{i+1}")
        draw.rounded_rectangle([840, box_y + 25, 960, box_y + 70], radius=15, fill=colors[i % len(colors)])
        draw.text((900, box_y + 47), num_str, fill="#ffffff", font=font_badge, anchor="mm")

        # تیتر
        t_text = reshape_text(b_title)
        draw.text((820, box_y + 47), t_text, fill="#ffffff", font=font_bullet_title, anchor="rm")

        # توضیحات
        d_text = reshape_text(b_desc)
        draw.text((940, box_y + 130), d_text, fill="#94a3b8", font=font_bullet_desc, anchor="rm")

        box_y += 280

    # 5. کال تواکشن و دکمه تبلیغاتی پایین استوری (CTA)
    cta_box_top = 1520
    draw.rounded_rectangle([90, cta_box_top, 990, cta_box_top + 160], radius=28, fill="#0284c7")
    cta_display = reshape_text(cta_text)
    draw.text((540, cta_box_top + 80), cta_display, fill="#ffffff", font=font_cta, anchor="mm")

    # فوتر
    footer = reshape_text("کار ۱۰ ساعته رو با هوش مصنوعی تو ۱۰ دقیقه جمع کن 🧠")
    draw.text((540, 1740), footer, fill="#64748b", font=font_badge, anchor="mm")

    out_path = str(STORIES_DIR / filename)
    img.save(out_path, quality=95)
    return out_path

class AutonomousContentEngine:
    def __init__(self):
        self.client = insta_manager.client

    def generate_viral_story_content(self, topic: str = "تکنیک‌های پرامپت‌نویسی پولساز"):
        """تولید متون و سناریوی استوری با هوش مصنوعی"""
        prompt = f"""شما نکسوس، استراتژیست ارشد پیج NextMind (@nextmind.hq) هستید. 
برای موضوع "{topic}"، محتوای یک استوری فوق‌العاده کاربردی با فرمت دقیق JSON زیر بنویسید:
{{
  "category": "ترفند روز هوش مصنوعی",
  "headline": "کار ۱۰ ساعته رو تو ۱۰ دقیقه جمع کن!",
  "bullets": [
    {{"title": "تکنیک منتقد سخت‌گیر", "desc": "به AI بگو: قبل از پاسخ، مثل یک داور بی‌رحم ایرادها رو بگو."}},
    {{"title": "قانون خط قرمز منفی", "desc": "بهش بگو کلمات کلیشه‌ای و مقدمه‌چینی ممنوعه؛ مستقیم برو سر اصل مطلب."}},
    {{"title": "خروجی ماتریسی", "desc": "بخواه که نتیجه رو در قالب جدول مقایسه‌ای بده تا بلافاصله قابل استفاده باشه."}}
  ],
  "cta": "زیر آخرین ریلز بنویس «کد» تا پکیج پرامپت‌ها برات ارسال بشه 🚀"
}}
فقط JSON خالص بازگردانید."""
        try:
            raw = ai_assistant.generate_reply(prompt, username="سیستم محتوا")
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            import json
            return json.loads(raw.strip())
        except Exception:
            return {
                "category": "ترفند روز هوش مصنوعی",
                "headline": "کار ۱۰ ساعته رو تو ۱۰ دقیقه جمع کن!",
                "bullets": [
                    {"title": "تکنیک منتقد سخت‌گیر", "desc": "به AI دستور بده مثل یک داور حرفه‌ای خروجی رو ارزیابی کنه."},
                    {"title": "قانون خط قرمز منفی", "desc": "ممنوعیت مقدمه‌چینی‌های کلیشه‌ای برای گرفتن پاسخ مستقیم."},
                    {"title": "خروجی ماتریسی و عملیاتی", "desc": "دریافت سریع نتیجه در جدول برای صرفه‌جویی زمان."}
                ],
                "cta": "کلمه «کد» رو دایرکت بفرست تا پکیج پرامپت‌ها برات ارسال بشه 🚀"
            }

    def publish_story_now(self, topic: str = "تکنیک‌های پرامپت‌نویسی پولساز") -> bool:
        """تولید و انتشار خودکار استوری روی پیج اینستاگرام"""
        try:
            print(f"[Content Engine] Generating story graphic for: {topic}...")
            story_data = self.generate_viral_story_content(topic)
            
            image_path = create_story_card(
                category=story_data.get("category", "آموزش هوش مصنوعی"),
                headline=story_data.get("headline", "کار ۱۰ ساعته تو ۱۰ دقیقه"),
                bullets=story_data.get("bullets", []),
                cta_text=story_data.get("cta", "کلمه «کد» رو بفرست 🚀"),
                filename=f"story_{int(time.time())}.jpg"
            )
            print(f"[Content Engine] Story image generated at: {image_path}")

            # انتشار مستقیم روی پیج با instagrapi
            if not insta_manager.is_logged_in:
                insta_manager.login()

            print("[Content Engine] Uploading story to Instagram @nextmind.hq...")
            result = self.client.photo_upload_to_story(image_path)
            print(f"[Content Engine] ✅ Story published successfully! ID: {result.pk}")
            return True
        except Exception as e:
            print(f"[Content Engine Error] Failed to publish story: {e}")
            return False

    def generate_viral_reel_package(self, topic: str = "خلاصه‌ساز ۳۰ ثانیه‌ای ویدیو NoteGPT") -> str:
        """تولید کپشن، هوک و کال‌تواکشن ریلز با هوش مصنوعی نکسوس"""
        prompt = f"""شما نکسوس، کاراکتر و راهنمای ارشد هوش مصنوعی پیج NextMind (@nextmind.hq) هستید.
برای ریلز با موضوع "{topic}"، یک متن کپشن اینستاگرام با ساختار ویرال زیر بنویسید:
1. هوک شوکه‌کننده ثانیه اول
2. اصل ماجرا و ۳ نکته کاربردی
3. کال‌تو‌اکشن واضح برای کامنت کردن کلمه کلیدی «جزوه» یا «کد»
4. هشتگ‌های پربازدید و تخصصی

فقط متن نهایی کپشن بدون مقدمه‌چینی بازگردانید."""
        try:
            caption = ai_assistant.generate_reply(prompt, username="سیستم ریلز")
            return caption.strip()
        except Exception:
            return f"""🚀 {topic}

کار ۱۰ ساعته رو با هوش مصنوعی تو ۱۰ دقیقه جمع کن! 🧠

دیگه نیازی نیست ساعت‌ها پای ویدیوهای آموزشی و پادکست‌های طولانی وقت تلف کنی؛ با این ابزار هر ویدیویی رو تو ۳۰ ثانیه تبدیل به جزوه خلاصه و نقشه ذهنی کن!

👇 کلمه «جزوه» رو کامنت کن تا لینک و آموزش اختصاصی آنی بیاد دایرکتت 🚀

#هوش_مصنوعی #آموزش_هوش_مصنوعی #تولید_محتوا #ابزار_هوش_مصنوعی #نکسوس #ai #notegpt"""

    def create_reel_cover(self, title: str, subtitle: str = "نکسوس | هوش مصنوعی 🧠") -> str:
        """تولید کاور استاندارد ریلز اینستاگرام (1080x1920) با تم دارک سایبرپانک"""
        width, height = 1080, 1920
        img = Image.new("RGB", (width, height), color="#080b18")
        draw = ImageDraw.Draw(img)

        for y in range(height):
            ratio = y / height
            r = int(8 + ratio * 15)
            g = int(11 + ratio * 18)
            b = int(24 + ratio * 70)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # المان‌های نئونی تزئینی
        draw.ellipse([650, -100, 1200, 450], fill=(28, 42, 100, 90))
        draw.ellipse([-200, 1200, 400, 1850], fill=(16, 68, 120, 90))

        try:
            font_title = ImageFont.truetype(FONT_PATH, 54)
            font_sub = ImageFont.truetype(FONT_PATH, 34)
            font_brand = ImageFont.truetype(FONT_PATH, 30)
        except Exception:
            font_title = font_sub = font_brand = ImageFont.load_default()

        # هدر برند
        draw.rectangle([100, 150, 980, 240], fill="#0f172a", outline="#38bdf8", width=2)
        brand = reshape_text("NextMind HQ | @nextmind.hq")
        draw.text((540, 195), brand, fill="#38bdf8", font=font_brand, anchor="mm")

        # کادر کاور
        draw.rounded_rectangle([80, 750, 1000, 1170], radius=30, fill="#0f172a", outline="#8b5cf6", width=3)
        t_text = reshape_text(title)
        draw.text((540, 900), t_text, fill="#ffffff", font=font_title, anchor="mm")

        s_text = reshape_text(subtitle)
        draw.text((540, 1040), s_text, fill="#38bdf8", font=font_sub, anchor="mm")

        # فوتر
        footer = reshape_text("کار ۱۰ ساعته رو با هوش مصنوعی تو ۱۰ دقیقه جمع کن ⚡")
        draw.text((540, 1750), footer, fill="#64748b", font=font_brand, anchor="mm")

        cover_path = str(STORIES_DIR / f"reel_cover_{int(time.time())}.jpg")
        img.save(cover_path, quality=95)
        return cover_path

    def publish_reel_now(self, video_path: str, topic: str = "خلاصه‌ساز ۳۰ ثانیه‌ای ویدیوهای ۲ ساعته با NoteGPT") -> bool:
        """انتشار مستقیم یک فایل ویدیویی به عنوان ریلز در اینستاگرام"""
        try:
            v_path = Path(video_path)
            if not v_path.exists():
                print(f"[Content Engine] Video file not found: {video_path}")
                return False

            print(f"[Content Engine] Generating viral caption for Reel: {topic}...")
            caption = self.generate_viral_reel_package(topic)

            print("[Content Engine] Generating high-res cyber cover...")
            cover_path = self.create_reel_cover(title=topic, subtitle="ترفندهای پولساز نکسوس 🧠")

            if not insta_manager.is_logged_in:
                insta_manager.login()

            print(f"[Content Engine] Uploading video to Instagram Reels @nextmind.hq ({v_path.name})...")
            media = self.client.clip_upload(
                path=v_path,
                caption=caption,
                thumbnail=Path(cover_path),
                show_preview_in_feed=True
            )
            print(f"[Content Engine] ✅ Reel published successfully! PK: {media.pk}, Code: {media.code}")
            return True
        except Exception as e:
            print(f"[Content Engine Error] Failed to publish Reel: {e}")
            return False

    def check_and_trigger_schedule(self):
        """بررسی ساعت و زمان‌بندی طلایی انتشار برای ارسال خودکار استوری‌ها و ریلزها"""
        # انتشار خودکار غیرفعال است و محتواها توسط خود کاربر منتشر می‌شوند
        return
        hour = now.hour
        minute = now.minute
        today_str = now.strftime("%Y-%m-%d")

        # ۱. اسلات استوری عصر (ساعت 17:15 تا 18:30 - تیزر ریلز شب: خلاصه‌ساز ویدیو NoteGPT)
        if 17 <= hour < 19:
            slot = "evening_story"
            if not is_slot_published(slot, today_str):
                print(f"[Content Scheduler] ⏰ زمان طلایی استوری عصر فرا رسید ({hour}:{minute:02d}). در حال تولید و انتشار...")
                success = self.publish_story_now(topic="خلاصه‌ساز ۳۰ ثانیه‌ای ویدیوهای ۲ ساعته و جزوه‌سازی هوشمند با NoteGPT")
                if success:
                    log_published_slot(slot, today_str, "story", "NoteGPT Teaser", "published")

        # ۲. اسلات انتشار ریلز شب (ساعت 20:30 تا 21:30 - تایم طلایی اکسپلور در ایران)
        if 20 <= hour < 22 and (hour > 20 or minute >= 30):
            slot_reel = "night_reel"
            if not is_slot_published(slot_reel, today_str):
                # بررسی وجود فایل ویدیو در پوشه صف انتشار reels_queue
                video_files = [f for f in REELS_DIR.glob("*.mp4") if f.is_file()]
                if video_files:
                    target_video = video_files[0]
                    print(f"[Content Scheduler] 🎬 ویدیوی آماده در صف ریلز پیدا شد: {target_video.name}. در حال انتشار خودکار...")
                    reel_topic = "خلاصه‌ساز ۳۰ ثانیه‌ای ویدیوهای ۲ ساعته با NoteGPT"
                    success = self.publish_reel_now(str(target_video), topic=reel_topic)
                    if success:
                        log_published_slot(slot_reel, today_str, "reel", reel_topic, "published")
                        # انتقال ویدیو به پوشه بایگانی منتشره‌ها
                        try:
                            target_video.rename(REELS_PUBLISHED_DIR / target_video.name)
                        except Exception:
                            pass
                else:
                    # اگر ویدیویی در صف نبود
                    pass

            # ۳. اسلات استوری شب (ساعت 20:35 تا 22:00 - لید مگنت و کال‌تواکشن بعد از ریلز)
            slot_story = "night_story"
            if not is_slot_published(slot_story, today_str):
                print(f"[Content Scheduler] ⏰ زمان طلایی استوری شب فرا رسید ({hour}:{minute:02d}). در حال تولید و انتشار...")
                success = self.publish_story_now(topic="دریافت رایگان تقلب‌نامه خلاصه‌ساز ویدیوی NoteGPT")
                if success:
                    log_published_slot(slot_story, today_str, "story", "NoteGPT Lead Magnet", "published")

        # ۴. اسلات استوری صبح (ساعت 10:15 تا 12:00 - آموزش اول روز: ابزار اینفوگرافیک‌ساز Napkin AI)
        elif 10 <= hour < 12 and (hour > 10 or minute >= 15):
            slot = "morning_story"
            if not is_slot_published(slot, today_str):
                print(f"[Content Scheduler] ⏰ زمان طلایی استوری صبح فرا رسید ({hour}:{minute:02d}). در حال تولید و انتشار...")
                success = self.publish_story_now(topic="تبدیل متن و یادداشت به اینفوگرافیک و دیاگرام در ۱۰ ثانیه با Napkin AI")
                if success:
                    log_published_slot(slot, today_str, "story", "Napkin AI Infographics", "published")

content_engine = AutonomousContentEngine()
