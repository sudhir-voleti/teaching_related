import sys
sys.path.append("/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os")
from sync_sheets_to_db import sync_live_responses

if __name__ == "__main__":
    print("🚀 TRIGGERING SINGLE BULK CLASSROOM SYNCHRONIZATION...")
    sync_live_responses()
    print("✅ Bulk synchronization loop completed. Sync engine closed.")
