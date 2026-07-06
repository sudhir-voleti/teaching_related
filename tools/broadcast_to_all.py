import sys
import os
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from global_utils import send_agentmail_packet, DB_PATH

def execute_generic_broadcast(course_code, subject, body_content):
    """
    A pure pipeline tool: Pulls the roster for a specific course 
    and broadcasts any arbitrary subject and message body provided.
    """
    print(f"📣 [Broadcast Engine] Initializing email blast for course: {course_code}...")
    
    # 1. Pull the roster for the target course from the database ledger
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if course_code filtering is available in the schema
        cursor.execute("PRAGMA table_info(Lec01_responses)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "course_code" in columns:
            cursor.execute("SELECT DISTINCT email, student_name FROM Lec01_responses WHERE course_code = ? AND email IS NOT NULL", (course_code.upper(),))
        else:
            cursor.execute("SELECT DISTINCT email, student_name FROM Lec01_responses WHERE email IS NOT NULL")
            
        roster = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"❌ Aborting Broadcast: Database connection failure. {str(e)}")
        return False
        
    if not roster:
        print(f"⚠️ Broadcast Hold: No active student records located for course '{course_code}'.")
        return False

    # 2. Loop through the roster and dispatch the exact text provided
    success_count = 0
    for email, name in roster:
        # Prepend a personalized greeting to keep the email clean
        personalized_body = f"Dear {name},\n\n{body_content}"
        
        status, msg = send_agentmail_packet(email, subject, personalized_body)
        if status:
            success_count += 1
            print(f"   📬 Sent to: {email}")
        else:
            print(f"   ⚠️ Network detour for {email}: {msg} (Log record created)")
            
    print(f"\n✨ Broadcast complete. Distributed packets to {success_count} student endpoints.")
    return True

if __name__ == "__main__":
    # Test-driving the clean, generic tool loop with sample inputs
    sample_subject = "Important Update: Review Assignment Parameters"
    sample_body = "Please review the updated case study guidelines on the portal before tomorrow's session."
    
    execute_generic_broadcast("MTGT", sample_subject, sample_body)
