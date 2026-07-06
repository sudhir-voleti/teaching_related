import sqlite3

DB_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/db/MTGT1-ledger.db"

def execute_query(sql_command, params=()):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_command, params)
            if sql_command.strip().upper().startswith("SELECT"):
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                return {"status": "success", "data": [dict(zip(columns, row)) for row in rows]}
            conn.commit()
            return {"status": "success", "rows_affected": cursor.rowcount}
    except Exception as e:
        return {"error": str(e)}
