import re
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv



# -----------------------------------------------------------
# SETUP GEMINI
# -----------------------------------------------------------

load_dotenv()  # loads .env

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")


# -----------------------------------------------------------
# BASIC PYTHON HELPERS
# -----------------------------------------------------------

def count_words(text):
    words = re.findall(r"\b\w+\b", text)
    return len(words)


def filler_word_rate(text):
    fillers = ["uh", "um", "like", "basically", "you know", "literally"]
    words = re.findall(r"\b\w+\b", text.lower())
    if len(words) == 0:
        return 0
    count = sum(1 for w in words if w in fillers)
    return count / len(words)




def salutation_score(text):
    t = text.lower()
    score=0
    # Basic salutations → 2
    if re.search(r"\bhello\b", t) or re.search(r"\bhi\b", t):
        score= 2

    # Formal salutations → 4
    if any(phrase in t for phrase in ["good morning", "good afternoon", "good evening"]):
        score= 4

    # Enthusiastic salutations → 5
    enthusiastic_phrases = [
        "excited to",
        "thrilled to",
        "happy to",
        "glad to",
        "feeling great to",
        "delighted to"
    ]
    if any(p in t for p in enthusiastic_phrases):
        score= 5

    # If none found → no salutation → score 0
    return score



def speech_rate_score(text):
    wc = count_words(text)
    if 60 <= wc <= 120:
        return 10
    elif 40 <= wc < 60 or 120 < wc <= 150:
        return 5
    else:
        return 0


# -----------------------------------------------------------
# KEY INFO PRESENCE — 8 categories
# -----------------------------------------------------------

KEYWORD_CATEGORIES = {
    "name": ["my name is", "i am", "this is"],
    "age": ["years old", "year old", "yrs old"],
    "class": ["class", "grade", "studying in"],
    "school": ["school", "high school"],
    "family": ["family", "parents", "brother", "sister", "siblings"],
    "hobbies": ["i like", "i love", "my hobby", "my hobbies are", "interested in","interests"],
    "goals": ["my goal", "i want to become", "i aim to", "in the future i want","goals"],
    "unique_point": ["something unique", "unique about me", "special about me"]
}


def score_key_info(text):
    t = text.lower()
    max_points = 30
    per_category = max_points / len(KEYWORD_CATEGORIES)
    score = 0

    for category, keywords in KEYWORD_CATEGORIES.items():

        # Age special regex
        if category == "age":
            if re.search(r"\b\d+\s*(years old|year old|yrs old)\b", t):
                score += per_category
                continue

        found = any(kw in t for kw in keywords)
        if found:
            score += per_category

    return score


def flow_score(text):
    t = text.lower()

    # 1. Salutation keywords
    salutation = ["hello", "hi", "good morning", "good afternoon", "good evening"]

    # 2. Basic details in expected order
    basic = [
        "my name is", 
        "i am", 
        "years old", 
        "class", 
        "grade", 
        "studying", 
        "school",
        "from",     # place
        "i live in" # place
    ]

    # 3. Additional details
    additional = [
        "family", 
        "parents", 
        "brother", 
        "sister",
        "hobby", 
        "hobbies", 
        "i like", 
        "i love",
        "interested",
        "goal", 
        "future", 
        "i want to become",
    ]

    # 4. Closing
    closing = ["thank you", "that's all", "this is all about me"]

    # Build the expected sequence in ORDER
    sequence = [
        salutation,
        basic,
        additional,
        closing
    ]

    order_score = 0
    last_index = -1

    # iterate groups in order: salutation -> basic -> additional -> closing
    for group in sequence:
        found_pos = None

        for keyword in group:
            idx = t.find(keyword)
            if idx != -1:
                found_pos = idx
                break

        # If this group keyword appears AND appears in order → score++
        if found_pos is not None:
            if found_pos > last_index:
                order_score += 1
                last_index = found_pos

    # Normalize:
    # 4 groups → score 0–4 → scale to 0–5
    flow = (order_score / 4) * 5

    return round(flow, 2)



# -----------------------------------------------------------
# GEMINI LLM SCORING (Grammar, Vocab, Sentiment, Flow, Clarity)
# -----------------------------------------------------------

def gemini_analysis(text, context):
    prompt = f"""
You are scoring a student's self-introduction transcript to test their communication skills.

Analyze the transcript and return STRICT JSON with these keys:

1. grammar_score (0–10)
2. vocab_score (0–10)
3. flow_quality (0–10)
4. clarity_score (0–15)
5. engagement_score (0–15)

6. unique_point_score (0–5)
   - Score based on whether the student mentioned anything special, uncommon, or impressive 
     (award, achievement, responsibility, unique skill, project, leadership, creativity, 
      volunteering, competition, entrepreneurship, or any notable detail).
   - 0 means nothing unique was found.
   - 5 means clearly unique or special information was expressed.

7. unique_point_explanation (1–2 sentence description)

8. strengths (list of strings)
9. improvements (list of strings)

Context is: {context}.

Transcript:
{text}

Return JSON ONLY.
"""

    response = model.generate_content(prompt)
    cleaned = response.text.strip("```json").strip("```")
    return json.loads(cleaned)


# -----------------------------------------------------------
# FINAL SCORE COMBINER
# -----------------------------------------------------------

def score_transcript(transcript, rubric, context="interview"):
    transcript = transcript.strip()

    # -------- PYTHON SCORES --------
    sal = salutation_score(transcript)
    keyinfo = score_key_info(transcript)
    flow = flow_score(transcript)
    speech = speech_rate_score(transcript)
    filler_rate = filler_word_rate(transcript)
   

    # -------- GEMINI SCORES --------
    ai = gemini_analysis(transcript, context)

    grammar = ai["grammar_score"]
    vocab = ai["vocab_score"]
    ai_flow = ai["flow_quality"]
    clarity = ai["clarity_score"]
    engagement = ai["engagement_score"]
    unique_score= ai["unique_point_score"]

    # -------- COMBINE USING RUBRIC WEIGHTS --------

    # Content & Structure = 40
    content_total = sal + keyinfo + flow + (ai_flow / 10) * 5 + unique_score
    content_final = (content_total / 40) * 40

    # Speech Rate = 10
    sr_final = (speech / 10) * 10

    # Language & Grammar = 20
    lang_total = grammar + vocab
    lang_final = (lang_total / 20) * 20

    # Clarity = 15
    clarity_final = (clarity / 15) * 15

    # Engagement = 15
    engage_final = (engagement / 15) * 15

    overall = content_final + sr_final + lang_final + clarity_final + engage_final

    
    

    # -------- RESULT --------
    return {
        "overall": round(overall, 2),
        "python_metrics": {
            "salutation": sal,
            "key_info": keyinfo,
            "flow": flow,
            "speech_rate_score": speech,
            "filler_word_rate": filler_rate,
            
        },
        "gemini_metrics": ai
    }
