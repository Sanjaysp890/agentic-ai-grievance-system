import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------
# DB CONNECTION
# -------------------------------------------------
def get_connection():
    return psycopg2.connect(
        dbname="grievance_db",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        host="localhost",
        port="5432"
    )

# =================================================
# USERS
# =================================================
def create_user(name, email, password, role="user", department=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (name, email, password, role, department)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING user_id;
        """,
        (name, email, password, role, department)
    )

    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id


def validate_login(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT user_id, name, role, department
        FROM users
        WHERE email = %s AND password = %s;
        """,
        (email, password)
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return {
            "user_id": row[0],
            "name": row[1],
            "role": row[2],
            "department": row[3]
        }

    return None

# =================================================
# COMPLAINTS
# =================================================
def save_complaint(original_input, english_text, input_type, language, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO complaints
        (original_input, english_text, input_type, language, status, created_at, user_id)
        VALUES (%s, %s, %s, %s, 'PENDING', NOW(), %s)
        RETURNING complaint_id;
        """,
        (original_input, english_text, input_type, language, user_id)
    )

    complaint_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return complaint_id


def update_complaint_classification(complaint_id, department, priority):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE complaints
        SET department = %s,
            priority = %s,
            status = 'IN_PROGRESS'
        WHERE complaint_id = %s;
        """,
        (department, priority, complaint_id)
    )

    conn.commit()
    cur.close()
    conn.close()


def save_department_response(complaint_id, department, response_text):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO department_response
        (complaint_id, department, response_text, status, responded_at)
        VALUES (%s, %s, %s, 'RESPONDED', NOW());
        """,
        (complaint_id, department, response_text)
    )

    cur.execute(
        """
        UPDATE complaints
        SET status = 'RESOLVED'
        WHERE complaint_id = %s;
        """,
        (complaint_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

# =================================================
# ✅ LEARNING AGENT STORAGE
# =================================================
def save_previous_responses(complaint_id, responses):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE complaints
        SET previous_responses = %s
        WHERE complaint_id = %s;
        """,
        (json.dumps(responses), complaint_id)
    )

    conn.commit()
    cur.close()
    conn.close()


def get_complaint_text(complaint_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT english_text FROM complaints WHERE complaint_id = %s;",
        (complaint_id,)
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    return row[0] if row else None

# =================================================
# ADMIN HELPERS
# =================================================
def get_complaint_department(complaint_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT department FROM complaints WHERE complaint_id = %s;",
        (complaint_id,)
    )

    row = cur.fetchone()
    cur.close()
    conn.close()

    return row[0] if row else None


def get_complaints_by_department(department):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT complaint_id, english_text, original_input, status
        FROM complaints
        WHERE department = %s
        ORDER BY complaint_id DESC;
        """,
        (department,)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "complaint_id": r[0],
            "english_text": r[1],
            "original_input": r[2],
            "status": r[3]
        }
        for r in rows
    ]

# =================================================
# USER HELPERS
# =================================================
def get_complaints_by_user(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            c.complaint_id,
            c.english_text,
            c.original_input,
            c.department,
            c.priority,
            c.status,
            c.created_at,
            dr.response_text,
            c.previous_responses
        FROM complaints c
        LEFT JOIN department_response dr
            ON c.complaint_id = dr.complaint_id
        WHERE c.user_id = %s
        ORDER BY c.complaint_id DESC;
        """,
        (user_id,)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "complaint_id": r[0],
            "english_text": r[1],
            "original_input": r[2],
            "department": r[3],
            "priority": r[4],
            "status": r[5],
            "created_at": r[6],
            "admin_response": r[7],
            "previous_responses": r[8] or []
        }
        for r in rows
    ]
