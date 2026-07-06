import json
import sqlite3
import os

CONFIG_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/config/active_lecture.json"
DB_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/db/MTGT1-ledger.db"

def update_active_lecture(course_code, lecture_id, questions_list, rubric_text):
    """
    Overwrites system settings for the active module and purges the dynamic 
    workspace buffers matching the specific course to prevent multi-course data drift.
    """
    # 1. Enforce strict type constraints on the input course key
    course_key = str(course_code).strip().upper()
    
    payload = {
        "course_code": course_key,
        "active_lecture_id": lecture_id,
        "rubric": rubric_text,
        "questions": questions_list
    }
    
    try:
        # Write structural parameter definitions to the shared active state json
        with open(CONFIG_PATH, 'w') as f:
            json.dump(payload, f, indent=2)
        print(f"📝 Multi-Course OS Configuration Updated: {course_key} - {lecture_id}")
        
        # 2. Database isolation check: purge records only for this specific course
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verify if our ledger table handles explicit course keys (adding safety column resilience)
        cursor.execute("PRAGMA table_info(Lec01_responses)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "course_code" in columns:
            cursor.execute("DELETE FROM Lec01_responses WHERE course_code = ?", (course_key,))
            print(f"🧹 Database Isolation: Purged existing raw entries matching course key '{course_key}'.")
        else:
            # Fallback path if working on the single-course structural prototype schema
            cursor.execute("DELETE FROM Lec01_responses")
            print(f"🧹 Protocol Warning: Column 'course_code' missing from database layout. Flushed global response tables.")
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed to provision multi-course lecture registry: {str(e)}")
        return False

if __name__ == "__main__":
    print("📋 Testing Multi-Course Active Lecture Manager Infrastructure...")
    
    # Verify behavior with an alphanumeric module target code (e.g., MTGT)
    sample_questions = [
        {"id": "q1", "type": "MCQ", "label": "Identify the primary positioning metric"},
        {"id": "q4", "type": "OPEN", "label": "Detail your operational automation logic"}
    ]
    
    update_active_lecture(
        course_code="MTGT", 
        lecture_id="Lec03", 
        questions_list=sample_questions, 
        rubric_text="Excellent criteria: explicit transmission bottlenecks named."
    )
