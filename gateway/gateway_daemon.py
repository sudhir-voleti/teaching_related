import sys
import os
import time
import json
import urllib.request

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.global_utils import AGENTMAIL_KEY, INBOX_ID
from tools.broadcast_to_all import execute_generic_broadcast

def check_inbound_commands():
    """Polls the AgentMail v0 endpoint for new unread messages sent by the instructor."""
    url = f"https://api.agentmail.to/v0/inboxes/{INBOX_ID}/messages?status=unread"
    
    if AGENTMAIL_KEY == "omlx-local":
        print("📊 [Sandbox Mode] Polling skipped. System awaiting active production credentials.")
        return
        
    try:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {AGENTMAIL_KEY}"})
        with urllib.request.urlopen(req, timeout=10) as response:
            messages = json.loads(response.read().decode('utf-8'))
            
        for msg in messages.get("data", []):
            sender = msg.get("from", "")
            body = msg.get("text", "")
            
            if "sudhir_voleti@isb.edu" not in sender and "sudhir.voleti@gmail.com" not in sender:
                continue
                
            print(f"🦅 [Gateway Message Intercepted] Processing content payload from: {sender}")
            
            if "[SYSTEM-COMMAND]: ROSTER_ALERT" in body or "email the roster" in body.lower():
                print("📣 Intent Mapped: Initiating Global Course Broadcast sequence...")
                clean_body = body.replace("[SYSTEM-COMMAND]: ROSTER_ALERT", "").strip()
                
                execute_generic_broadcast(
                    course_code="MTGT",
                    subject="⚠️ Class Update: Marketing Course Announcement",
                    body_content=clean_body
                )
                
                # Mark message as read/processed on server
                mark_as_read_url = f"https://api.agentmail.to/v0/inboxes/{INBOX_ID}/messages/{msg['id']}/read"
                mark_req = urllib.request.Request(mark_as_read_url, headers={"Authorization": f"Bearer {AGENTMAIL_KEY}"}, method="POST")
                urllib.request.urlopen(mark_req, timeout=5)
                
    except Exception as e:
        print(f"⚠️ Gateway Daemon Polling Hiccup: {str(e)}")

if __name__ == "__main__":
    print("📡 MARKETING AGENT OS INBOUND GATEWAY PORTAL ACTIVATED...")
    print("Watching for verified email command packets loop. Press Ctrl+C to terminate.")
    while True:
        check_inbound_commands()
        time.sleep(30)
