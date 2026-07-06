import sys
import os
import time
import json
import re
import urllib.request

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.global_utils import AGENTMAIL_KEY, INBOX_ID, query_omlx_llm
from tools.send_email import execute_send_email
from mcp_servers import mcp_filesystem, mcp_sqlite

LOG_FILE = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/gateway/processed_emails.txt"

def get_processed_ids():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def mark_id_as_processed(msg_id):
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg_id}\n")

def run_agent_reasoning_cycle(conversation_history):
    system_prompt = """You are Ornith-1.0-9B, the sovereign cognitive operating center for the MTGT1 Course Agent OS. 
Analyze the conversation history and historical tool execution results to determine your next action.

You must reply in exactly one of two clean formats. Do not wrap your response in markdown fences.

Format Option A (If you need to call a tool to get information or modify the environment):
{"tool_call": "name_of_tool", "arguments": {...}}

Format Option B (If you have completely fulfilled the user's intent and are ready to issue your final response or status):
{"final_response": "Your structured update text or outbound notification confirmation message goes here"}

Available Tool Catalog:
1. tool_call: "create_directory" | args: {"subfolder": "string path", "name": "string folder name"}
2. tool_call: "list_directory"   | args: {"subfolder": "string path"}
3. tool_call: "database_query"   | args: {"sql_command": "raw SQL text"}
4. tool_call: "send_email"       | args: {"recipients": ["array of email strings"], "subject": "string", "body_content": "string"}

Orchestration Guide for Emails:
- Private Admin Replies: If the professor asks you a question or requests a schema/file report back to them, use 'send_email' targeting ONLY the professor's email address (e.g., ["sudhir.voleti@gmail.com"]).
- Global Class Announcements: If the professor explicitly asks you to broadcast an announcement to the class or student group, use 'send_email' targeting the sandbox cohort array: ["archanadilpali@gmail.com", "profsudhirvoleti@gmail.com", "sudhir.voleti@gmail.com", "sudhir_voleti@isb.edu"].

Keep looping until you can generate a complete 'final_response' block."""

    response_text = query_omlx_llm(
        model_name="Ornith-1.0-9B-oQ4-fp16",
        system_prompt=system_prompt,
        user_prompt=json.dumps(conversation_history),
        temperature=0.1
    )
    
    clean_json = response_text.replace("```json", "").replace("```", "").strip()
    if "</think>" in clean_json:
        clean_json = clean_json.split("</think>")[-1].strip()
    
    match = re.search(r"({.*})", clean_json, re.DOTALL)
    if match:
        clean_json = match.group(1)
        
    try:
        return json.loads(clean_json)
    except Exception:
        return {"final_response": f"Parsing glitch on response agent packet: {response_text}"}

def orchestrate_agent_loop(initial_email_body):
    print("🦅 [Agent Loop Initialization] Processing user intent packet...")
    history = [{"role": "user", "content": initial_email_body}]
    
    for execution_turn in range(5):
        decision = run_agent_reasoning_cycle(history)
        
        if "final_response" in decision:
            print(f"✨ [Task Resolution] Ornith completed the assignment:\n{decision['final_response']}")
            break
            
        elif "tool_call" in decision:
            tool_name = decision["tool_call"]
            args = decision.get("arguments", {})
            print(f"🛠️  [System Call] Brain invoked tool: {tool_name} with parameters: {args}")
            
            observation = ""
            if tool_name == "create_directory":
                observation = str(mcp_filesystem.create_directory(args.get("subfolder", ""), args.get("name", "")))
            elif tool_name == "list_directory":
                observation = str(mcp_filesystem.list_directory(args.get("subfolder", "")))
            elif tool_name == "database_query":
                observation = str(mcp_sqlite.execute_query(args.get("sql_command", "")))
            elif tool_name == "send_email":
                observation = execute_send_email(
                    recipients=args.get("recipients", []),
                    subject=args.get("subject", "⚠️ Administrative Routing Alert"),
                    body_content=args.get("body_content", "")
                )
            else:
                observation = f"Error: Tool '{tool_name}' is not wired into daemon execution matrix."
                
            print(f"📊 [Observation Recorded]: {observation}")
            history.append({"role": "assistant", "content": f"Executed tool {tool_name}. Result: {observation}"})
        else:
            break

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
            
            if msg_id in processed_ids or not any(admin in sender for admin in ["sudhir_voleti@isb.edu", "sudhir.voleti@gmail.com", "profsudhirvoleti@gmail.com"]):
                continue
                
            print(f"\n🔥 [Intercepted] Inbound Administrative Signal: {msg_id}")
            mark_id_as_processed(msg_id)
            orchestrate_agent_loop(body)
            break
    except Exception as e:
        print(f"⚠️ Gateway Daemon Polling Hiccup: {str(e)}")

if __name__ == "__main__":
    print("📡 OS CONTINUOUS REASONING LOOP LIVE (UNIFIED COMMUNICATIONS MATRIX ACTIVE)...")
    while True:
        check_inbound_commands()
        time.sleep(15)
