import json
import sqlite3
import urllib.request
import os

DB_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/db/MTGT1-ledger.db"

def load_env_variable(key_name, default_value="omlx-local"):
    """Reads secret tokens from the local hidden .env file manually without external libraries."""
    env_path = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/.env"
    if not os.path.exists(env_path):
        return default_value
    try:
        with open(env_path, "r") as f:
            for line in f:
                if line.strip().startswith(key_name):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        return parts[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return default_value

OMLX_KEY = load_env_variable("OMLX_API_KEY")
AGENTMAIL_KEY = load_env_variable("AGENTMAIL_API_KEY")
INBOX_ID = load_env_variable("AGENTMAIL_INBOX_ID")

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
    url = f"https://api.agentmail.to/v0/inboxes/{INBOX_ID}/messages/send"
    payload = {
        "to": to_email,
        "subject": subject,
        "text": body_content
    }
    
    if AGENTMAIL_KEY == "omlx-local":
        print(f"   📊 [Sandbox Simulation] Packet routed to carrier routing array for: {to_email}")
        return True, "Simulated network handshake clear."
        
    try:
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json", 
                "Authorization": f"Bearer {AGENTMAIL_KEY}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return True, "Email successfully queued with backend relay."
    except Exception as e:
        return False, str(e)
