import psycopg2
from psycopg2 import sql
import os

# Database connection configuration
DB_CONFIG = {
    'dbname': 'postgres',    # Replace with your database name
    'user': 'postgres',            # Replace with your username
    'password': '0000',   # Replace with your password
    'host': 'localhost',           # Replace with your host
    'port': '5342',                # Replace with your port
}

def verify_certificate(certificate_code):
    """Check if a certificate code exists in the database."""
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Query to search for the certificate code
        query = sql.SQL("""
            SELECT participant_name, course_name
            FROM certificates
            WHERE participant_id = %s
        """)
        
        # Debugging: Show what is being queried
        # print(f"DEBUG: Searching for participant_id: {certificate_code}")
        
        # Execute the query
        cursor.execute(query, (certificate_code,))
        result = cursor.fetchone()
        
        # Check if a result was found
        if result:
            participant_name, course_name = result
            print("\nCertificate Found!")
            print(f"Participant Name: {participant_name}")
            print(f"Course Name: {course_name}")
        else:
            print("\nError: Certificate code does not exist.")
    
    except Exception as e:
        print(f"\nDatabase Error: {e}")
    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    # Ask the user to input a certificate code
    certificate_code = input("Enter the Certificate Code (e.g., CPIAD202408-001): ").strip()
    verify_certificate(certificate_code)