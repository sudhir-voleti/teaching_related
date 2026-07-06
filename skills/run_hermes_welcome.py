import sys
import os
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.global_utils import query_omlx_llm, DB_PATH
from tools.broadcast_to_all import execute_generic_broadcast

def setup_test_roster_db():
    """Seeds your 4 personal test accounts into the active database workspace table."""
    print("🗄️  Seeding local SQLite database table with the 4 test roster profiles...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure the target table exists with a robust schema layout
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Lec01_responses (
            timestamp TEXT,
            email TEXT PRIMARY KEY,
            student_name TEXT,
            q_id TEXT,
            q_response TEXT,
            q_type TEXT,
            course_code TEXT
        )
    """)
    
    # Clean old records from previous simulation tests to avoid duplicate key violations
    cursor.execute("DELETE FROM Lec01_responses")
    
    test_roster = [
        ("16:00:00", "sudhir_voleti@isb.edu", "Prof. Sudhir Voleti (ISB)", "roster", "active", "SYSTEM", "MTGT"),
        ("16:00:00", "sudhir.voleti@gmail.com", "Sudhir Voleti (Gmail)", "roster", "active", "SYSTEM", "MTGT"),
        ("16:00:00", "profsudhirvoleti@gmail.com", "Professor Sudhir (Gmail)", "roster", "active", "SYSTEM", "MTGT"),
        ("16:00:00", "archanadilpali@gmail.com", "Archana Dilpali", "roster", "active", "SYSTEM", "MTGT")
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO Lec01_responses 
        (timestamp, email, student_name, q_id, q_response, q_type, course_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, test_roster)
    
    conn.commit()
    conn.close()
    print("✅ Local sandbox database roster verification completed.")

def orchestrate_welcome_skill(course_code):
    """
    Skill Orchestrator: Combines LLM text generation with structural broadcast 
    to dispatch a personalized architecture tour straight to the active roster.
    """
    print(f"\n🧠 [Skill: run_hermes_welcome] Instructing Qwen to compose the personalized introductory body text...")
    
    system_prompt = (
        "You are Hermes, the quick, articulate automated messenger agent for Prof. Sudhir's course. "
        "You speak with professional warmth, exceptional clarity, and a touch of crisp modern technical confidence."
    )
    
    user_request = (
        f"Compose a friendly, high-impact welcome message introducing students to the '{course_code}' framework. "
        "Explicitly detail the main actors working behind the scenes in our M1 agentic setup:\n"
        "1. Ornith-9B (The Intent Parse Gateway - watches our inbox, breaks down instructions, and routes user demands)\n"
        "2. Qwen (The Evaluation Engine - reads milestones, parses student arguments, and processes grading criteria)\n"
        "3. Hermes (Your Outbound Courier - coordinates rapid status updates, alerts, and report card deliveries)\n"
        "4. Terminal (The local Mac Studio server engine execution layer where these elements interact live)\n\n"
        "Note: Do NOT include generic placeholder greetings like 'Dear Student Name' or 'Hello [Name]'. "
        "Start your response directly with the first paragraph text. Keep it under 4 paragraphs, and close with a signature from Agent Hermes."
    )
    
    # Query Qwen locally via the shared utilities block
    welcome_text_payload = query_omlx_llm("Qwen3.6-35B-A3B-4bit", system_prompt, user_request)
    
    print("\n📝 [Review Screen] Displaying generated text package from Qwen:")
    print("=" * 70)
    print(welcome_text_payload)
    print("=" * 70)
    
    # Feed the smart composition payload straight into our clean, generic tool pipe
    subject_line = f"🎓 Welcome to {course_code} — A Message from Agent Hermes"
    execute_generic_broadcast(course_code, subject_line, welcome_text_payload)

if __name__ == "__main__":
    setup_test_roster_db()
    orchestrate_welcome_skill("MTGT")
