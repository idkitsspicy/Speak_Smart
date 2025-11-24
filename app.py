from flask import Flask, render_template, request
from scorer_gemini import score_transcript

app = Flask(__name__)

def highlight_bad_segments(transcript):
    filler_words = ["um", "uh","uhh", "like", "you know", "basically", "actually","ummm","uhhh","don't know","not sure","ahh","hmm","So","so"]

    for w in filler_words:
        transcript = transcript.replace(
            f" {w} ",
            f" <span class='bad'>{w}</span> "
        )

    return transcript


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        transcript = request.form.get("transcript", "").strip()
        context = request.form.get("context", "interview").strip()

        file = request.files.get("file")
        if file and file.filename != "":
            transcript = file.read().decode("utf-8")

        # Score transcript
        result = score_transcript(transcript, rubric=None, context=context)

        # Compute transcript length
        char_count = len(transcript)
        word_count = len(transcript.split())
        
        # dynamic scoring thresholds
        result['score_flags'] = {
            "flow": result['python_metrics'].get('flow', 0) < 5,
            "clarity": result['gemini_metrics'].get('clarity_score', 0) < 5,
            "grammar": result['gemini_metrics'].get('grammar_score', 0) < 7,
            "vocab": result['gemini_metrics'].get('vocab_score', 0) < 5,
            "engagement": result['gemini_metrics'].get('engagement_score', 0) < 5,
            "unique": result['gemini_metrics'].get('unique_point_score', 0) < 5
        }

        # highlight transcript BEFORE sending to UI
        result['highlighted_transcript'] = highlight_bad_segments(transcript)

        return render_template(
            "results.html",
            result=result,
            score_flags=result['score_flags'],
            char_count=char_count,
            word_count=word_count,
            transcript=transcript
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
