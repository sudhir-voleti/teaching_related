import sys
import os
import json
import urllib.request

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.global_utils import AGENTMAIL_KEY, INBOX_ID

def execute_send_email(recipients, subject, body_content):
    """
    Unified multi-recipient email utility tool for the Agent OS.
    Handles single administrative replies and global class distributions.
    """
    if isinstance(recipients, str):
        recipients = [r.strip() for r in recipients.split(",") if r.strip()]
        
    print(f"📬 [Email Engine] Processing dispatch request for targets: {recipients}")
    success_count = 0
    
    for target in recipients:
        url = f"https://api.agentmail.to/v0/inboxes/{INBOX_ID}/messages"
        payload = {
            "to": target,
            "subject": subject,
            "text": body_content
        }
        
        # Primary Routing Attempt
        try:
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {AGENTMAIL_KEY}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status in [200, 201]:
                    print(f"   📬 Delivered -> {target}")
                    success_count += 1
                    continue
        except Exception:
            pass
            
        # Alt Route Fallback
        try:
            url_alt = f"https://api.agentmail.to/v0/inboxes/{INBOX_ID}/messages/send"
            req_alt = urllib.request.Request(
                url_alt,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {AGENTMAIL_KEY}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req_alt, timeout=10) as response_alt:
                if response_alt.status in [200, 201]:
                    print(f"   📬 Delivered -> {target}")
                    success_count += 1
        except Exception as err:
            print(f"   ❌ Delivery failure for {target}: {str(err)}")
            
    return f"Distributed packets successfully to {success_count} endpoints."
