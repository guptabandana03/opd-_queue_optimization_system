from flask import Flask
import sqlite3
from config import DATABASE_PATH
from flask import render_template, request, redirect


app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_patients_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_number INTEGER,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            visit_type TEXT,
            emergency_allowed INTEGER DEFAULT 0,
            status TEXT DEFAULT 'WAITING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


AVG_TIME_PER_PATIENT = 5

def build_priority_queue(patients):
    enriched = []

    for p in patients:
        score = 0

        # Emergency rule (SIMPLE)
        if p["visit_type"] == "Emergency" and p["emergency_allowed"] == 1:
            score += 5
        else:
            score += 1

        enriched.append({
            "data": p,
            "priority_score": score
        })

    enriched.sort(
        key=lambda x: (-x["priority_score"], x["data"]["token_number"])
    )

    return enriched


def get_priority_queue_with_time(patients):
    priority_queue = build_priority_queue(patients)

    final = []
    for index, item in enumerate(priority_queue):
        final.append({
            "data": item["data"],
            "priority_score": item["priority_score"],
            "estimated_time": index * AVG_TIME_PER_PATIENT
        })

    return final


@app.route("/")
def home():
    conn = get_db_connection()
    conn.close()
    return "OPD Queue Optimization System with DB connected!"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        visit_type = request.form["visit_type"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(token_number) FROM patients")
        last_token = cursor.fetchone()[0]
        if visit_type == "Emergency":
            emergency_allowed = 1
        else:
            emergency_allowed = 0

        if last_token is None:
            token_number = 1
        else:
            token_number = last_token + 1


        cursor.execute("""
    INSERT INTO patients (token_number, name, age, gender, visit_type, emergency_allowed)
    VALUES (?, ?, ?, ?, ?, ?)
        """, (token_number, name, age, gender, visit_type, emergency_allowed))

        conn.commit()
        conn.close()

        return f"Patient Registered Successfully! Your Token Number is {token_number}"

    return render_template("register.html")

@app.route("/queue")
def queue():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE status='WAITING'")
    patients = cursor.fetchall()
    conn.close()

    final_queue = get_priority_queue_with_time(patients)

    return render_template("queue.html", patients=final_queue)


@app.route("/doctor")
def doctor_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE status='WAITING'")
    patients = cursor.fetchall()
    conn.close()

    if not patients:
        return render_template("doctor.html", next_patient=None)

    # SAME logic as queue
    priority_queue = build_priority_queue(patients)

    next_patient = priority_queue[0]

    return render_template("doctor.html", next_patient=next_patient)


@app.route("/display")
def display_screen():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE status='WAITING'")
    patients = cursor.fetchall()
    conn.close()

    display_data = get_priority_queue_with_time(patients)

    return render_template("display.html", patients=display_data)


@app.route("/emergency/<int:patient_id>")
def emergency_override(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Emergency mark
    cursor.execute("""
        UPDATE patients
        SET visit_type = 'Emergency'
        WHERE patient_id = ?
    """, (patient_id,))

    conn.commit()
    conn.close()

    return redirect("/doctor")


@app.route("/status", methods=["GET", "POST"])
def patient_status():
    if request.method == "POST":
        token_number = int(request.form["token_number"])

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get patient
        cursor.execute(
            "SELECT * FROM patients WHERE token_number = ?",
            (token_number,)
        )
        patient = cursor.fetchone()

        if not patient:
            conn.close()
            return "Invalid Token Number"

        # Get waiting queue
        cursor.execute(
            "SELECT * FROM patients WHERE status='WAITING'"
        )
        waiting_patients = cursor.fetchall()
        conn.close()

        # Sort waiting patients same as queue logic
        priority_queue = get_priority_queue_with_time(waiting_patients)

        # Find position
        position = None
        for index, item in enumerate(priority_queue):
            if item["data"]["token_number"] == token_number:
                position = index
                break

        estimated_time = priority_queue[position]["estimated_time"]

        return render_template(
            "status.html",
            patient=patient,
            position=position,
            estimated_time=estimated_time
        )

    return render_template("status.html")

@app.route("/serve/<int:patient_id>")
def serve_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE patients
        SET status = 'DONE'
        WHERE patient_id = ?
    """, (patient_id,))
    # Emergency used → block all other emergencies
    cursor.execute("""
        UPDATE patients
        SET emergency_allowed = 0
        WHERE visit_type='Emergency'
    """)
    conn.commit()
    conn.close()

    return redirect("/doctor")

@app.route("/reset_emergency")
def reset_emergency():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE patients
        SET emergency_allowed = 1
        WHERE status='WAITING'
    """)

    conn.commit()
    conn.close()
    return "Emergency reset done"


if __name__ == "__main__":
    create_patients_table()
    app.run()
