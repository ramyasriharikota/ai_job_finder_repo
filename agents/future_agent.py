# agents/future_agent.py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def future_skill_report(title, company, location, user_skills):

    prompt = f"""
You are an expert Future Skills & Career Coach AI.

Generate a powerful, future-ready skill analysis for:

Role: {title}
Company: {company}
User Skills: {user_skills}

Follow EXACTLY this structure:

🔮 FUTURE SKILL & CAREER FIT REPORT

🎯 1. Career Fit Score (0–100%)

🚀 2. Future Skills Required (2025–2030)

📈 3. AI Automation Impact

💼 4. Missing Skills (Based on User Skills)

🧭 5. 30-Day Learning Roadmap (Week 1 → Week 4)

📚 6. Tools & Technologies To Learn

📊 7. Upgrade Impact Score

💡 8. Future Career Path (2025+)
"""

    # 🔥 EXACT SAME FORMAT AS AI INSIGHTS (this is the version your Groq supports)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content
