import sys
import os
import time
import json
import urllib.request

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.global_utils import AGENTMAIL_KEY, INBOX_ID, query_omlx_llm
from tools.broadcast_to_all import execute_generic_broadcast
from mcp_servers import mcp_filesystem, mcp_sqlite, mcp_code_runner

LOG_FILE = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/gateway/processed_emails.txt"

def get_processed_ids():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def mark_id_as_processed(msg_id):
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg_id}\n")

def ask_ornith_to_route(email_body):
    """Feeds the text to Ornith-9B along with tool metadata definitions for zero-shot intent parsing."""
    system_prompt = """You are Ornith-9B, the Intent Parse Gateway for the MTGT1 Course Agent OS. Your job is to read an administrative command email and route it to the correct Model Context Protocol (MCP) tool or custom skill utility.

You must reply with ONLY a valid raw JSON object. Do not enclose it in markdown code blocks or add conversational text.

Available Tools:
1. intent: "create_directory"
   Description: Builds a new folder inside a specific lecture path.
   Arguments: {"subfolder": "string containing parent directory, e.g. Lec01", "name": "string name of folder"}

2. intent: "list_directory"
   Description: Lists the contents of a directory.
   Arguments: {"subfolder": "string target subfolder name"}

3. intent: "broadcast_to_all"
   Description: Blasts a course-wide announcement or email notification to all student rosters.
   Arguments: {"body_content": "the message string to deliver to students"}

4. intent: "database_query"
   Description: Runs read-only queries or administrative roster modifications against the SQLite file.
   Arguments: {"sql_command": "raw standard SQL statement to run"}

5. intent: "unknown"
   Description: Use this if the intent is not clear or doesn't map cleanly.

Example Output format:
{"intent": "create_directory", "arguments": {"subfolder": "Lec01", "name": "test1"}}"""

    # Call your local endpoint via global_utils helper
    response_text = query_omlx_llm(
        model_name="ornith-9b", 
        system_prompt=system_prompt, 
        user_prompt=email_body, 
        temperature=0.1
    )
    
    # Strip away accidental markdown ticks if the model emits them
    clean_json = response_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean_json)
    except Exception:
        print(f"⚠️ Failed to parse JSON from Ornith. Raw text was: {response_text}")
        return {"intent": "unknown", "arguments": {}}

def execute_parsed_intent(routing_pack):
    intent = routing_pack.get("intent")
    args = routing_pack.get("arguments", {})
    
    print(f"🦅 [Ornith Routing] Mapped Intent -> {intent} with args: {args}")
    
    if intent == "create_directory":
        res = mcp_filesystem.create_directory(args.get("subfolder", ""), args.get("name", ""))
        print(f"📁 MCP File Response: {res}")
        
    elif intent == "list_directory":
        res = mcp_filesystem.list_directory(args.get("subfolder", ""))
        print(f"📁 MCP File List Response: {res}")
        
    elif intent == "database_query":
        res = mcp_sqlite.execute_query(args.get("sql_command", ""))
        print(f"🗄️ MCP SQLite Response: {res}")
        
    elif intent == "broadcast_to_all":
        print("📣 Executing Global Course Broadcast execution chain...")
        execute_generic_broadcast(
            course_code="MTGT",
            subject="⚠️ Class Update: Marketing Course Announcement",
            body_content=args.get("body_content", "")
        )
    else:
        print("❓ Intent mapped to unknown or unhandled pathway. No action taken.")

def check_inbound_commands():
    url = f"https://api.agentmail.to/v0/inboxes/{INBOX_ID}/messages"
    if AGENTMAIL_KEY == "omlx-local":
        return
        
    try:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {AGENTMAIL_KEY}"})
        with urllib.request.urlopen(req, timeout=10) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            
        messages_list = res_json.get("messages", [])
        processed_ids = get_processed_ids()
        
        for msg in messages_list:
            sender = msg.get("from", "")
            subject = msg.get("subject", "")
            body = msg.get("text", msg.get("preview", ""))
            msg_id = msg.get("message_id", msg.get("id", f"{sender}_{subject}")).strip()
            
            if msg_id in processed_ids:
                continue
                
            allowed_senders = ["sudhir_voleti@isb.edu", "sudhir.voleti@gmail.com", "profsudhirvoleti@gmail.com"]
            if not any(admin_email in sender for admin_email in allowed_senders):
                continue
                
            print(f"🔥 [Intercepted] New Inbound Administrative Token Found. Lockout ID: {msg_id}")
            mark_id_as_processed(msg_id)
            
            # Pass the body text off to the router engine
            routing_pack = ask_ornith_to_route(body)
            execute_parsed_intent(routing_pack)
            break
                
    except Exception as e:
        print(f"⚠️ Gateway Daemon Polling Hiccup: {str(e)}")

if __name__ == "__main__":
    print("📡 OS INTEGRATED MCP GATEWAY ACTIVATED (ORNITH INTENT ROUTER ENGINE LIVE)...")
    while True:
        check_inbound_commands()
        time.sleep(15)
