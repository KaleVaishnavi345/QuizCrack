from flask import Flask, render_template, request, session
import random
from questions import questions

app = Flask(__name__)
app.secret_key = "quiz_secret_key"

# In-memory leaderboard (top 5)
leaderboard = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/quiz/<category>")
def quiz(category):
    if category not in questions:
        return "Category not found", 404

    # Pick 18 random questions from the selected category
    selected = random.sample(questions[category], 18)

    # Store correct answers in session
    session['quiz_data'] = selected
    session['answers'] = {f"q{i}": q['answer'] for i, q in enumerate(selected)}
    session['category'] = category

    return render_template("quiz.html", questions=selected, enumerate=enumerate, category=category)

@app.route("/submit", methods=["POST"])
def submit():
    quiz_data = session.get("quiz_data", [])
    correct_count = 0
    points = 0
    results = []

    for i, q in enumerate(quiz_data):
        user_answer = request.form.get(f"q{i}")
        is_correct = (user_answer == q["answer"])
        if is_correct:
            correct_count += 1
            points += 10  # 10 points per correct

        results.append({
            "question": q["question"],
            "user_answer": user_answer if user_answer else "Not Attempted",
            "correct_answer": q["answer"],
            "is_correct": is_correct
        })

    username = request.form.get("username", "Guest")

    # Update leaderboard with points (not correct_count)
    leaderboard.append({"username": username, "score": points})
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    if len(leaderboard) > 5:
        leaderboard.pop()

    category = session.get('category', 'Unknown')
    return render_template("result.html",
                           correct=correct_count,   # number of correct answers
                           points=points,           # total score
                           total=len(quiz_data),
                           results=results,
                           leaderboard=leaderboard,
                           category=category)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
