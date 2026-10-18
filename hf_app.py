import os
import sys
import threading
import time
from fastapi import FastAPI
import uvicorn

# Initialize FastAPI app for Hugging Face Spaces port 7860
app = FastAPI(title="NextMind HQ Instagram Automation Space")

# Write session file if passed in environment variable
session_env = os.environ.get("INSTA_SESSION_JSON")
if session_env and not os.path.exists("insta_session.json"):
    try:
        with open("insta_session.json", "w", encoding="utf-8") as f:
            f.write(session_env)
        print("[HF Space] Successfully initialized insta_session.json from secret.")
    except Exception as e:
        print(f"[HF Space] Error writing session: {e}")

def run_instagram_monitor():
    """Background thread to run InstagramDirectMonitor 24/7"""
    try:
        from monitor_service import InstagramDirectMonitor
        print("[HF Space] Starting 24/7 Instagram Direct Monitor...")
        monitor = InstagramDirectMonitor()
        monitor.start()
    except Exception as e:
        print(f"[HF Space Monitor Error] {e}")

@app.on_event("startup")
def startup_event():
    # Start monitor in daemon thread
    t = threading.Thread(target=run_instagram_monitor, daemon=True)
    t.start()

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "NextMind HQ - 24/7 Instagram Autonomous Engine",
        "cloud": "Hugging Face Spaces (Always On)",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"[NextMind Cloud] Binding to port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
