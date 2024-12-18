from flask import Flask, request, render_template, redirect, url_for, session
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from certificate_generator import generate_certificate
from database_manager import insert_certificate
import os

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '0000',
    'host': 'localhost',
    'port': '5342'
}

from flask import request, redirect, render_template, url_for
import os
from werkzeug.utils import secure_filename

@app.route('/admin/generate_and_add_certificate', methods=['POST'])
def generate_and_add_certificate():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    try:
        # Collect form data
        participant_name = request.form['participant_name']
        course_name = request.form['course_name']
        date_place = request.form['date_place']
        course_details = request.form['course_details']
        coordinator_name = request.form['coordinator_name']
        coordinator_title = request.form['coordinator_title']
        director_name = request.form['director_name']
        director_title = request.form['director_title']
        description_text = request.form['description_text']
        objective_text = request.form['objective_text']
        study_plan_items = request.form['study_plan_items'].splitlines()
        codigo_curso = request.form['codigo_curso']

        # File uploads
        template_image = request.files['template_image']
        template_second_image = request.files['template_second_image']
        coordinator_signature = request.files['coordinator_signature']
        director_signature = request.files['director_signature']
        output_folder = request.form['output_folder']

        # Save files to a temporary directory
        temp_dir = os.path.join(os.getcwd(), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)

        template_image_path = os.path.join(temp_dir, secure_filename(template_image.filename))
        template_second_image_path = os.path.join(temp_dir, secure_filename(template_second_image.filename))
        coordinator_signature_path = os.path.join(temp_dir, secure_filename(coordinator_signature.filename))
        director_signature_path = os.path.join(temp_dir, secure_filename(director_signature.filename))

        template_image.save(template_image_path)
        template_second_image.save(template_second_image_path)
        coordinator_signature.save(coordinator_signature_path)
        director_signature.save(director_signature_path)

        # Generate Certificates
        participant_names = participant_name.split("\n")
        for i, name in enumerate(participant_names, start=1):
            # Clean participant name
            clean_name = name.strip().replace("\r", "").replace("\n", "").replace(" ", "_")
            
            participant_id = f"{codigo_curso}-{i:03d}"
            output_file = os.path.join(output_folder, f"{clean_name}_certificate.pdf")

            # Call certificate generator
            generate_certificate(
                name=name.strip(),
                course_name=course_name,
                date_place=date_place,
                course_details=course_details,
                coordinator_name=coordinator_name,
                coordinator_title=coordinator_title,
                director_name=director_name,
                director_title=director_title,
                signature_images={"coordinator": coordinator_signature_path, "director": director_signature_path},
                output_file=output_file,
                template_image=template_image_path,
                template_second_image=template_second_image_path,
                description_text=description_text,
                objective_text=objective_text,
                study_plan_items=study_plan_items,
                codigo_curso=codigo_curso,
                participant_number=i
            )


            # Store in database
            insert_certificate(
                participant_name=name,
                course_name=course_name,
                date_of_course=date_place,
                participant_id=participant_id,
                certificate_path=output_file
            )

        return redirect(url_for('admin_dashboard'))

    except Exception as e:
        return render_template('admin_dashboard.html', message=f"Error generating certificates: {e}")


@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = None
    cursor = None
    try:
        # Fetch all certificates
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT participant_id, participant_name, course_name FROM certificates")
        certificates = cursor.fetchall()

        return render_template('admin_dashboard.html', certificates=certificates)
    except Exception as e:
        return render_template('admin_dashboard.html', message=f"Database Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Fetch admin user
            cursor.execute("SELECT password_hash FROM admin_users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[0], password):
                session['admin'] = username
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template('admin_login.html', message="Invalid credentials.")
        except Exception as e:
            return render_template('admin_login.html', message=f"Database Error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('admin_login.html')

# Admin Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

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

app.secret_key = 'verySecret'

if __name__ == '__main__':
    app.run(debug=True)
    app.secret_key = 'verySecret'

