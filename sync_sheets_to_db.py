import os
import sqlite3
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

DB_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/db/course_data.db"
CREDS_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/tools/google_creds.json"
SHEET_NAME = "MTGT1_Lec01_Responses"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def sync_live_responses():
    print("⏳ Initializing local synchronization hook...")
    if not os.path.exists(CREDS_PATH):
        print(f"❌ Error: Local credentials file missing at {CREDS_PATH}")
        return

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        all_rows = sheet.get_all_values()
        print(f"📡 Successfully downloaded {len(all_rows)} data entries from Google Drive.")
    except Exception as e:
        print(f"❌ Google API Sync Stalled: {e}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    new_records_count = 0
    
    for row in all_rows:
        if not row or len(row) < 5:
            continue
            
        course_id = row[0].strip().upper()
        lec_id = row[1].strip()
        q_id = row[2].strip().lower()
        student_email = row[3].strip().lower()
        response_payload = row[4].strip()
        
        if course_id == "COURSE_ID" or "@" not in student_email:
            continue

        try:
            cursor.execute("""
                INSERT OR IGNORE INTO student_quiz_responses 
                (course_id, lec_id, q_id, student_email, response_payload)
                VALUES (?, ?, ?, ?, ?)
            """, (course_id, lec_id, q_id, student_email, response_payload))
            if cursor.rowcount > 0:
                new_records_count += 1
        except Exception as sqlite_err:
            print(f"⚠️ Insertion anomaly for user {student_email}: {sqlite_err}")

    conn.commit()
    conn.close()
    print(f"✅ Ingestion Complete. {new_records_count} brand-new response lines successfully locked to SQLite.")

if __name__ == "__main__":
    sync_live_responses()
