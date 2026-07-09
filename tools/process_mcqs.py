import os
import sys
import json
import sqlite3
import matplotlib.pyplot as plt
import urllib.request

def call_local_summary(model_name, counts_data, correct_answers, token_str):
    url = "http://localhost:8000/v1/chat/completions"
    system_prompt = "You are a marketing research analyst providing a brief 2-sentence pedagogical insight based on student quiz selection frequencies."
    user_prompt = f"Correct Answer Key Set: {correct_answers}. Option distribution counts: {json.dumps(counts_data)}. Give a swift overview of where the cohort converged or tripped up."
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'))
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {token_str}")
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode('utf-8'))
            return res['choices'][0]['message']['content']
    except Exception as e:
        return f"Analytics summary extraction bypass: {str(e)}"

def parse_options_set(input_string):
    clean = str(input_string).replace("|", ",").replace(";", ",")
    return set(opt.strip().upper() for opt in clean.split(",") if opt.strip())

def analyze_and_chart_mcq(lecture_table, q_id, correct_answer_key, token_str="omlx-local"):
    db_path = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/db/course_data.db"
    chart_output = f"/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/assets/{lecture_table}_{q_id}_distribution.png"
    
    true_set = parse_options_set(correct_answer_key)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT email, q_response FROM {lecture_table} WHERE q_id = ?", (q_id,))
        all_rows = cursor.fetchall()
        
        if not all_rows:
            return {"status": "error", "message": f"No student response records found for {q_id} inside {lecture_table}."}
            
        distribution = {}
        for email, response in all_rows:
            student_set = parse_options_set(response)
            for opt in student_set:
                distribution[opt] = distribution.get(opt, 0) + 1
                
            intersection_size = len(student_set.intersection(true_set))
            union_size = len(student_set.union(true_set))
            
            if union_size > 0:
                jaccard_index = intersection_size / union_size
                score = round(1.0 + (4.0 * jaccard_index), 2)
            else:
                score = 1.0
                
            feedback = f"MMCQ Evaluation: Options Selected: {sorted(list(student_set))}. Correct Key Matrix: {sorted(list(true_set))}."
            cursor.execute(f"UPDATE {lecture_table} SET star_rating = ?, feedback_comment = ?, status = 'GRADED' WHERE email = ? AND q_id = ?", (score, feedback, email, q_id))
            
        conn.commit()

        plt.figure(figsize=(6, 4))
        options = sorted(list(distribution.keys()))
        counts = [distribution[opt] for opt in options]
        colors = ['#2ecc71' if opt in true_set else '#e74c3c' for opt in options]
        
        plt.bar(options, counts, color=colors, edgecolor='#34495e', linewidth=1.2)
        plt.title(f"Class Response Distribution Profile ({lecture_table} - {q_id})", fontsize=12, fontweight='bold', pad=15)
        plt.xlabel("Selected Option Flags", fontsize=10, labelpad=10)
        plt.ylabel("Student Selection Frequency", fontsize=10, labelpad=10)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(chart_output, dpi=150)
        plt.close()

        insight = call_local_summary("Qwen3.6-27B-5bit", distribution, sorted(list(true_set)), token_str)

        return {
            "status": "success",
            "message": f"Successfully graded multi-choice profiles across {len(all_rows)} student entries.",
            "chart_path": chart_output,
            "distribution_summary": distribution,
            "ai_pedagogical_insight": insight
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()
