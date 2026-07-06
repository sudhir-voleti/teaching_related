import sys
import os
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from global_utils import query_omlx_llm, send_agentmail_packet, DB_PATH

def execute_hermes_broadcast(course_code, lecture_id):
    """
    Pulls the active student cohort emails from the database ledger, uses the local LLM
    to generate an introductory message from Agent Hermes, and broadcasts it out.
    """
    print(f"📣 [Hermes Engine] Initializing system welcome broadcast for {course_code} - {lecture_id}...")
    
    # 1. Fetch distinct student emails and names from your database tracking ledger
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT email, student_name FROM Lec01_responses WHERE email IS NOT NULL")
        roster = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"❌ Aborting Broadcast: Unable to connect to roster records. {str(e)}")
        return False
        
    if not roster:
        print("⚠️ Broadcast Hold: No active student records found inside the database ledger.")
        return False

    # 2. Instruct the LLM to generate Hermes' official persona introduction message
    system_persona = "You are Hermes, the quick and friendly automated messenger agent for Prof. Sudhir's course. You speak with clarity, utilizing a touch of crisp technical authority."
    user_prompt = (
        f"Compose an introductory message welcoming students to the course '{course_code}'. "
        "Briefly explain the backend players in this system architecture:\n"
        "1. Ornith (The Intent Parse Gateway - interprets your emails and instructions)\n"
        "2. Qwen (The Evaluation Engine - analyzes submissions against grading rubrics)\n"
        "3. Hermes (Your Outbound Courier - brings immediate alerts and reports straight to your inbox)\n\n"
        "Keep the note under 4 concise paragraphs and end with a signature from Agent Hermes."
    )
    
    print("🧠 Requesting persona message compilation from the local LLM engine...")
    welcome_message = query_omlx_llm("Qwen3.6-35B-A3B-4bit", system_persona, user_prompt)
    
    print("\n📝 Generated Persona Message Preview:")
    print("------------------------------------------------------------")
    print(welcome_message)
    print("------------------------------------------------------------\n")
    
    # 3. Step through the active cohort roster array and dispatch emails
    success_count = 0
    for email, name in roster:
        subject_line = f"🎓 Welcome to {course_code} — Message from Agent Hermes"
        personalized_body = f"Hello {name},\n\n{welcome_message}"
        
        # In actual execution, this relays straight out via AgentMail API
        status, msg = send_agentmail_packet(email, subject_line, personalized_body)
        if status:
            success_count += 1
            print(f"   📬 Dispatched introduction packet successfully to: {email}")
        else:
            print(f"   ⚠️ Relay latency detour for {email}: {msg} (Simulated execution logged)")
            
    print(f"\n✨ Broadcast processing complete. Distributed introductory packets to {success_count} student endpoints.")
    return True

if __name__ == "__main__":
    # Test-driving the script locally to evaluate runtime loops
    execute_hermes_broadcast("MTGT", "Lec01")
