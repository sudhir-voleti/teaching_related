import sys
import os
import sqlite3
import json
from collections import Counter

base_path = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os"
sys.path.append(base_path)
sys.path.append(os.path.join(base_path, "tools"))

import sync_sheets_to_db
import global_utils

RUBRIC = """
A top-tier answer (4-5 stars) must correctly identify structural Go-To-Market (GTM) strategy gaps,
specifically calling out psychographic/behavioral customer misalignments or choice paralysis in conversion loops.
Lower-tier answers (1-3 stars) mention broad budget/marketing execution elements without linking back to core consumer needs.
"""

def extract_top_bigrams(text_list, top_n=5):
    bigrams = []
    stopwords = {'the', 'a', 'is', 'and', 'to', 'in', 'of', 'for', 'on', 'with', 'at', 'by', 'an', 'are', 'it', 'too', 'this', 'that', 'they', 'our', 'we', 'i'}
    for text in text_list:
        cleaned_text = text.replace('.', '').replace(',', '').replace('!', '').replace('?', '').replace(';', '')
        words = [w.lower() for w in cleaned_text.split()]
        words = [w for w in words if w and w not in stopwords]
        for i in range(len(words) - 1):
            bigrams.append(f"{words[i]} {words[i+1]}")
    return Counter(bigrams).most_common(top_n)

def run_batch_grading(rows, course_id, lec_id, q_id):
    print("🧠 Initiating Off-Duty Batch LLM Evaluation via Qwen...")
    payload_items = []
    for email, response in rows:
        payload_items.append({"email": email, "response": response})
        
    system_prompt = """You are an expert marketing professor grading open-ended student quiz responses.
Your entire output must be a valid, strict JSON array of objects with exactly three keys: "email", "score_stars", and "feedback_text".
Do not add markdown wrappers like ```json or any chat conversational text. Return ONLY the raw JSON array string."""

    user_prompt = f"### EVALUATION RUBRIC:\n{RUBRIC}\n\n### BATCH DATA TO EVALUATE:\n{json.dumps(payload_items, indent=2)}"
    
    try:
        from global_utils import query_omlx_llm
        raw_output = query_omlx_llm(
            model_name="Qwen3.6-35B-A3B-4bit",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0
        ).strip()
        
        if "```" in raw_output:
            raw_output = raw_output.split("```")[1].replace("json", "").strip()
            
        return json.loads(raw_output.strip())
    except Exception as e:
        print(f"❌ Batch evaluation pipeline failed: {e}")
        return []

def main():
    if len(sys.argv) < 4:
        print("❌ Error: Missing parameters.")
        return
        
    course_id = sys.argv[1].strip()
    lec_id = sys.argv[2].strip()
    q_id = sys.argv[3].strip()
    mode = sys.argv[4].strip().lower() if len(sys.argv) >= 5 else "live"
    professor_email = "sudhir.voleti@gmail.com"
    
    db_path = os.path.join(base_path, "db/course_data.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    if mode == "live":
        print(f"⚡ [LIVE MODE] Running High-Speed Class Aggregator for {course_id.upper()} {lec_id.upper()}...")
        sync_sheets_to_db.sync_live_responses()
        
        cur.execute("SELECT student_email, response_payload FROM student_quiz_responses WHERE LOWER(course_id)=LOWER(?) AND LOWER(lec_id)=LOWER(?) AND LOWER(q_id)=LOWER(?)", (course_id, lec_id, q_id))
        rows = cur.fetchall()
        
        if not rows:
            print("⚠️ No student responses found.")
            conn.close()
            return
            
        payloads = [r[1] for r in rows]
        top_phrases = extract_top_bigrams(payloads, top_n=5)
        
        report_msg = f"=== {course_id.upper()} {lec_id.upper()} {q_id.upper()} LIVE TOPIC ANALYSIS ===\nSubmissions: {len(payloads)}\n\n"
        for phrase, count in top_phrases:
            report_msg += f"- {phrase.ljust(30)} : {count} mentions\n"
            
        print(report_msg)
        global_utils.send_student_email_with_attachment(to_email=professor_email, subject=f"Live Themes: {q_id.upper()}", body_text=report_msg, attachment_file=None)
        print("🚀 Near-zero latency execution complete. Heavy grading skipped for off-duty hours.")
        
    elif mode == "batch":
        print(f"🌙 [BATCH MODE] Initiating Post-Class Grading Sequence...")
        # Select rows where score_stars hasn't been set yet
        cur.execute("SELECT student_email, response_payload FROM student_quiz_responses WHERE LOWER(course_id)=LOWER(?) AND LOWER(lec_id)=LOWER(?) AND LOWER(q_id)=LOWER(?) AND score_stars IS NULL", (course_id, lec_id, q_id))
        rows = cur.fetchall()
        
        if not rows:
            print("✅ All entries are already graded and logged.")
            conn.close()
            return
            
        evaluations = run_batch_grading(rows, course_id, lec_id, q_id)
        if evaluations:
            success_count = 0
            for item in evaluations:
                cur.execute("UPDATE student_quiz_responses SET score_stars = ?, feedback_text = ? WHERE student_email = ? AND LOWER(course_id) = LOWER(?) AND LOWER(lec_id) = LOWER(?) AND LOWER(q_id) = LOWER(?)", 
                            (item.get("score_stars"), item.get("feedback_text"), item.get("email"), course_id, lec_id, q_id))
                if cur.rowcount > 0: success_count += 1
            conn.commit()
            print(f"💾 Background Ledger Updated: {success_count} records scored.")
            
    conn.close()
    print("🎉 Processing loop complete.")

if __name__ == "__main__":
    main()