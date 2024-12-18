from certificate_generator import generate_certificate
from database_manager import insert_certificate
import os

# Define test data
names = ["Pedro Perez", "Juan Rodriguez"]
course = "Actualización profesional en Analítica de Datos"
date_place = "Montevideo, 21 de noviembre de 2024"
course_details = "45 horas lectivas | Modalidad presencial | CPI"
coordinator_name = "Ing. Cristina Mayr"
coordinator_title = "Coordinadora del Curso"
director_name = "MBA Ing. Eduardo Carozo"
director_title = "Director del Centro de Posgrados en Ingeniería"

# Paths to assets
template_image = os.path.join("assets", "certificate_template.jpg")
template_second_image = os.path.join("assets", "certificate_second_template.jpg")
signature_images = {
    "coordinator": os.path.join("assets", "firmaCM.png"),
    "director": os.path.join("assets", "firmaEC.jpg")
}

# Additional text sections
description_text = "Curso dictado en Montevideo, desde el 8 de agosto al 21 de noviembre de 2024 (45 horas)."
objective_text = "Los participantes aplicarán herramientas y técnicas de análisis de datos."
study_plan_items = [
    "Módulo 1: Data Science",
    "Módulo 2: Bases de datos",
    "Módulo 3: Conceptos básicos de Big Data",
    "Módulo 4: Python y Big Data",
    "Módulo 5: Visualización para Business Intelligence",
    "Módulo 6: Tecnologías de IA"
]

# Output folder
output_folder = os.path.join(os.getcwd(), "certificados")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Course code prefix
codigo_curso = "CPIAD202408"

# Generate certificates and save to the database
for i, name in enumerate(names, start=1):
    participant_id = f"{codigo_curso}-{i:03d}"
    output_file = os.path.join(output_folder, f"{name.replace(' ', '_')}_certificate.pdf")

    # Generate the certificate
    generate_certificate(
        name=name,
        course_name=course,
        date_place=date_place,
        course_details=course_details,
        coordinator_name=coordinator_name,
        coordinator_title=coordinator_title,
        director_name=director_name,
        director_title=director_title,
        signature_images=signature_images,
        output_file=output_file,
        template_image=template_image,
        template_second_image=template_second_image,
        description_text=description_text,
        objective_text=objective_text,
        study_plan_items=study_plan_items,
        codigo_curso=codigo_curso,
        participant_number=i
    )

    print(f"Generated: {output_file}")

    # Insert into database
    insert_certificate(
        participant_name=name,
        course_name=course,
        date_of_course="2024-11-21",  # Static for this example
        participant_id=participant_id,
        certificate_path=output_file
    )
