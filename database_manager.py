import psycopg2
from psycopg2 import sql

# Database configuration
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "0000",
    "host": "localhost",
    "port": "5433"
}

def connect_db():
    """Establishes a connection to the database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def insert_certificate(participant_name, course_name, date_of_course, participant_id, certificate_path):
    """
    Inserts a certificate record into the database.

    Parameters:
    - participant_name: Name of the participant.
    - course_name: Name of the course.
    - date_of_course: Date of the course.
    - participant_id: Unique participant ID.
    - certificate_path: Path to the generated PDF.
    """
    query = """
    INSERT INTO certificates (participant_name, course_name, date_of_course, participant_id, certificate_path)
    VALUES (%s, %s, %s, %s, %s)
    """
    try:
        conn = connect_db()
        if conn:
            with conn.cursor() as cur:
                cur.execute(query, (participant_name, course_name, date_of_course, participant_id, certificate_path))
            conn.commit()
            conn.close()
            print(f"Certificate for {participant_name} inserted into database.")
    except Exception as e:
        print(f"Error inserting data into database: {e}")
