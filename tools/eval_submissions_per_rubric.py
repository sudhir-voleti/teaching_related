import os
import sys
import json
import sqlite3
import urllib.request

def call_local_inference(model_name, system_prompt, user_prompt):
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=90) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            return json.loads(res_json['choices'][0]['message']['content'])
    except Exception as e:
        print(f"⚠️ Inference chunk failure exception: {str(e)}")
        return {"evaluation_matrix": []}

def run_batch_evaluation(lecture_table, rubric_path, batch_size=10):
    db_path = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/db/course_data.db"
    
    if not os.path.exists(rubric_path):
        return {"status": "error", "message": f"Rubric asset not found at {rubric_path}"}
        
    with open(rubric_path, "r") as f:
        rubric_data = f.read()
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Gather all pending submissions
        cursor.execute(f"SELECT email, student_name, q_id, q_response FROM {lecture_table} WHERE status = 'SUBMITTED'")
        submissions = cursor.fetchall()
        
        if not submissions:
            return {"status": "success", "message": "No pending submissions found requiring grading."}
            
        print(f"🧬 [Batch Processing Active] Found {len(submissions)} records. Chunk Allocation Size: {batch_size}")
        
        system_prompt = """You are an elite quantitative marketing professor. You will be given an evaluation rubric and a block list of multiple student quiz submissions.
Evaluate every student independently based on the rules. 
You MUST output your response as a single valid JSON object containing an array named "evaluation_matrix" where each element maps back to the student's email:
{
  "evaluation_matrix": [
    {
      "email": "student@isb.edu",
      "star_rating": 4.5,
      "feedback_comment": "Excellent data framing and parameter estimation reasoning."
    }
  ]
}"""

        # 2. Divide the total array into parameterized chunks
        for i in range(0, len(submissions), batch_size):
            chunk = submissions[i:i + batch_size]
            print(f"📦 Shipping chunk block row indices {i} to {i + len(chunk)} straight to Qwen...")
            
            # Formulate the multi-student data sub-packet
            batch_list = []
            for email, name, q_id, response in chunk:
                batch_list.append({
                    "email": email,
                    "student_name": name,
                    "question_id": q_id,
                    "submission_text": response
                })
                
            user_prompt = f"CRITICAL EVALUATION RUBRIC CRITERIA:\n{rubric_data}\n\nPENDING COHORT SUBMISSIONS LIST:\n{json.dumps(batch_list, indent=2)}"
            
            # Execute the single consolidated model pass
            chunk_results = call_local_inference(
                model_name="Qwen3.6-27B-5bit",
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            # 3. Stream data updates back into the SQLite transaction space
            matrix = chunk_results.get("evaluation_matrix", [])
            for record in matrix:
                s_email = record.get("email")
                score = record.get("star_rating", 3.0)
                feedback = record.get("feedback_comment", "Graded via batch runtime configuration pipeline.")
                
                cursor.execute(f"""
                    UPDATE {lecture_table}
                    SET star_rating = ?, feedback_comment = ?, status = 'GRADED'
                    WHERE email = ?
                """, (score, feedback, s_email))
                
            conn.commit()
            print(f"✅ Successfully written and saved {len(matrix)} student updates to SQLite system layers.")
            
        return {"status": "success", "message": f"Successfully completed all batch chunks against {lecture_table}."}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    # Test stub verification entry point
    res = run_batch_evaluation("Lec02_responses", "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/assets/templates/case_analysis_rubric.json", batch_size=10)
    print(json.dumps(res, indent=2))
