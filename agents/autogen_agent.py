# agents/autogen_agent.py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

def run_consensus(ai_insights, future_skills, reasoning, career_path):
    """
    Combine 4 agent outputs into a single deterministic consensus report.
    IMPORTANT: This function expects text outputs from the 4 agents (strings).
    It does NOT call other agents itself.
    """

    prompt = f"""
You are a Moderator AI whose job is to COMBINE and SYNTHESIZE the following four agent reports
into a single final CONSENSUS REPORT. Use the agent texts as source material — do NOT invent
facts not supported by the inputs.

DETERMINISTIC RULES:
- Do NOT print any internal debate, turns, or chain-of-thought.
- Do NOT include 'Turn' or 'Critic' or 'Moderator' lines.
- Do NOT add extra speculative information beyond what the inputs support.
- Keep output concise and human-readable.
- Be deterministic: produce the same structured report for the same inputs.

OUTPUT FORMAT (exactly):
1) 🧾 Executive Summary (1–2 lines)
2) 🎯 Unified Career Fit Score: <number>% — one short justification line
3) 🏋️ Combined Key Strengths
- <bullet 1>
- <bullet 2>
- <bullet 3>
4) ⚠️ Top 5 Critical Gaps (ranked)
1. ...
2. ...
3. ...
4. ...
5. ...
5) 🧭 Priority Roadmap (Week 1 → Week 4) — 4 short bullets (Week 1, Week 2, Week 3, Week 4)
6) 📈 Career Projection (1 line)
7) ✅ Final Recommendation (Apply / Apply After Upskill / Don't Apply) — 1-line rationale

Now combine these inputs:

--- AI_INSIGHTS ---
{ai_insights}

--- FUTURE_SKILLS ---
{future_skills}

--- REASONING ---
{reasoning}

--- CAREER_PATH ---
{career_path}

Produce ONLY the final CONSENSUS REPORT following the exact format above.
"""

    try:
        # temperature=0 for increased determinism
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=900
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Consensus Error: {e}]"
