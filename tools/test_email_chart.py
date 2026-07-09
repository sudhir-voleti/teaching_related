import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.send_email import execute_send_email

def test_chart_delivery():
    target_chart = "/Users/sudhirvoleti/teaching_trials/courses/MTGT1/marketing-agent-os/assets/Lec02_responses_q1_distribution.png"
    recipient = "sudhir.voleti@gmail.com"
    
    html_layout = """
    <html>
      <body style="font-family: Arial, sans-serif; color: #2c3e50; line-height: 1.6;">
        <h2 style="color: #1b5e20; border-bottom: 2px solid #c8e6c9; padding-bottom: 8px;">
          📊 MTGT1 Core MCQ Analytics Dashboard
        </h2>
        <p>Professor Voleti,</p>
        <p>The analytics pipeline has successfully generated the class distribution graph for your lecture files.</p>
        
        <div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 12px; margin: 15px 0; border-radius: 4px;">
          <strong>📈 Visual Asset Included:</strong> The distribution plot has been compiled and attached directly to this message as a high-resolution PNG file. You can drag it straight into your class slide deck.
        </div>
        
        <p style="font-size: 0.85em; color: #95a5a6; margin-top: 25px;">🤖 Transmitted autonomously via the local Agent OS pipeline.</p>
      </body>
    </html>
    """
    
    res = execute_send_email(
        recipients=[recipient],
        subject="📊 Verification Unit Test: MCQ Distribution Plot Attached",
        body_content="The class distribution plot asset has been successfully compiled and attached.",
        html_content=html_layout,
        image_path=target_chart
    )
    print(f"\n🏁 Verification Matrix Complete: {res}")

if __name__ == "__main__":
    test_chart_delivery()
