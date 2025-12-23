import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# -------------------------------------------------
# Database connection helper
# -------------------------------------------------
def get_connection():
    return psycopg2.connect(
        dbname="grievance_db",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        host="localhost",
        port="5432"
    )

# -------------------------------------------------
# 1️⃣ INSERT NEW COMPLAINT (Intake Agent)
# -------------------------------------------------
def save_complaint(original_input, english_text, input_type, language):
    """
    Inserts a new complaint into the complaints table
    and returns the generated complaint_id
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO complaints
        (original_input, english_text, input_type, language, status, created_at)
        VALUES (%s, %s, %s, %s, 'OPEN', NOW())
        RETURNING complaint_id;
        """,
        (original_input, english_text, input_type, language)
    )

    complaint_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return complaint_id

# -------------------------------------------------
# 2️⃣ UPDATE CLASSIFICATION (After Classifier Agent)
# -------------------------------------------------
def update_complaint_classification(complaint_id, department, priority):
    """
    Updates department, priority, and status
    for an existing complaint
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE complaints
        SET
            department = %s,
            priority = %s,
            status = 'IN_PROGRESS'
        WHERE complaint_id = %s;
        """,
        (department, priority, complaint_id)
    )

    conn.commit()
    cur.close()
    conn.close()

# -------------------------------------------------
# 3️⃣ INSERT DEPARTMENT RESPONSE
# -------------------------------------------------
def save_department_response(complaint_id, department, response_text):
    """
    Stores the department's response linked to the complaint
    and marks the complaint as RESOLVED
    """
    conn = get_connection()
    cur = conn.cursor()

    # Insert department response
    cur.execute(
        """
        INSERT INTO department_response
        (complaint_id, department, response_text, status, responded_at)
        VALUES (%s, %s, %s, 'RESPONDED', NOW());
        """,
        (complaint_id, department, response_text)
    )

    # 🔴 THIS WAS MISSING
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
