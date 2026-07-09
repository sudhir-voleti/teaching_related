import re

with open("/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/gateway/gateway_daemon.py", "r") as f:
    content = f.read()

old_parse = """    clean_json = response_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean_json)
    except Exception:
        return {"final_response": f"Parsing glitch on response agent packet: {response_text}"}"""

new_parse = """    # Robust extraction: isolate the outer JSON boundaries if reasoning tokens bleed over
    clean_json = response_text.replace("```json", "").replace("```", "").strip()
    if "</think>" in clean_json:
        clean_json = clean_json.split("</think>")[-1].strip()
    
    match = re.search(r"({.*})", clean_json, re.DOTALL)
    if match:
        clean_json = match.group(1)
        
    try:
        return json.loads(clean_json)
    except Exception:
        return {"final_response": f"Parsing glitch on response agent packet: {response_text}"}"""

if old_parse in content:
    content = content.replace(old_parse, new_parse)
    if "import re" not in content:
        content = "import re\n" + content
    with open("/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/gateway/gateway_daemon.py", "w") as f:
        f.write(content)
    print("✅ Gateway parser robustly patched against trailing reasoning tokens.")
else:
    print("⚠️ Targets misaligned. Manual overwrite required.")
