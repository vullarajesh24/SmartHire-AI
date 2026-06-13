from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
from flask import Flask, render_template, request, session,redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "smarthire"

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("smarthire.db")

        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("smarthire.db")

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session['username'] = username

            return render_template('dashboard.html', username=username)

        else:
            return "Invalid Username or Password"
    return render_template('login.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/coding')
def coding():
    return render_template('coding.html')


@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/save_score')
def save_score():

    username = session.get('username')

    if not username:
        return redirect('/login')

    answered = int(request.args.get('answered', 0))
    score = int((answered / 3) * 100)

    session['score'] = score

    conn = sqlite3.connect("smarthire.db")
    cursor = conn.cursor()

    # Save the score
    cursor.execute(
        "INSERT INTO scores (username, score) VALUES (?, ?)",
        (username, score)
    )

    # Optional cleanup
    cursor.execute("DELETE FROM scores WHERE username IS NULL")
    cursor.execute("DELETE FROM scores WHERE username='None'")

    conn.commit()
    conn.close()

    return render_template(
        'result.html',
        username=username,
        score=score,
        answered=answered
    )
@app.route('/admin')
def admin():

    conn = sqlite3.connect("smarthire.db")
    cursor = conn.cursor()

    search = request.args.get('search')

    if search:
        cursor.execute(
            "SELECT username, score FROM scores WHERE username LIKE ?",
            ('%' + search + '%',)
        )
    else:
        cursor.execute(
            "SELECT username, score FROM scores"
        )

    scores = cursor.fetchall()

    # Top Performer
    cursor.execute(
        "SELECT username, score FROM scores ORDER BY score DESC LIMIT 1"
    )
    top_user = cursor.fetchone()

    # Total Attempts
    cursor.execute("SELECT COUNT(*) FROM scores")
    total_attempts = cursor.fetchone()[0]

    # Average Score
    cursor.execute("SELECT AVG(score) FROM scores")
    average_score = cursor.fetchone()[0]

    if average_score is None:
        average_score = 0
    else:
        average_score = round(average_score, 2)

    # Leaderboard
    cursor.execute("""
        SELECT username, MAX(score) AS best_score
        FROM scores
        WHERE username IS NOT NULL
        GROUP BY username
        ORDER BY best_score DESC
        LIMIT 5
    """)

    leaderboard = cursor.fetchall()

    conn.close()

    return render_template(
        'admin.html',
        scores=scores,
        top_user=top_user,
        total_attempts=total_attempts,
        average_score=average_score,
        leaderboard=leaderboard
    )

    


from openpyxl import Workbook
from flask import send_file
import sqlite3
@app.route('/export_excel')
def export_excel():

    conn = sqlite3.connect("smarthire.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username, score FROM scores")
    data = cursor.fetchall()

    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Scores"

    ws.append(["Username", "Score"])

    for row in data:
        ws.append(row)

    wb.save("scores.xlsx")

    return send_file(
        "scores.xlsx",
        as_attachment=True
    )
@app.route('/face_verify')
def face_verify():
    return render_template('face_verify.html')


@app.route('/pdf_report')
def pdf_report():

    username = session.get('username', 'Unknown')

    score = session.get('score',0)

    status = "Selected" if score >= 50 else "Not Selected"

    pdf = SimpleDocTemplate("candidate_report.pdf")

    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("SmartHire AI Candidate Report", styles['Title']))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Candidate Name: {username}", styles['Normal']))
    content.append(Paragraph(f"Score: {score}/100", styles['Normal']))
    content.append(Paragraph(f"Status: {status}", styles['Normal']))

    pdf.build(content)

    return send_file(
        "candidate_report.pdf",
        as_attachment=True
    )


@app.route('/logout')
def logout():
    session.clear()   # Clears all session data
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)