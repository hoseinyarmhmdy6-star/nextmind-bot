import os
import sys
import time
import json

# Ensure immediate unbuffered output in GitHub Actions
sys.stdout.reconfigure(encoding='utf-8')
print("=" * 60)
print("🚀 NextMind HQ - Autonomous Instagram Cloud Engine 🚀")
print(f"[*] Started at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
print("=" * 60)

# 1. Restore Instagram session from Secret if present
session_data = os.environ.get("INSTA_SESSION_JSON")
if session_data and not os.path.exists("insta_session.json"):
    try:
        with open("insta_session.json", "w", encoding="utf-8") as f:
            f.write(session_data)
        print("[Cloud Init] Successfully restored insta_session.json from Secret.")
    except Exception as e:
        print(f"[Cloud Init Error] Could not restore session: {e}")

# 2. Maximum duration for this runner cycle (default 300 minutes = 5 hours)
# GitHub Actions allows up to 360 minutes (6 hours) per job
run_duration_minutes = int(os.environ.get("RUN_DURATION_MINUTES", "300"))
end_time = time.time() + (run_duration_minutes * 60)
print(f"[*] Scheduled runtime: {run_duration_minutes} minutes (until {time.strftime('%H:%M:%S', time.localtime(end_time))}).")

# 3. Start Instagram Direct Monitor
try:
    from database import init_db
    init_db()
    
    from monitor_service import InstagramDirectMonitor
    from config import INSTA_USERNAME

    monitor = InstagramDirectMonitor()
    
    print(f"[*] Authenticating @{INSTA_USERNAME}...")
    from modules.automation.insta_client import insta_manager
    if not insta_manager.login():
        print("[-] Login failed. Exiting.")
        sys.exit(1)
        
    print("[+] Successfully connected to Instagram API via device context!")
    print("[+] Starting high-speed real-time polling loop...")
    
    loop_count = 0
    while time.time() < end_time:
        loop_count += 1
        try:
            # 1. Check DMs every cycle (real-time responsiveness)
            monitor.check_direct_messages()
            
            # 2. Check Comments every 4 cycles (every ~45s)
            if loop_count % 4 == 0:
                monitor.check_latest_comments()

            # 3. Live Sync stats to Cloudflare KV every 8 cycles (~1.5 min)
            if loop_count % 8 == 0:
                try:
                    monitor.sync_live_profile()
                except Exception as es:
                    print(f"[Cloud Live Sync Error] {es}")

            # 4. 24/7 Organic Growth & High-Impact Audience Acquisition from live competitors every 4 cycles (~50s)
            if loop_count % 4 == 0:
                try:
                    from modules.automation.competitor_growth import run_safe_growth_tick
                    run_safe_growth_tick(max_targets=1)
                except Exception as eg:
                    print(f"[Cloud Growth Error] {eg}")
                
            # Rest 10-14 seconds between polls
            time.sleep(12)
            
        except Exception as e:
            print(f"[Loop Exception] {e}")
            time.sleep(15)

    print(f"[+] Reached scheduled runtime limit of {run_duration_minutes}m.")
    print("[*] Handing over cleanly to the next scheduled relay cycle.")

except Exception as fatal:
    print(f"[Fatal Engine Error] {fatal}")
    sys.exit(1)
