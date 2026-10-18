import os
from pathlib import Path
from fastapi import FastAPI, Request, Query, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse
from config import META_VERIFY_TOKEN, KEYWORD_TRIGGERS
from database import get_stats, get_all_leads
from modules.official_api.comment_handler import process_comment_event
from modules.official_api.dm_handler import process_dm_event

app = FastAPI(title="NextMind Instagram Bot Webhook Server", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_PATH = BASE_DIR / "templates" / "dashboard.html"

@app.get("/", response_class=HTMLResponse)
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Serves the complete Persian web admin dashboard"""
    if TEMPLATE_PATH.exists():
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>داشبورد یافت نشد</h1>", status_code=404)

@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Verification endpoint required by Meta Developer portal."""
    if hub_mode == "subscribe" and hub_verify_token == META_VERIFY_TOKEN:
        print("[Webhook Verification] Token matched successfully!")
        return Response(content=hub_challenge, media_type="text/plain")
    else:
        raise HTTPException(status_code=403, detail="Verification token mismatch")

@app.post("/webhook")
async def handle_webhook(request: Request):
    """Main webhook receiver for live comments and direct messages."""
    payload = await request.json()
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") == "comments" and change.get("value"):
                process_comment_event(change["value"])
        for messaging in entry.get("messaging", []):
            sender_id = messaging.get("sender", {}).get("id")
            text = messaging.get("message", {}).get("text")
            if sender_id and text:
                process_dm_event(sender_id, text)
    return {"status": "ok"}

# -------------------------------------------------------------
# REST APIs for Web Admin Dashboard
# -------------------------------------------------------------
@app.get("/api/stats")
async def api_stats():
    return get_stats()

@app.get("/api/triggers")
async def api_triggers():
    return KEYWORD_TRIGGERS

@app.post("/api/triggers")
async def api_add_trigger(request: Request):
    data = await request.json()
    kw = data.get("keyword")
    reply = data.get("reply_text")
    follow = data.get("require_follow", False)
    if kw and reply:
        KEYWORD_TRIGGERS[kw] = {"reply_text": reply, "require_follow": follow}
        return {"success": True, "triggers": KEYWORD_TRIGGERS}
    raise HTTPException(status_code=400, detail="Missing keyword or reply_text")

@app.delete("/api/triggers/{keyword}")
async def api_delete_trigger(keyword: str):
    if keyword in KEYWORD_TRIGGERS:
        del KEYWORD_TRIGGERS[keyword]
        return {"success": True}
    raise HTTPException(status_code=404, detail="Keyword not found")

@app.get("/api/leads")
async def api_leads():
    return get_all_leads()

@app.post("/api/test-comment")
async def test_comment(data: dict):
    process_comment_event(data)
    return {"status": "processed", "data": data}

@app.post("/api/test-dm")
async def test_dm(data: dict):
    result = process_dm_event(
        sender_id=data.get("sender_id", "test_u1"),
        message_text=data.get("text", data.get("message_text", "")),
        username=data.get("username", "test_user")
    )
    return {"status": "processed", "result": result}

@app.get("/api/insta/status")
async def api_insta_status():
    import os
    from config import INSTA_USERNAME, INSTA_SESSION_FILE
    has_session = os.path.exists(INSTA_SESSION_FILE)
    return {
        "username": INSTA_USERNAME,
        "has_session": has_session,
        "authenticated": has_session,
        "mode": "Direct Automation Engine"
    }
