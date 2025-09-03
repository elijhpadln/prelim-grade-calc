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
    <title>Semester Grade Calculator</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
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
            background: rgba(255, 255, 255, 0.9);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            width: 500px;
            text-align: center;
        }
        h1 { margin-bottom: 20px; color: #2c3e50; }
        h2 { margin-top: 20px; font-size: 18px; color: #34495e; }
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
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            background: rgba(241, 248, 255, 0.95);
            color: #2c3e50;
            text-align: left;
        }
        .status { font-weight: bold; }
        .pass { color: green; font-weight: bold; }
        .fail { color: red; font-weight: bold; }
        .deans { color: #e67e22; font-weight: bold; }
    </style>

    <!-- JavaScript Validation -->
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const gradeInputs = document.querySelectorAll("input[type='number'][min][max]");
        gradeInputs.forEach(input => {
            input.addEventListener("input", function() {
                let val = parseFloat(this.value);
                if (val > 100) this.value = 100;
                if (val < 0) this.value = 0;
            });
        });
    });
    </script>
</head>
<body>
    <div class="container">
        <h1>🎓 Semester Grade Calculator</h1>
        <form method="POST">
            <h2>Attendance (Whole Semester)</h2>
            <input type="number" name="absences" placeholder="Total Absences" min="0" required><br>

            <h2>Prelim</h2>
            <input type="number" name="prelim_exam" placeholder="Prelim Exam (0-100)" min="0" max="100" required><br>
            <input type="number" name="prelim_quizzes" placeholder="Prelim Quizzes (0-100)" min="0" max="100" required><br>
            <input type="number" name="prelim_requirements" placeholder="Prelim Requirements (0-100)" min="0" max="100" required><br>
            <input type="number" name="prelim_recitation" placeholder="Prelim Recitation (0-100)" min="0" max="100" required><br>

            <h2>Midterm</h2>
            <input type="number" name="midterm_exam" placeholder="Midterm Exam (0-100)" min="0" max="100" required><br>
            <input type="number" name="midterm_quizzes" placeholder="Midterm Quizzes (0-100)" min="0" max="100" required><br>
            <input type="number" name="midterm_requirements" placeholder="Midterm Requirements (0-100)" min="0" max="100" required><br>
            <input type="number" name="midterm_recitation" placeholder="Midterm Recitation (0-100)" min="0" max="100" required><br>

            <h2>Finals</h2>
            <input type="number" name="finals_exam" placeholder="Finals Exam (0-100)" min="0" max="100" required><br>
            <input type="number" name="finals_quizzes" placeholder="Finals Quizzes (0-100)" min="0" max="100" required><br>
            <input type="number" name="finals_requirements" placeholder="Finals Requirements (0-100)" min="0" max="100" required><br>
            <input type="number" name="finals_recitation" placeholder="Finals Recitation (0-100)" min="0" max="100" required><br>

            <button type="submit">Calculate</button>
        </form>

        {% if result %}
        <div class="result">
            <p class="status">{{ result }}</p>
            {% if prelim_grade is not none %}
                <p>📌 <b>Prelim Grade:</b> {{ prelim_grade }}</p>
                <p>📘 <b>Midterm Grade:</b> {{ midterm_grade }}</p>
                <p>📕 <b>Finals Grade:</b> {{ finals_grade }}</p>
                <hr>
                <p>🎯 <b>Overall Grade:</b> {{ overall_grade }}</p>
                <p><b>Status:</b> 
                    {% if overall_grade >= 90 %}
                        <span class="deans">🌟 Dean's Lister!</span>
                    {% elif overall_grade >= 75 %}
                        <span class="pass">✅ PASSED</span>
                    {% else %}
                        <span class="fail">❌ FAILED</span>
                    {% endif %}
                </p>
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
def safe_float(value):
    try:
        val = float(value)
        if 0 <= val <= 100:
            return val
        else:
            return None
    except (TypeError, ValueError):
        return None

def compute_term(absences, exam, quizzes, requirements, recitation):
    if absences >= 4:
        return None, "❌ FAILED due to 4 or more absences."
    for g in [exam, quizzes, requirements, recitation]:
        if g is None:
            return None, "⚠️ Invalid input! Grades must be 0–100."
    attendance = max(0, 100 - (absences * 10))
    class_standing = (0.40 * quizzes) + (0.30 * requirements) + (0.30 * recitation)
    grade = (0.60 * exam) + (0.10 * attendance) + (0.30 * class_standing)
    return round(grade, 2), "✅ Calculation Successful!"

@app.route("/", methods=["GET", "POST"])
def calculate():
    result = None
    prelim_grade = midterm_grade = finals_grade = overall_grade = None

    if request.method == "POST":
        try:
            absences = int(request.form.get("absences", 0))

            prelim_exam = safe_float(request.form.get("prelim_exam", 0))
            prelim_quizzes = safe_float(request.form.get("prelim_quizzes", 0))
            prelim_requirements = safe_float(request.form.get("prelim_requirements", 0))
            prelim_recitation = safe_float(request.form.get("prelim_recitation", 0))

            midterm_exam = safe_float(request.form.get("midterm_exam", 0))
            midterm_quizzes = safe_float(request.form.get("midterm_quizzes", 0))
            midterm_requirements = safe_float(request.form.get("midterm_requirements", 0))
            midterm_recitation = safe_float(request.form.get("midterm_recitation", 0))

            finals_exam = safe_float(request.form.get("finals_exam", 0))
            finals_quizzes = safe_float(request.form.get("finals_quizzes", 0))
            finals_requirements = safe_float(request.form.get("finals_requirements", 0))
            finals_recitation = safe_float(request.form.get("finals_recitation", 0))

            prelim_grade, msg1 = compute_term(absences, prelim_exam, prelim_quizzes, prelim_requirements, prelim_recitation)
            midterm_grade, msg2 = compute_term(absences, midterm_exam, midterm_quizzes, midterm_requirements, midterm_recitation)
            finals_grade, msg3 = compute_term(absences, finals_exam, finals_quizzes, finals_requirements, finals_recitation)

            if prelim_grade is None or midterm_grade is None or finals_grade is None:
                result = msg1 if prelim_grade is None else msg2 if midterm_grade is None else msg3
            else:
                overall_grade = (0.20 * prelim_grade) + (0.30 * midterm_grade) + (0.50 * finals_grade)
                result = "✅ Calculation Successful!"

        except ValueError:
            result = "⚠️ Invalid input! Please enter numbers only."

    return render_template_string(html_template,
                                  result=result,
                                  prelim_grade=prelim_grade,
                                  midterm_grade=midterm_grade,
                                  finals_grade=finals_grade,
                                  overall_grade=round(overall_grade, 2) if overall_grade else None)

if __name__ == "__main__":
    app.run(debug=True)



