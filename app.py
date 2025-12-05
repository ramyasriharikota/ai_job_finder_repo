# app.py
from flask import Flask, render_template, request, jsonify
from agents.linkedin_agent import search_linkedin
from agents.ai_agent import analyze_job_with_groq
from agents.future_agent import future_skill_report
from agents.reasoning_agent import reasoning_analysis
from agents.career_predict_agent import career_prediction
from flask import make_response
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    role = request.form.get("role", "")
    location = request.form.get("location", "")
    user_skills = request.form.get("skills", "")

    jobs = search_linkedin(role, location, show_browser=True)

    for j in jobs:
        j.setdefault("title", "Unknown")
        j.setdefault("company", "")
        j.setdefault("location", "")
        j.setdefault("source", "LinkedIn")
        j.setdefault("link", "#")
        j.setdefault("description", "")
        j["user_skills"] = user_skills

    response = make_response(render_template("results.html", jobs=jobs))
    response.headers["Clear-Cache"] = "1"
    return response


@app.route("/analyze", methods=["POST"])
def analyze():
    payload = request.get_json(force=True)
    title = payload.get("title", "")
    company = payload.get("company", "")
    description = payload.get("description", "") or f"{title} at {company}"
    user_skills = payload.get("user_skills", "")

    try:
        ai_result = analyze_job_with_groq(title, company, description, user_skills)
        return jsonify({"ok": True, "ai": ai_result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/future_skills", methods=["POST"])
def future_skills():
    data = request.get_json(force=True)
    title = data.get("title", "")
    company = data.get("company", "")
    location = data.get("location", "")
    user_skills = data.get("user_skills", "")

    try:
        report = future_skill_report(title, company, location, user_skills)
        return jsonify({"ok": True, "report": report})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/rank_jobs", methods=["POST"])
def rank_jobs():
    data = request.get_json(force=True)
    jobs = data.get("jobs", [])
    skills = data.get("skills", "")

    skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
    rankings = []

    for job in jobs:
        text = " ".join([
            job.get("title", ""),
            job.get("company", ""),
            job.get("location", "")
        ]).lower()

        score = 0

        for sk in skill_list:
            if sk in text:
                score += 20

        boosts = {
            "python": 15,
            "sql": 15,
            "machine learning": 20,
            "ml": 10,
            "data": 10,
            "analyst": 20,
            "engineer": 10,
            "mongo": 10,
            "power bi": 10
        }

        for key, val in boosts.items():
            if key in text:
                score += val

        score = min(score, 100)

        rankings.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "score": score
        })

    rankings = sorted(rankings, key=lambda x: x["score"], reverse=True)

    return jsonify({"ok": True, "rankings": rankings})


@app.route("/reasoning", methods=["POST"])
def reasoning():
    data = request.get_json(force=True)
    try:
        report = reasoning_analysis(
            data.get("title", ""),
            data.get("company", ""),
            data.get("description", ""),
            data.get("user_skills", "")
        )
        return jsonify({"ok": True, "report": report})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/career_predict", methods=["POST"])
def career_predict():
    data = request.get_json(force=True)
    try:
        report = career_prediction(
            data.get("title", ""),
            data.get("company", ""),
            data.get("user_skills", "")
        )
        return jsonify({"ok": True, "report": report})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/consensus", methods=["POST"])
def consensus():
    data = request.get_json(force=True)

    ai = data.get("ai_insights", "")
    fs = data.get("future_skills", "")
    rs = data.get("reasoning", "")
    cp = data.get("career_path", "")

    from agents.autogen_agent import run_consensus

    try:
        final = run_consensus(ai, fs, rs, cp)
        return jsonify({"ok": True, "report": final})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
# 🚀 NEW: Resume Upload → Extract Skills API
# ============================================================
import PyPDF2
import docx
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def pdf_extract(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for pg in reader.pages:
        t = pg.extract_text()
        if t:
            text += t + "\n"
    return text

def docx_extract(file):
    d = docx.Document(file)
    return "\n".join([p.text for p in d.paragraphs])


@app.post("/extract_skills")
def extract_skills():
    try:
        file = request.files.get("resume")
        if not file:
            return {"ok": False, "error": "No file uploaded"}

        name = file.filename.lower()

        if name.endswith(".pdf"):
            text = pdf_extract(file)
        elif name.endswith(".doc") or name.endswith(".docx"):
            text = docx_extract(file)
        else:
            return {"ok": False, "error": "Unsupported file type"}

        prompt = f"""
        Extract ONLY the technical skills that are explicitly written in the resume.

VERY IMPORTANT RULES:
- Do NOT infer or guess skills.
- Do NOT add skills based on assumptions.
- Do NOT include anything "implied" or "related".
- Include skills ONLY if they are directly mentioned in the text.

Extract the following categories ONLY if explicitly present:
- Programming Languages
- Tools
- Frameworks
- Databases
- Cloud Platforms (only if AWS / GCP / Azure are explicitly mentioned)
- AI/ML keywords (only if explicitly mentioned)
- Technical skills used in projects

Return ONLY a comma-separated list of explicit skills. No descriptions, no extra words.

        Resume:
        {text}
        """

        out = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        skills = out.choices[0].message.content.strip()

        return {"ok": True, "skills": skills}

    except Exception as e:
        return {"ok": False, "error": str(e)}
    


from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.post("/chat")
def chat():
    data = request.json
    message = data.get("message", "")
    skills = data.get("skills", "")
    jobs = data.get("jobs", [])

    # If user is just greeting → DON'T use skills
    greetings = ["hi", "hello", "hey", "hii", "heyy", "yo", "good morning", "good evening"]

    if message.lower().strip() in greetings:
        use_skills = False
    else:
        use_skills = True

    # If using skills only when relevant
    skill_context = skills if use_skills else "None (user did not request skill-based help)"

    prompt = f"""
You are an **AI Job Coach** — a professional mentor for job seekers.
Your tasks:
- Answer professionally
- Give career guidance, roadmap, suggestions
- Use user skills & job list when relevant
- Keep answers simple, friendly, and helpful

Rules:
- Respond ONLY to the user's current message.
- If the user did not ask anything career-related, DO NOT mention their skills.
- If the message is a greeting, respond simply and warmly.
- Use user skills ONLY if they ask about jobs, roles, resume, career, roadmap, learning, or interviews.
- Never make assumptions or hallucinate.
- Keep responses professional, short, and helpful.

User skills (only if needed):
{skill_context}

User message:
"{message}"

Now generate the best possible reply.
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = completion.choices[0].message.content
    return jsonify({"reply": reply})






if __name__ == "__main__":
    app.run(debug=True, port=5001)
