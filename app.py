from flask import Flask, render_template_string, request

app = Flask(__name__)

# ===========================
# HTML TEMPLATE
# ===========================
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grade Calculators</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            min-height: 100vh;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            align-items: flex-start;
            padding: 40px;
            background: url("/static/image_6487327-scaled.jpg") no-repeat center center fixed;
            background-size: cover;
            position: relative;
        }
        body::after {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.25);
            z-index: -1;
        }
        .container {
            background: rgba(255, 255, 255, 0.85);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            width: 380px;
            text-align: center;
            margin: 20px;
            animation: slideFadeIn 1s ease-in-out;
        }
        @keyframes slideFadeIn {
            from { opacity: 0; transform: translateY(50px) scale(0.95); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }
        h1 { margin-bottom: 15px; color: #2c3e50; font-size: 22px; }
        input {
            width: 90%;
            padding: 10px;
            margin: 6px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        button {
            margin-top: 12px;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            transition: 0.3s;
        }
        button:hover { background: #2980b9; }
        .result {
            margin-top: 15px;
            padding: 12px;
            border-radius: 10px;
            background: rgba(241, 248, 255, 0.9);
            color: #2c3e50;
            text-align: left;
        }
        .status { font-weight: bold; }
    </style>
</head>
<body>
    <!-- Prelim Calculator -->
    <div class="container">
        <h1>📊 Prelim Calculator</h1>
        <form method="POST" action="/prelim">
            <input type="number" name="absences" placeholder="Absences" required><br>
            <input type="number" name="exam" placeholder="Prelim Exam (0-100)" required><br>
            <input type="number" name="quizzes" placeholder="Quizzes (0-100)" required><br>
            <input type="number" name="requirements" placeholder="Requirements (0-100)" required><br>
            <input type="number" name="recitation" placeholder="Recitation (0-100)" required><br>
            <button type="submit">Calculate</button>
        </form>
        {% if prelim_result %}
        <div class="result">
            <p class="status">{{ prelim_result }}</p>
            {% if prelim_grade is not none %}
                <p>📌 <b>Prelim Grade:</b> {{ prelim_grade }}</p>
                <p>✅ To <b>PASS (75%)</b>, you need:<br>
                   Midterm = {{ pass_midterm }}, Finals = {{ pass_finals }}</p>
                <p>🌟 To be a <b>Dean's Lister (90%)</b>, you need:<br>
                   Midterm = {{ dl_midterm }}, Finals = {{ dl_finals }}</p>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <!-- Midterm Calculator -->
    <div class="container">
        <h1>📘 Midterm Calculator</h1>
        <form method="POST" action="/midterm">
            <input type="number" name="absences" placeholder="Absences" required><br>
            <input type="number" name="exam" placeholder="Midterm Exam (0-100)" required><br>
            <input type="number" name="quizzes" placeholder="Quizzes (0-100)" required><br>
            <input type="number" name="requirements" placeholder="Requirements (0-100)" required><br>
            <input type="number" name="recitation" placeholder="Recitation (0-100)" required><br>
            <button type="submit">Calculate</button>
        </form>
        {% if midterm_result %}
        <div class="result">
            <p class="status">{{ midterm_result }}</p>
            {% if midterm_grade is not none %}
                <p>📘 <b>Midterm Grade:</b> {{ midterm_grade }}</p>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <!-- Finals Calculator -->
    <div class="container">
        <h1>📕 Finals Calculator</h1>
        <form method="POST" action="/finals">
            <input type="number" name="absences" placeholder="Absences" required><br>
            <input type="number" name="exam" placeholder="Final Exam (0-100)" required><br>
            <input type="number" name="quizzes" placeholder="Quizzes (0-100)" required><br>
            <input type="number" name="requirements" placeholder="Requirements (0-100)" required><br>
            <input type="number" name="recitation" placeholder="Recitation (0-100)" required><br>
            <button type="submit">Calculate</button>
        </form>
        {% if finals_result %}
        <div class="result">
            <p class="status">{{ finals_result }}</p>
            {% if finals_grade is not none %}
                <p>📕 <b>Finals Grade:</b> {{ finals_grade }}</p>
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# ===========================
# BACKEND LOGIC
# ===========================
def compute_period_grade(absences, exam, quizzes, requirements, recitation):
    if absences >= 4:
        return None, "❌ FAILED due to 4 or more absences."
    attendance = max(0, 100 - (absences * 10))
    class_standing = (0.40 * quizzes) + (0.30 * requirements) + (0.30 * recitation)
    grade = (0.60 * exam) + (0.10 * attendance) + (0.30 * class_standing)
    return round(grade, 2), "✅ Calculation Successful!"

def required(midterm_weight, finals_weight, target, prelim):
    remaining = target - (0.20 * prelim)
    midterm = finals = remaining / (midterm_weight + finals_weight/2)
    return round(midterm, 2), round(finals, 2)

@app.route("/", methods=["GET"])
def home():
    return render_template_string(html_template)

@app.route("/prelim", methods=["POST"])
def prelim():
    try:
        absences = int(request.form.get("absences"))
        exam = float(request.form.get("exam"))
        quizzes = float(request.form.get("quizzes"))
        requirements = float(request.form.get("requirements"))
        recitation = float(request.form.get("recitation"))

        grade, msg = compute_period_grade(absences, exam, quizzes, requirements, recitation)

        if grade is not None:
            pass_midterm, pass_finals = required(0.30, 0.50, 75, grade)
            dl_midterm, dl_finals = required(0.30, 0.50, 90, grade)
            return render_template_string(html_template,
                                          prelim_grade=grade,
                                          prelim_result=msg,
                                          pass_midterm=pass_midterm,
                                          pass_finals=pass_finals,
                                          dl_midterm=dl_midterm,
                                          dl_finals=dl_finals)
        return render_template_string(html_template, prelim_result=msg)

    except:
        return render_template_string(html_template, prelim_result="⚠️ Invalid input!")

@app.route("/midterm", methods=["POST"])
def midterm():
    try:
        absences = int(request.form.get("absences"))
        exam = float(request.form.get("exam"))
        quizzes = float(request.form.get("quizzes"))
        requirements = float(request.form.get("requirements"))
        recitation = float(request.form.get("recitation"))
        grade, msg = compute_period_grade(absences, exam, quizzes, requirements, recitation)
        return render_template_string(html_template, midterm_grade=grade, midterm_result=msg)
    except:
        return render_template_string(html_template, midterm_result="⚠️ Invalid input!")

@app.route("/finals", methods=["POST"])
def finals():
    try:
        absences = int(request.form.get("absences"))
        exam = float(request.form.get("exam"))
        quizzes = float(request.form.get("quizzes"))
        requirements = float(request.form.get("requirements"))
        recitation = float(request.form.get("recitation"))
        grade, msg = compute_period_grade(absences, exam, quizzes, requirements, recitation)
        return render_template_string(html_template, finals_grade=grade, finals_result=msg)
    except:
        return render_template_string(html_template, finals_result="⚠️ Invalid input!")

if __name__ == "__main__":
    app.run(debug=True)


