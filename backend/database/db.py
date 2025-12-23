# import os
# import psycopg2
from dotenv import load_dotenv

# load_dotenv()

# conn = psycopg2.connect(
#     dbname="grievance_db",
#     user="postgres",
#     password=os.getenv("DB_PASSWORD"),
#     host="localhost",
#     port="5432"
# )

# def save_complaint(original_input, english_text, input_type, language):
#     cur = conn.cursor()
#     cur.execute(
#         """
#         INSERT INTO complaints
#         (original_input, english_text, input_type, language, status)
#         VALUES (%s, %s, %s, %s, 'PENDING')
#         """,
#         (original_input, english_text, input_type, language)
#     )
#     conn.commit()
#     cur.close()



# if __name__ == "__main__":
#     print("DB connected successfully")
def save_complaint(original, english, input_type, language):
    print("[DB MOCK] Complaint saved")
    print(f"Original: {original}")
    print(f"English: {english}")
    print(f"Type: {input_type}, Language: {language}")
