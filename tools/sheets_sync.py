import urllib.request
import csv
import sqlite3
import io

DB_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/db/MTGT1-ledger.db"

def sync_cloud_buffer_to_ledger(sheet_csv_url):
    """
    Fetches raw milestone rows from the Google Sheet CSV endpoint
    and synchronizes them into the local SQLite schema.
    """
    print("⏰ [Sync Pulse] Connecting to cloud spreadsheet buffer...")
    try:
        req = urllib.request.Request(
            sheet_csv_url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            csv_content = response.read().decode('utf-8')
            
        # Parse the cloud spreadsheet data strings safely
        csv_file = io.StringIO(csv_content)
        reader = csv.reader(csv_file)
        header = next(reader) # Extract column labels row
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        new_rows_counter = 0
        for row in reader:
            if not row or len(row) < 5:
                continue
                
            # Expected schema structure mapping: 
            # timestamp, email, name, question_id, response_text, question_type
            timestamp, email, name, q_id, q_response, q_type = row[0], row[1], row[2], row[3], row[4], row[5]
            
            # Idempotent write step: insert record only if it doesn't already exist
            cursor.execute("""
                INSERT OR IGNORE INTO Lec01_responses 
                (timestamp, email, student_name, q_id, q_response, q_type) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, email.strip(), name.strip(), q_id.strip(), q_response.strip(), q_type.strip()))
            
            if cursor.rowcount > 0:
                new_rows_counter += 1
                
        conn.commit()
        conn.close()
        print(f"✅ [Sync Pulse] Synchronization complete. Ingested {new_rows_counter} brand-new structured records.")
        return True, new_rows_counter
        
    except Exception as e:
        print(f"⚠️ Sync Interrupted: {str(e)}")
        return False, str(e)

if __name__ == "__main__":
    print("📊 Testing Sheet Synchronization Module Architecture...")
    # Structural mock URL endpoint for testing harness validation
    mock_url = "https://docs.google.com/spreadsheets/d/1_mock_id/export?format=csv"
    print(f"Module initialized. Target configuration URL registered.")
