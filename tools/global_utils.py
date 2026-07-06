import json
import sqlite3
import urllib.request

DB_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/db/MTGT1-ledger.db"
OMLX_KEY = "omlx-local"
AGENTMAIL_KEY = "omlx-local"  # Swap with production AgentMail credentials when active

def query_omlx_llm(model_name, system_prompt, user_prompt, temperature=0.3):
    """Universal helper to communicate with locally hosted vLLM engines."""
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature
    }
    try:
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {OMLX_KEY}"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"LLM Generation Error: {str(e)}"

def send_agentmail_packet(to_email, subject, body_content):
    """Universal outbound helper to dispatch tracking messages via AgentMail."""
    url = "https://api.agentmail.to/v1/send"
    payload = {
        "to": to_email,
        "subject": subject,
        "body": body_content
    }
    try:
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {AGENTMAIL_KEY}"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return True, "Email successfully queued with backend relay."
    except Exception as e:
        return False, str(e)
