# Speak_Smart
Speak Smart is a tool that analyses and evaluates audio transcript of a self-introduction given by the user either in textual or uploaded file format. Speak Smart is unique since it uses real time LLM integration to evaluate user's response.
## Metrics take into consideration :-
### Content & Structure 
```
1. Salutation
2. Key Information Covered
3. Flow/Order of Information
4. Speech Rate
5. Filler Word Rate
```
### Language & Clarity 
```
1. Grammar
2. Vocabulary
3. Flow Quality
4. Clarity
```
### Engagement & Uniqueness
```
1. Engagement
2. Unique Point
```
---

# 📄 Steps to Run the Transcript Scoring Tool Locally

(Uses Gemini + Python Metrics)


---

## 1. Environment Setup

### Clone the repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

---

## 2. Create and Activate Virtual Environment

### Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Typical dependencies include:

```
python-dotenv
google-generativeai
textblob
vaderSentiment
regex
requests
numpy
flask

```

(Your actual requirements.txt governs final list.)

---

## 4. Configure Gemini API Key

### You must create an environment variable:

### Windows:

```bash
set GEMINI_API_KEY=YOUR_KEY_HERE
```

### Mac / Linux:

```bash
export GEMINI_API_KEY=YOUR_KEY_HERE
```

💡 Your application requires this key for semantic evaluation using Gemini.

---

## 5. Run the Flask Server

```bash
python app.py
```

If successful, you’ll see:

```
 * Running on http://127.0.0.1:5000/
```

---

## 6. Use the Application

Open browser and go to:

```
http://localhost:5000
```

You will see a UI that allows:

✔ paste transcript
✔ optionally upload text file
✔ run evaluation
✔ receive:

* Python metrics
* Gemini semantic scoring
* combined weighted scores
* recommendations

---

## 7. Output Format

Your tool returns structured results such as:

```
overall_score: 82
python_metrics:
    filler_rate: 3.1%
    flow: 7
    content_density: 5.2
gemini_metrics:
    clarity_score: 8
    vocabulary_score: 7
    engagement_score: 6
    unique_point_score: 5
score_flags:
    flow: false
    clarity: false
    vocab: false
    engagement: true  <-- below threshold
```

---

## 8. Stopping the Server

Press:

```
CTRL + C
```







