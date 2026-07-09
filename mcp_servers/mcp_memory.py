import sqlite3
import os
import json

DB_PATH = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/db/agent_memory.db"

def init_memory_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create entities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            name TEXT PRIMARY KEY,
            type TEXT,
            description TEXT
        )
    """)
    # Create relationships table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relations (
            source TEXT,
            predicate TEXT,
            target TEXT,
            PRIMARY KEY (source, predicate, target)
        )
    """)
    conn.commit()
    conn.close()

def add_relation(source, predicate, target):
    init_memory_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Seed placeholder entities if they don't exist yet
        cursor.execute("INSERT OR IGNORE INTO entities (name, type) VALUES (?, ?)", (source, "unknown"))
        cursor.execute("INSERT OR IGNORE INTO entities (name, type) VALUES (?, ?)", (target, "unknown"))
        # Insert relation link
        cursor.execute("INSERT OR REPLACE INTO relations VALUES (?, ?, ?)", (source, predicate, target))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Linked: {source} -> {predicate} -> {target}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def query_memory(entity_name):
    init_memory_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT predicate, target FROM relations WHERE source = ?", (entity_name,))
        forward = [f"-[{row[0]}]-> {row[1]}" for row in cursor.fetchall()]
        cursor.execute("SELECT source, predicate FROM relations WHERE target = ?", (entity_name,))
        backward = [f"<-[{row[1]}]- {row[0]}" for row in cursor.fetchall()]
        conn.close()
        return {"status": "success", "entity": entity_name, "connections": forward + backward}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Self-contained instantiation test
    init_memory_db()
    add_relation("Arvind", "collaborates_with", "Prof_Voleti")
    add_relation("Lec02", "utilizes_distribution", "Tweedie")
    print(json.dumps(query_memory("Lec02")))
