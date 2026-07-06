import json
import sqlite3

PERMISSIONS_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/config/student_permissions.json"
DB_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/db/MTGT1-ledger.db"

def verify_access(sender_email, requested_skill):
    """
    Validates identity and enforces Role-Based Access Control (RBAC).
    Returns: (bool_is_allowed, string_reason)
    """
    try:
        with open(PERMISSIONS_PATH, 'r') as f:
            perms = json.load(f)
    except Exception as e:
        return False, f"System Configuration Error: Unable to read permissions map. {str(e)}"
        
    if sender_email in perms["roles"]["admins"]:
        return True, "Admin verification success. Full execution clearance granted."
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Lec01_responses WHERE email = ?", (sender_email,))
        is_registered = cursor.fetchone()[0] > 0
        conn.close()
    except Exception as e:
        return False, f"Database Verification Interrupted: {str(e)}"
        
    if not is_registered:
        return False, f"Access Denied: Senders signature ({sender_email}) is missing from the course ledger roster."
        
    allowed_student_skills = perms["permissions"]["student_accessible_skills"]
    if requested_skill in allowed_student_skills:
        return True, f"Student verification success. Skill '{requested_skill}' is authorized for execution."
    elif requested_skill in perms["permissions"]["admin_only_skills"]:
        return False, f"Access Denied: Action '{requested_skill}' requires administrative clearance privileges."
    else:
        return False, f"Unknown Capability: Action '{requested_skill}' is not a registered tool in the store."

if __name__ == "__main__":
    print("📋 Testing Security Access Controller...")
    print(verify_access("sudhir_voleti@isb.edu", "eval_responses"))
