import zipfile
import tempfile
from flask import Flask, request, render_template, redirect, url_for, session, send_file
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import os
from certificate_generator import generate_certificate
from database_manager import insert_certificate
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '0000',
    'host': 'localhost',
    'port': '5433'
}

app.secret_key = 'verySecret'

# First page (Login/Register)
@app.route('/', methods=['GET'])
def first_page():
    return render_template('first_page.html')

# Admin Registration
@app.route('/admin/register', methods=['POST'])
def admin_register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    hashed_password = generate_password_hash(password)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Insert new admin user into the database
        cursor.execute("""
            INSERT INTO admin_users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (username, email, hashed_password))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('first_page', message="Registration successful! Please log in."))

    except psycopg2.Error as e:
        return render_template('first_page.html', message=f"Error: {e}")

# Admin Login
@app.route('/admin/login', methods=['POST'])
def admin_login():
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
            return render_template('first_page.html', message="Invalid credentials.")
    except Exception as e:
        return render_template('first_page.html', message=f"Database Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Admin Dashboard
@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('first_page'))

    return render_template('admin_dashboard.html')

@app.route('/admin/verify', methods=['GET', 'POST'])
def verify_certificate():
    if request.method == 'POST':
        code = request.form['certificate_code']
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Query database for certificate
            cursor.execute("SELECT participant_name, course_name FROM certificates WHERE participant_id = %s", (code,))
            result = cursor.fetchone()

            if result:
                return render_template("verify_certificate.html", message=f"Valid Certificate! Name: {result[0]}, Course: {result[1]}")
            else:
                return render_template("verify_certificate.html", message="Invalid Certificate Code.")

        except Exception as e:
            return render_template("verify_certificate.html", message=f"Database Error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    return render_template("verify_certificate.html", message=None)

@app.route('/admin/create_certificate', methods=['GET'])
def admin_create_certificate():
    if 'admin' not in session:
        return redirect(url_for('first_page'))
    return render_template('admin_create_certificate.html')

@app.route('/admin/view_certificates', methods=['GET'])
def admin_view_certificates():
    if 'admin' not in session:
        return redirect(url_for('first_page'))

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Fetch all certificates
        cursor.execute("SELECT participant_id, participant_name, course_name, certificate_path FROM certificates")
        certificates = cursor.fetchall()

        return render_template('admin_view_certificates.html', certificates=certificates)

    except Exception as e:
        return render_template('admin_dashboard.html', message=f"Database Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/admin/download_certificate')
def download_certificate():
    if 'admin' not in session:
        return redirect(url_for('first_page'))

    cert_path = request.args.get('cert_path')

    if cert_path and os.path.exists(cert_path):
        return send_file(cert_path, as_attachment=True)
    else:
        return render_template('admin_view_certificates.html', message="Error: Certificate not found.")


# Admin Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('first_page'))

@app.route('/admin/generate_and_add_certificate', methods=['POST'])
def generate_and_add_certificate():
    if 'admin' not in session:
        return redirect(url_for('first_page'))

    try:
        # Collect form data
        participant_names = request.form['participant_name'].strip().split("\n")  # Split multiple names
        course_name = request.form['course_name']
        date_place = request.form['date_place']
        course_details = request.form['course_details']
        coordinator_name = request.form['coordinator_name']
        coordinator_title = request.form['coordinator_title']
        director_name = request.form['director_name']
        director_title = request.form['director_title']
        description_text = request.form['description_text']
        objective_text = request.form['objective_text']
        study_plan_items = request.form['study_plan_items'].strip().split("\n")
        codigo_curso = request.form['codigo_curso']

        # File uploads
        template_image = request.files['template_image']
        template_second_image = request.files['template_second_image']
        coordinator_signature = request.files['coordinator_signature']
        director_signature = request.files['director_signature']

        # Save files temporarily
        temp_dir = tempfile.mkdtemp()

        template_image_path = os.path.join(temp_dir, secure_filename(template_image.filename))
        template_second_image_path = os.path.join(temp_dir, secure_filename(template_second_image.filename))
        coordinator_signature_path = os.path.join(temp_dir, secure_filename(coordinator_signature.filename))
        director_signature_path = os.path.join(temp_dir, secure_filename(director_signature.filename))

        template_image.save(template_image_path)
        template_second_image.save(template_second_image_path)
        coordinator_signature.save(coordinator_signature_path)
        director_signature.save(director_signature_path)

        # Generate certificates
        generated_files = []
        for i, name in enumerate(participant_names, start=1):
            clean_name = name.strip().replace("\r", "").replace("\n", "").replace(" ", "_")  # Sanitize filename
            participant_id = f"{codigo_curso}-{i:03d}"
            output_file = os.path.join(temp_dir, f"{clean_name}_certificate.pdf")

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

            insert_certificate(
                participant_name=name.strip(),
                course_name=course_name,
                date_of_course=date_place,
                participant_id=participant_id,
                certificate_path=output_file
            )

            generated_files.append(output_file)

        # Create ZIP file
        zip_path = os.path.join(temp_dir, f"certificates_{codigo_curso}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in generated_files:
                zipf.write(file, os.path.basename(file))

        # Send ZIP file for download
        return send_file(zip_path, as_attachment=True, mimetype='application/zip')

    except Exception as e:
        return render_template('admin_create_certificate.html', message=f"Error generating certificates: {e}")
    except Exception as e:
        return render_template('admin_create_certificate.html', message=f"Error generating certificate: {e}")

    except Exception as e:
        return render_template('admin_create_certificate.html', message=f"Error generating certificate: {e}")

    except Exception as e:
        return render_template('admin_dashboard.html', message=f"Error generating certificates: {e}")

if __name__ == '__main__':
    app.run(debug=True)
