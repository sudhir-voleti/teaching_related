import sys
import os

base_path = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os"
sys.path.append(base_path)
sys.path.append(os.path.join(base_path, "tools"))

import sync_sheets_to_db
import global_utils

def main():
    if len(sys.argv) < 4:
        print("❌ Error: Missing parameters.")
        return
        
    course_id = sys.argv[1].strip()
    lec_id = sys.argv[2].strip()
    q_id = sys.argv[3].strip()
    email = sys.argv[4].strip() if len(sys.argv) >= 5 else "sudhir.voleti@gmail.com"
    
    print(f"⚡ Executing MCQ Pipeline: {course_id.upper()} {lec_id.upper()} {q_id.upper()}...")
    
    sync_sheets_to_db.sync_live_responses()
    global_utils.generate_mcq_distribution(course_id, lec_id, q_id)
    global_utils.email_mcq_analysis_report(course_id, lec_id, q_id, email)
    print("🎉 Process complete")

if __name__ == "__main__":
    main()
