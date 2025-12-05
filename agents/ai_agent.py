# agents/ai_agent.py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_job_with_groq(title, company, description, user_skills):
    prompt = f"""
You are an expert job analysis assistant.

### ⭐ Job Match Summary
- Title: {title}
- Company: {company}

### ✅ Skill Match (0–100%)
Estimate match % and explain.

### 🧠 Key Strengths
List 3 bullet points.

### ⚠️ Missing Skills
List missing areas.

### 🎯 Should You Apply?
YES or NO with explanation.

User Skills: {user_skills}
Job Description: {description}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content
