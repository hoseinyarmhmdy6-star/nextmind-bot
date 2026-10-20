import sqlite3
from datetime import datetime
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Processed Comments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_comments (
        comment_id TEXT PRIMARY KEY,
        post_id TEXT,
        user_id TEXT,
        username TEXT,
        comment_text TEXT,
        keyword_matched TEXT,
        dm_sent INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Users / Leads Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        is_following INTEGER DEFAULT 0,
        last_keyword TEXT,
        lead_magnet_delivered INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. Competitor Scraped Accounts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS competitor_leads (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        competitor_source TEXT,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        followed_at TIMESTAMP NULL,
        unfollowed_at TIMESTAMP NULL,
        liked_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending' -- pending, followed, unfollowed, error
    )
    """)

    # 4. DM History & AI Interaction Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dm_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        username TEXT,
        sender TEXT, -- 'user', 'bot', 'ai'
        message_text TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 5. Processed Inbound DMs Deduplication Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_dms (
        message_id TEXT PRIMARY KEY,
        thread_id TEXT,
        user_id TEXT,
        username TEXT,
        message_text TEXT,
        reply_text TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. Content Scheduling & Publishing Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS published_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_name TEXT,
        date_str TEXT,
        media_type TEXT,
        topic TEXT,
        media_id TEXT,
        published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(slot_name, date_str)
    )
    """)

    conn.commit()
    conn.close()
    
    # همگام‌سازی ابری حافظه ضداسپم برای جلوگیری از ارسال پیام‌های تکراری و بی‌مورد
    sync_processed_from_cloud()

def push_processed_to_cloud(comment_id: str = None, user_id: str = None, dm_id: str = None):
    """ذخیره شناسه پردازش‌شده در حافظه ابری کلودفلر تا در هیچ کانتینری در گیت‌هاب اکشن پیام تکراری ارسال نشود"""
    try:
        import urllib.request, json
        payload = {}
        if comment_id: payload["comment_id"] = str(comment_id)
        if user_id: payload["user_id"] = str(user_id)
        if dm_id: payload["dm_id"] = str(dm_id)
        if not payload: return
        req = urllib.request.Request(
            "https://nextmind-bot.hoseinyarmhmdy6.workers.dev/api/processed-ids",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        )
        urllib.request.urlopen(req, timeout=4)
    except Exception:
        pass

def sync_processed_from_cloud():
    """همگام‌سازی بلادرنگ حافظه ضداسپم از سرور ابری کلودفلر به دیتابیس لوکال (حیاتی برای گیت‌هاب اکشن)"""
    try:
        import urllib.request, json
        req = urllib.request.Request(
            "https://nextmind-bot.hoseinyarmhmdy6.workers.dev/api/processed-ids",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        res = urllib.request.urlopen(req, timeout=4)
        data = json.loads(res.read())
        conn = get_connection()
        cursor = conn.cursor()
        
        # ثبت کامنت‌های پردازش‌شده در حافظه دائم
        for cid in data.get("comments", []):
            cursor.execute("""
                INSERT OR IGNORE INTO processed_comments (comment_id, post_id, user_id, username, comment_text, keyword_matched, dm_sent)
                VALUES (?, 'cloud_synced', 'cloud_user', 'synced', 'cloud comment', 'synced', 1)
            """, (str(cid),))

        # ثبت کاربرانی که پکیج را دریافت کرده‌اند (جلوگیری قطعی از ارسال مجدد دایرکت)
        for uid in data.get("delivered_users", []):
            cursor.execute("""
                INSERT INTO leads (user_id, username, is_following, last_keyword, lead_magnet_delivered)
                VALUES (?, 'protected_user', 1, 'protected', 1)
                ON CONFLICT(user_id) DO UPDATE SET lead_magnet_delivered = 1
            """, (str(uid),))

        conn.commit()
        conn.close()
    except Exception:
        pass

def is_slot_published(slot_name: str, date_str: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM published_schedule WHERE slot_name = ? AND date_str = ?", (slot_name, date_str))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def log_published_slot(slot_name: str, date_str: str, media_type: str, topic: str, media_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO published_schedule (slot_name, date_str, media_type, topic, media_id)
        VALUES (?, ?, ?, ?, ?)
    """, (slot_name, date_str, media_type, topic, media_id))
    conn.commit()
    conn.close()

def is_dm_processed(message_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_dms WHERE message_id = ?", (message_id,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def log_processed_dm(message_id: str, thread_id: str, user_id: str, username: str, message_text: str, reply_text: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO processed_dms (message_id, thread_id, user_id, username, message_text, reply_text)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (message_id, thread_id, user_id, username, message_text, reply_text))
    cursor.execute("""
        INSERT INTO dm_logs (user_id, username, sender, message_text)
        VALUES (?, ?, 'user', ?)
    """, (user_id, username, message_text))
    cursor.execute("""
        INSERT INTO dm_logs (user_id, username, sender, message_text)
        VALUES (?, ?, 'ai', ?)
    """, (user_id, username, reply_text))
    conn.commit()
    conn.close()

def is_comment_processed(comment_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_comments WHERE comment_id = ?", (comment_id,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def has_user_commented_on_post(post_id: str, user_id: str) -> bool:
    """بررسی اینکه آیا ربات قبلاً به این کاربر زیر این پست یا ریلز پاسخ داده است (قانون پاسخ یکباره به هر نفر زیر یک پست)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM processed_comments 
        WHERE post_id = ? AND user_id = ? AND keyword_matched != 'already_replied'
    """, (str(post_id), str(user_id)))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def log_comment(comment_id: str, post_id: str, user_id: str, username: str, comment_text: str, keyword: str, dm_sent: bool = True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO processed_comments (comment_id, post_id, user_id, username, comment_text, keyword_matched, dm_sent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (comment_id, post_id, user_id, username, comment_text, keyword, 1 if dm_sent else 0))
    conn.commit()
    conn.close()
    push_processed_to_cloud(comment_id=comment_id, user_id=user_id)

def update_user_status(user_id: str, username: str, is_following: bool = False, keyword: str = None, delivered: bool = False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (user_id, username, is_following, last_keyword, lead_magnet_delivered, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            is_following=excluded.is_following,
            last_keyword=coalesce(excluded.last_keyword, leads.last_keyword),
            lead_magnet_delivered=excluded.lead_magnet_delivered,
            updated_at=CURRENT_TIMESTAMP
    """, (user_id, username, 1 if is_following else 0, keyword, 1 if delivered else 0))
    conn.commit()
    conn.close()
    if delivered:
        push_processed_to_cloud(user_id=user_id)

def get_user_lead(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return dict(res) if res else None

def log_dm(user_id: str, username: str, sender: str, message_text: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO dm_logs (user_id, username, sender, message_text)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, sender, message_text))
    conn.commit()
    conn.close()

def save_competitor_leads(leads: list, competitor: str):
    conn = get_connection()
    cursor = conn.cursor()
    for lead in leads:
        cursor.execute("""
            INSERT OR IGNORE INTO competitor_leads (user_id, username, competitor_source, status)
            VALUES (?, ?, ?, 'pending')
        """, (str(lead['id']), lead['username'], competitor))
    conn.commit()
    conn.close()

def get_pending_competitor_leads(limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM competitor_leads WHERE status = 'pending' LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_lead_followed(user_id: str, liked_count: int = 0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE competitor_leads
        SET status = 'followed', followed_at = CURRENT_TIMESTAMP, liked_count = ?
        WHERE user_id = ?
    """, (liked_count, user_id))
    conn.commit()
    conn.close()

def get_today_followed_count() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM competitor_leads WHERE status = 'followed' AND date(followed_at) = date('now')")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM processed_comments")
    comments_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leads")
    leads_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM competitor_leads WHERE status = 'followed'")
    followed_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM competitor_leads WHERE status = 'pending'")
    pending_count = cursor.fetchone()[0]
    conn.close()
    return {
        "comments_handled": comments_count,
        "total_leads": leads_count,
        "competitor_followed": followed_count,
        "competitor_pending": pending_count
    }

def get_all_leads(limit: int = 50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY updated_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Initialize tables on import
init_db()
