import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.security import verify_access

def run_security_test_suite():
    print("🧪 RUNNING INSTRUCTIONAL SECURITY UNIT TESTS...")
    print("------------------------------------------------------------")
    
    pass_admin, reason_admin = verify_access("sudhir_voleti@isb.edu", "eval_responses")
    print(f"🔹 Profile A (Admin Requesting Admin Skill):")
    print(f"   • Expected: True | Result: {pass_admin}")
    print(f"   • Reason: {reason_admin}\n")
    
    pass_stud, reason_stud = verify_access("student_test@isb.edu", "eval_responses")
    print(f"🔹 Profile B (Student Requesting Admin Skill):")
    print(f"   • Expected: False | Result: {pass_stud}")
    print(f"   • Reason: {reason_stud}\n")
    
    print("------------------------------------------------------------")
    print("✨ TEST SUITE EXECUTION CYCLE CONCLUDED.")

if __name__ == "__main__":
    run_security_test_suite()
