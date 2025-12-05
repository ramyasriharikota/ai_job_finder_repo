# agents/career_predict_agent.py

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def career_prediction(title, company, skills):
    prompt = f"""
You are a Career Path Predictor AI.

Generate a future projection report for this user:

Role: {title}
Company: {company}
User Skills: {skills}

Follow EXACTLY this structure:

📈 1. Career Growth Path (2025 → 2030)
Show realistic promotions and job titles year-by-year.

💸 2. Salary Projection
Show estimated salary growth:
- Current
- 1-year
- 3-year
- 5-year

📊 3. Market Demand Forecast
Explain demand for this role in next 5 years (High/Medium/Low).

💡 4. Best Career Direction
Suggest the BEST path based on their skill profile.

🪜 5. Steps to Reach Next Level
Provide a short, actionable checklist.

Give only the report.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
