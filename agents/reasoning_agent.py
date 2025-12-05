# agents/reasoning_agent.py

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def reasoning_analysis(title, company, description, skills):
    prompt = f"""
You are a Job Reasoning Expert AI.

Generate a deep reasoning-based evaluation for:

Follow EXACTLY this structure:

🧩 Root Cause Breakdown
- Show 3–5 root causes why user matches or does not match.

📌 Key Observations
- Show 3 observations about role & user skills.

⚙️ Priority Skill Gaps
- List important missing skills sorted by importance.

🧠 Final Reasoned Conclusion
- ONE short paragraph with a final verdict.

Give only the report.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
