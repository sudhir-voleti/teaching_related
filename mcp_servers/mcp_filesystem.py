import os
import shutil

BASE_DIR = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1"

def list_directory(subfolder=""):
    target = os.path.normpath(os.path.join(BASE_DIR, subfolder.strip("/")))
    if not target.startswith(BASE_DIR):
        return {"error": "Security Exception: Out of bounds."}
    try:
        return {"files": os.listdir(target)}
    except Exception as e:
        return {"error": str(e)}

def create_directory(subfolder, name):
    target = os.path.normpath(os.path.join(BASE_DIR, subfolder.strip("/"), name.strip("/")))
    if not target.startswith(BASE_DIR):
        return {"error": "Security Exception: Out of bounds."}
    try:
        os.makedirs(target, exist_ok=True)
        return {"status": "success", "message": f"Created directory at {target}"}
    except Exception as e:
        return {"error": str(e)}
