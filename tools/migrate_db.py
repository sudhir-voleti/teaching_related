import sqlite3

DB_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/db/MTGT1-ledger.db"

def force_migrate_schema():
    print("🔧 [Database Migration] Aligning ledger schema layout...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Safely drop the existing prototype table to clear the column mismatch constraint
    cursor.execute("DROP TABLE IF EXISTS Lec01_responses")
    
    # Re-build the table architecture with explicit column definitions
    cursor.execute("""
        CREATE TABLE Lec01_responses (
            timestamp TEXT,
            email TEXT PRIMARY KEY,
            student_name TEXT,
            q_id TEXT,
            q_response TEXT,
            q_type TEXT,
            course_code TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Schema alignment successful. Table structures are locked in.")

if __name__ == "__main__":
    force_migrate_schema()
