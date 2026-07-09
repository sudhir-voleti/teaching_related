import unittest
import os
import json
import sqlite3
from tools.global_utils import (
    query_course_ledger, list_available_assets, generate_lecture_summary,
    send_personalized_bulk, email_inventory_manifest
)

class TestMarketingAgentOS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Seed data into the ledger DB that query_course_ledger actually uses."""
        cls.db_path = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/db/MTGT1-ledger.db"
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS test_responses (
            email TEXT PRIMARY KEY,
            student_name TEXT,
            q_id TEXT,
            status TEXT
        )''')
        
        cursor.execute("DELETE FROM test_responses")
        
        test_students = [
            ("sudhir.voleti@gmail.com", "Sudhir Voleti", "q1", "SUBMITTED"),
            ("archanadilpali@gmail.com", "Archana Dilpali", "q1", "GRADED"),
            ("profsudhirvoleti@gmail.com", "Prof Test", "q2", "SUBMITTED")
        ]
        cursor.executemany("INSERT OR REPLACE INTO test_responses VALUES (?,?,?,?)", test_students)
        conn.commit()
        conn.close()
        print(f"✅ Synthetic data seeded into {cls.db_path}")

    def test_query_ledger(self):
        result = query_course_ledger("SELECT COUNT(*) as cnt FROM test_responses")
        print("Query result:", result[:200])
        self.assertIn("cnt", result)

    def test_list_assets(self):
        result = list_available_assets("")
        data = json.loads(result)
        self.assertIsInstance(data, list)

    def test_generate_summary(self):
        summary = generate_lecture_summary("test_responses")
        print("Summary result:", summary[:300])
        self.assertIn("total", summary.lower())

    def test_personalized_bulk_dryrun(self):
        result = send_personalized_bulk(
            "test_responses",
            "Test Subject for {{name}}",
            "Hello {{name}}, this is a unit test.",
            None
        )
        self.assertIn("dispatched", result.lower())

    def test_inventory_manifest(self):
        result = email_inventory_manifest("sudhir.voleti@gmail.com")
        self.assertIn("Success", result)

if __name__ == '__main__':
    unittest.main(verbosity=2)
