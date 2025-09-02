from flask import Flask, render_template_string, request

app = Flask(__name__)

# HTML template with custom design
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prelim Grade Calculator</title>
    <style>
         body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: url("/static/image_6487327-scaled.jpg") no-repeat center center fixed;
            background-size: cover;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }


        }
        .container {
            background: #fff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            width: 400px;
            text-align: center;
            animation: fadeIn 0.8s ease-in-out;
        }
        h1 {
            margin-bottom: 20px;
            color: #2c3e50;
        }
        input {
            width: 90%;
            padding: 10px;
            margin: 8px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        button {
            margin-top: 15px;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: 0.3s;
        }
        button:hover {
            background: #2980b9;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            background: #f1f8ff;
            color: #2c3e50;
            text-align: left;
        }
        .status {
            font-weight: bold;
            color: #e74c3c;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Prelim Grade Calculator</h1>
        <form method="POST">
            <input type="number" name="absences" placeholder="Number of Absences" required><br>
            <input type="number" name="prelim_exam" placeholder="Prelim Exam Grade" required><br>
            <input type="number" name="quizzes" placeholder="Quizzes Grade" required><br>
            <input type="number" name="requirements" placeholder="Requirements Grade" required><br>
            <input type="number" name="recitation" placeholder="Recitation Grade" required><br>
            <button type="submit">Calculate</button>
        </form>

        {% if result %}
        <div class="result">
            <p class="status">{{ result }}</p>
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
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def calculate():
    result = None
    prelim_grade = None
    pass_midterm = dl_midterm = None
    pass_finals = dl_finals = None

    if request.method == "POST":
        try:
            absences = int(request.form.get("absences"))
            prelim_exam = float(request.form.get("prelim_exam"))
            quizzes = float(request.form.get("quizzes"))
            requirements = float(request.form.get("requirements"))
            recitation = float(request.form.get("recitation"))

            # Validation
            for grade in [prelim_exam, quizzes, requirements, recitation]:
                if grade < 0 or grade > 100:
                    result = "⚠️ Invalid input! Grades must be 0–100."
                    return render_template_string(html_template, result=result)

            if absences < 0:
                result = "⚠️ Invalid input! Absences cannot be negative."
                return render_template_string(html_template, result=result)

            # Attendance rule
            if absences >= 4:
                result = "❌ FAILED due to 4 or more absences."
            else:
                attendance = max(0, 100 - (absences * 10))
                class_standing = (0.40 * quizzes) + (0.30 * requirements) + (0.30 * recitation)
                prelim_grade = (0.60 * prelim_exam) + (0.10 * attendance) + (0.30 * class_standing)

                # Required grades for passing & dean’s list
                def required(midterm_weight, finals_weight, target, prelim):
                    remaining = target - (0.20 * prelim)
                    # Simplified assumption: Midterm = Finals
                    midterm = finals = remaining / (midterm_weight + finals_weight/2)
                    return round(midterm, 2), round(finals, 2)

                pass_midterm, pass_finals = required(0.30, 0.50, 75, prelim_grade)
                dl_midterm, dl_finals = required(0.30, 0.50, 90, prelim_grade)

                result = "✅ Calculation Successful!"

        except ValueError:
            result = "⚠️ Invalid input! Please enter numbers only."

    return render_template_string(html_template,
                                  result=result,
                                  prelim_grade=round(prelim_grade, 2) if prelim_grade else None,
                                  pass_midterm=pass_midterm,
                                  pass_finals=pass_finals,
                                  dl_midterm=dl_midterm,
                                  dl_finals=dl_finals)

if __name__ == "__main__":
    app.run(debug=True)
