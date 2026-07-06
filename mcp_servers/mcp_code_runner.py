import subprocess
import sys

def run_python_expression(code_string):
    """Safely evaluates or runs code blocks for calculations/Excel data parsing."""
    try:
        # Runs the script in a clean sub-shell process to prevent main server crashes
        result = subprocess.run(
            [sys.executable, "-c", code_string],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout.strip()}
        return {"status": "failed", "error": result.stderr.strip()}
    except Exception as e:
        return {"error": str(e)}
