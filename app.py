from flask import Flask, request, render_template
import psycopg2

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '0000',
    'host': 'localhost',
    'port': '5342'
}

# Verify Certificate Endpoint
@app.route('/', methods=['GET', 'POST'])
def verify_certificate():
    if request.method == 'POST':
        code = request.form['certificate_code']
        conn = None
        cursor = None
        try:
            # Connect to PostgreSQL
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Query database
            cursor.execute("SELECT participant_name, course_name FROM certificates WHERE participant_id = %s", (code,))
            result = cursor.fetchone()

            if result:
                return render_template("index.html", message=f"Valid Certificate! Name: {result[0]}, Course: {result[1]}")
            else:
                return render_template("index.html", message="Invalid Certificate Code.")

        except Exception as e:
            return render_template("index.html", message=f"Database Error: {e}")
        finally:
            # Close cursor and connection if they were initialized
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template("index.html", message=None)

if __name__ == '__main__':
    app.run(debug=True)
