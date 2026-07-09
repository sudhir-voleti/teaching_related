import sys
import os
import json
import urllib.request
import base64
import mimetypes

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.global_utils import AGENTMAIL_KEY, INBOX_ID

def execute_send_email(recipients, subject, body_content, html_content=None, image_path=None):
    """
    Unified email engine utilizing AgentMail's native attachment array primitives.
    Guarantees structural rendering compatibility across modern webmail systems like Gmail.
    """
    if isinstance(recipients, str):
        recipients = [r.strip() for r in recipients.split(",") if r.strip()]
        
    print(f"📬 [Email Engine] Processing dispatch request for targets: {recipients}")
    success_count = 0
    
    # Structure the attachment metadata payload if a file target path is present
    attachment_payload = []
    if image_path and os.path.exists(image_path):
        try:
            mime_type, _ = mimetypes.guess_type(image_path)
            mime_type = mime_type or "image/png"
            filename = os.path.basename(image_path)
            
            with open(image_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                
            attachment_payload.append({
                "content": encoded_string,
                "filename": filename,
                "content_type": mime_type
            })
            print(f"📎 Attached visual asset: {filename} ({mime_type})")
        except Exception as e:
            print(f"⚠️ Attachment binary processing error: {str(e)}")

    for target in recipients:
        url = f"https://api.agentmail.to/v0/inboxes/{INBOX_ID}/messages"
        
        payload = {
            "to": target,
            "subject": subject,
            "text": body_content
        }

        if html_content:
            payload["html"] = html_content
            
        if attachment_payload:
            payload["attachments"] = attachment_payload

        # Execution attempt via AgentMail REST surface
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
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status in [200, 201]:
                    print(f"   📬 Delivered -> {target}")
                    success_count += 1
                    continue
        except Exception:
            pass
            
        # Alternate Route Fallback Pipeline Check
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
            with urllib.request.urlopen(req_alt, timeout=12) as response_alt:
                if response_alt.status in [200, 201]:
                    print(f"   📬 Delivered -> {target}")
                    success_count += 1
        except Exception as err:
            print(f"   ❌ Delivery failure for {target}: {str(err)}")
            
    return f"Distributed packets successfully to {success_count} endpoints."
