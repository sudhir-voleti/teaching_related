import sys
import os
import sqlite3
import json

base_path = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os"
sys.path.append(base_path)
sys.path.append(os.path.join(base_path, "tools"))

import sync_sheets_to_db
import global_utils

DEFAULT_RUBRIC = """
Evaluate marketing intuition and logic consistency. 
Award 4-5 stars for structured frameworks showing clear psychographic insight or choice paralysis handling. 
Award 1-3 stars for vague, generic answers.
"""

def fetch_dynamic_asset(course_id, lec_id, asset_type):
    """Dynamically resolves file names based on lecture parameters."""
    filename = f"{course_id.lower()}_{lec_id.lower()}_{asset_type}.txt"
    asset_path = os.path.join(base_path, "assets", filename)
    if os.path.exists(asset_path):
        with open(asset_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def run_qwen_batch_grading(rows, course_id, lec_id, q_id):
    print(f"🧠 [Qwen Layer] Grading batch of {len(rows)} responses for {q_id.upper()}...")
    payload_items = [{"email": r[0], "response": r[1]} for r in rows]
    
    rubric_text = fetch_dynamic_asset(course_id, lec_id, f"{q_id}_rubric")
    if not rubric_text:
        rubric_text = fetch_dynamic_asset(course_id, lec_id, "rubric")
    if not rubric_text:
        rubric_text = DEFAULT_RUBRIC
    
    system_prompt = """You are an expert marketing professor grading open-ended student quiz responses.
Your output must be a valid, strict JSON array of objects with exactly three keys: "email", "score_stars", and "feedback_text".
The "score_stars" must be an integer from 1 to 5. The "feedback_text" must be a concise, 1-sentence personalized note.
Return ONLY the raw JSON array string. No chat markdown wrappers like ```json."""

    user_prompt = f"### EVALUATION RUBRIC:\n{rubric_text}\n\n### BATCH DATA:\n{json.dumps(payload_items, indent=2)}"
    
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
        print(f"❌ Grading compilation error for {q_id}: {e}")
        return []

def generate_class_report(course_id, lec_id, db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    report = f"==================================================\n"
    report += f"   CLASS METRICS SUMMARY: {course_id.upper()} {lec_id.upper()}\n"
    report += f"==================================================\n\n"
    
    cur.execute("SELECT DISTINCT q_id FROM student_quiz_responses WHERE LOWER(course_id)=LOWER(?) AND LOWER(lec_id)=LOWER(?)", (course_id, lec_id))
    questions = [q[0] for q in cur.fetchall()]
    
    for q_id in sorted(questions):
        cur.execute("SELECT score_stars FROM student_quiz_responses WHERE LOWER(course_id)=LOWER(?) AND LOWER(lec_id)=LOWER(?) AND q_id=? AND score_stars IS NOT NULL", (course_id, lec_id, q_id))
        scores = [s[0] for s in cur.fetchall()]
        
        if scores:
            avg_score = sum(scores) / len(scores)
            report += f"📊 {q_id.upper()} (Open-Ended Text Question):\n"
            report += f"   -> Total Evaluated Submissions: {len(scores)}\n"
            report += f"   -> Class Achievement Average  : {round(avg_score, 2)} / 5.00 Stars\n\n"
        else:
            cur.execute("SELECT response_payload, COUNT(*) FROM student_quiz_responses WHERE LOWER(course_id)=LOWER(?) AND LOWER(lec_id)=LOWER(?) AND q_id=? GROUP BY response_payload", (course_id, lec_id, q_id))
            dist_rows = cur.fetchall()
            total_mcq = sum(d[1] for d in dist_rows)
            report += f"📈 {q_id.upper()} (Multiple Choice Distribution):\n"
            for label, count in dist_rows:
                pct = (count / total_mcq) * 100
                report += f"   -> [Option {label}] {count} responses ({round(pct, 1)}%)\n"
            report += "\n"
            
    conn.close()
    return report

##

def main():
    # Lower bound checked at 2 now because packed args like sys.argv[1] = "MTGT Lec03" leave len(sys.argv) == 2
    if len(sys.argv) < 2:
        print("❌ Operational Halt: Missing parameters.")
        return
        
    # Unbundling Logic: Handle cases where the LLM passes space-clumped args inside a single string element
    if len(sys.argv) == 2 or (len(sys.argv) >= 3 and sys.argv[2].strip() == ""):
        raw_input_string = sys.argv[1].strip()
        parts = raw_input_string.split()
        raw_course = parts[0] if len(parts) > 0 else "MTGT"
        raw_lec = parts[1] if len(parts) > 1 else "Lec03"
    else:
        raw_course = sys.argv[1].strip()
        raw_lec = sys.argv[2].strip()
        
    # Defensive Quote Stripper Implementation
    course_id = raw_course.split("=")[-1].replace('"', '').replace("'", "") if "=" in raw_course else raw_course.replace('"', '').replace("'", "")
    lec_id = raw_lec.split("=")[-1].replace('"', '').replace("'", "") if "=" in raw_lec else raw_lec.replace('"', '').replace("'", "")
    
    print(f"🌙 [BATCH OPERATION] Launching Dynamic Lecture-Wide Macro for {course_id.upper()} {lec_id.upper()}...")
    sync_sheets_to_db.sync_live_responses()
    
    db_path = os.path.join(base_path, "db/course_data.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT q_id FROM student_quiz_responses WHERE LOWER(course_id)=LOWER(?) AND LOWER(lec_id)=LOWER(?) AND score_stars IS NULL", (course_id, lec_id))
    un_graded_questions = [q[0] for q in cur.fetchall()]
    mcq_tags = ['q1', 'q2', 'q3', 'q5']
    text_questions = [q for q in un_graded_questions if q not in mcq_tags]
    
    for q_id in text_questions:
        cur.execute("SELECT student_email, response_payload FROM student_quiz_responses WHERE LOWER(course_id)=LOWER(?) AND LOWER(lec_id)=LOWER(?) AND q_id=? AND score_stars IS NULL", (course_id, lec_id, q_id))
        target_rows = cur.fetchall()
        if not target_rows: continue
        
        evaluations = run_qwen_batch_grading(target_rows, course_id, lec_id, q_id)
        for item in evaluations:
            cur.execute("UPDATE student_quiz_responses SET score_stars = ?, feedback_text = ? WHERE student_email = ? AND LOWER(course_id) = LOWER(?) AND LOWER(lec_id) = LOWER(?) AND q_id = ?", 
                        (item.get("score_stars"), item.get("feedback_text"), item.get("email"), course_id, lec_id, q_id))
            
    conn.commit()
    trend_report = generate_class_report(course_id, lec_id, db_path)
    print(f"\n{trend_report}")
    
    questionnaire_text = fetch_dynamic_asset(course_id, lec_id, "questionnaire")
    if not questionnaire_text:
        questionnaire_text = "Master quiz template text file missing on disk context."
            
    cur.execute("SELECT DISTINCT student_email FROM student_quiz_responses WHERE LOWER(course_id)=LOWER(?) AND LOWER(lec_id)=LOWER(?)", (course_id, lec_id))
    student_emails = [e[0] for e in cur.fetchall()]
    
    print(f"📧 Staging summary package dispatches for {len(student_emails)} profiles...")
    for email in student_emails:
        cur.execute("SELECT q_id, response_payload, score_stars, feedback_text FROM student_quiz_responses WHERE student_email = ? AND LOWER(course_id) = LOWER(?) AND LOWER(lec_id) = LOWER(?)", (email, course_id, lec_id))
        records = cur.fetchall()
        
        student_stream = f"=== YOUR QUIZ SUBMISSION RECORD ===\n"
        for q, resp, stars, feedback in records:
            student_stream += f"\n📌 Question ID: {q.upper()}\n   -> Your Answer Text: \"{resp}\"\n"
            if stars:
                student_stream += f"   -> Grade Awarded   : {stars} / 5 Stars\n   -> Evaluator Note  : {feedback}\n"
            else:
                student_stream += f"   -> Grade Awarded   : Multiple-Choice Logged\n"
                
        final_body = f"Hello Student,\n\nPlease find your consolidated quiz report for Lecture 1 below.\n\n{trend_report}\n{student_stream}\n==================================================\n\n=== APPENDIX: MASTER QUESTIONNAIRE ===\n{questionnaire_text}\n"
        subject = f"Agent OS: Personal Quiz Portfolio Summary ({course_id.upper()} - {lec_id.upper()})"
        global_utils.send_student_email_with_attachment(to_email=email, subject=subject, body_text=final_body, attachment_file=None)
        
    conn.close()
    print("🎉 Dynamic batch execution complete!")
#

if __name__ == "__main__":
    main()