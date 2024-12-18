import tkinter as tk
from tkinter import messagebox
import psycopg2
from psycopg2 import sql
from verify_certificate import verify_certificate

# Database connection configuration
DB_CONFIG = {
    'dbname': 'certificates',    # Replace with your database name
    'user': 'postgres',            # Replace with your username
    'password': '0000',   # Replace with your password
    'host': 'localhost',           # Replace with your host
    'port': '5342',                # Replace with your port
}

def verify_certificate(certificate_code, result_label):
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
        
        # Execute the query
        cursor.execute(query, (certificate_code,))
        result = cursor.fetchone()

        # Debug: Print the query result
        print(f"Query Result: {result}")

        # Update the result label based on the query result
        if result:
            participant_name, course_name = result
            result_label.config(
                text=f"Certificate Found!\nParticipant: {participant_name}\nCourse: {course_name}",
                fg="green",
                font=("Arial", 12, "bold"),
            )
        else:
            result_label.config(
                text="Error: Certificate code does not exist.",
                fg="red",
                font=("Arial", 12, "bold"),
            )

    except Exception as e:
        messagebox.showerror("Database Error", f"Error connecting to database: {e}")
    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# GUI Application
def create_gui():
    root = tk.Tk()
    root.title("Certificate Verification")
    root.geometry("400x250")  # Set fixed window size

    # Title
    tk.Label(root, text="Certificate Verification", font=("Arial", 16, "bold")).pack(pady=10)

    # Certificate Code Input
    tk.Label(root, text="Enter Certificate Code (e.g., CPIAD202408-001):", font=("Arial", 10)).pack(pady=5)
    certificate_entry = tk.Entry(root, width=30, font=("Arial", 12))
    certificate_entry.pack(pady=5)

    # Result Label
    result_label = tk.Label(root, text="", font=("Arial", 12), wraplength=350)
    result_label.pack(pady=10)

    # Verify Button
    verify_button = tk.Button(
        root,
        text="Verify Certificate",
        font=("Arial", 12),
        command=lambda: verify_certificate(certificate_entry.get().strip(), result_label)
    )
    verify_button.pack(pady=10)
  
    # Run the GUI loop
    root.mainloop()

if __name__ == "__main__":
    
    create_gui()
