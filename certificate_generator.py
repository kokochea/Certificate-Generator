from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PIL import Image as PILImage
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

# ==============================
# Font and Color Configuration
# ==============================
pdfmetrics.registerFont(TTFont("Belleza", "Belleza-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Montserrat", "FontsFree-Net-Montserrat-Medium.ttf"))
pdfmetrics.registerFont(TTFont("Open-Sans", "OpenSans-VariableFont_wdth,wght.ttf"))
pdfmetrics.registerFont(TTFont("Futura", "futura-heavy.ttf"))

# Colors
azulCPI = colors.HexColor("#093979")
amarilloCPI = colors.HexColor("#ab7f28")
text_color = colors.black

# ==============================
# Helper Functions
# ==============================
def get_scaled_dimensions(image_path, max_width, max_height):
    """Scales the image to fit within specified dimensions while maintaining the aspect ratio."""
    with PILImage.open(image_path) as img:
        original_width, original_height = img.size
        aspect_ratio = original_width / original_height

        if original_width > max_width or original_height > max_height:
            if aspect_ratio > 1:
                return max_width, max_width / aspect_ratio
            else:
                return max_height * aspect_ratio, max_height
        return original_width, original_height

# ==============================
# Page Generation
# ==============================
def generate_second_page(c, width, height, description_text, objective_text, study_plan_items, codigo_curso, participant_number):
    """Generates the second page of the certificate."""
    # Styles for sections
    styles = getSampleStyleSheet()
    description_style = ParagraphStyle(
        name="DescriptionStyle",
        parent=styles["Normal"],
        fontName="Open-Sans",
        fontSize=15,
        textColor=colors.black,
        leading=20,
        alignment=0
    )
    modules_style = ParagraphStyle(
        name="ModulesStyle",
        parent=styles["Normal"],
        fontName="Open-Sans",
        fontSize=15,
        textColor=azulCPI,
        leading=20,
        alignment=0
    )

    # Spacing
    section_spacing = 20
    max_text_box_height = height - 200

    # Description Section
    description_paragraph = Paragraph(
        f'''<font face="Futura" color="#ab7f28" size=18>Descripción capacitación</font><BR/>{description_text}''',
        description_style
    )
    w, h = description_paragraph.wrap(width - 200, max_text_box_height)
    description_paragraph.drawOn(c, 50, height - 70 - h)
    y_position = height - 70 - h - section_spacing

    # Objective Section
    objective_paragraph = Paragraph(
        f'''<font face="Futura" color="#ab7f28" size=18>Objetivo general de la capacitación</font><BR/>{objective_text}''',
        description_style
    )
    w, h = objective_paragraph.wrap(width - 200, max_text_box_height)
    objective_paragraph.drawOn(c, 50, y_position - h)
    y_position -= h + section_spacing

    # # Study Plan Section
    # study_plan_title = Paragraph(
    #     f'''<font face="Futura" color="#ab7f28" size=18>Plan de estudios</font>''',
    #     description_style
    # )
    # w, h = study_plan_title.wrap(width - 200, max_text_box_height)
    # study_plan_title.drawOn(c, 50, y_position - h)
    # y_position -= h + 10

    # for item in study_plan_items:
    #     item_paragraph = Paragraph(f"• {item}", modules_style)
    #     w, h = item_paragraph.wrap(width - 200, max_text_box_height)
    #     item_paragraph.drawOn(c, 50, y_position - h)
    #     y_position -= h + 2

    # Certificate Code
    certificate_code = f"Código certificado: {codigo_curso}-{participant_number:03d}"
    c.setFont("Futura", 17)
    c.setFillColor(azulCPI)
    c.drawRightString(width - 60, 90, certificate_code)


def generate_certificate(name, course_name, date_place, course_details, coordinator_name, coordinator_title, director_name, director_title, signature_images, output_file, template_image, template_second_image, description_text, objective_text, study_plan_items, codigo_curso, participant_number):
    """Generates the complete certificate with both pages."""
    c = canvas.Canvas(output_file, pagesize=landscape(A4))
    width, height = landscape(A4)

    # First Page
    c.drawImage(template_image, 0, 0, width=width, height=height)

    # Main Content
    c.setFont("Open-Sans", 19)
    c.setFillColor(text_color)
    c.drawCentredString(width / 2, height - 150, "Otorga el presente certificado a")

    c.setFont("Belleza", 66)
    c.setFillColor(azulCPI)
    c.drawCentredString(width / 2, height - 220, name)

    c.setFont("Open-Sans", 25)
    c.setFillColor(text_color)
    c.drawCentredString(width / 2, height - 270, "por haber aprobado el")

    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(azulCPI)
    c.drawCentredString(width / 2, height - 320, course_name)

    # Footer Details
    c.setFont("Montserrat", 15)
    c.setFillColor(amarilloCPI)
    c.drawCentredString(width / 2, height - 380, date_place)

    c.setFont("Futura", 15)
    c.setFillColor(azulCPI)
    c.drawCentredString(width / 2, height - 400, course_details)

    # Signatures
    # if signature_images.get("coordinator"):
    #     max_width, max_height = 150, 65
    #     scaled_width, scaled_height = get_scaled_dimensions(signature_images["coordinator"], max_width, max_height)
    #     c.drawImage(signature_images["coordinator"], 200 - (scaled_width / 2), 90, width=scaled_width, height=scaled_height)
    if signature_images.get("director"):
        max_width, max_height = 150, 65
        scaled_width, scaled_height = get_scaled_dimensions(signature_images["director"], max_width, max_height)
        c.drawImage(signature_images["director"], width/2 - (scaled_width / 2), 90, width=scaled_width, height=scaled_height)

    # # Left signature
    # c.setFont("Helvetica-Bold", 15)
    # c.setFillColor(amarilloCPI)
    # c.drawCentredString(200, 100, "_________________________")
    # c.setFont("Belleza", 19)
    # c.setFillColor(text_color)
    # c.drawCentredString(200, 77, coordinator_name)
    # c.setFont("Open-Sans", 9)
    # c.setFillColor(amarilloCPI)
    # c.drawString(155, 60, coordinator_title)

    # Right signature
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(amarilloCPI)
    c.drawCentredString(width/2, 100, "_________________________")
    c.setFont("Belleza", 19)
    c.setFillColor(text_color)
    c.drawCentredString(width/2, 77, director_name)
    c.setFont("Open-Sans", 9)
    c.setFillColor(amarilloCPI)
    c.drawCentredString(width/2, 60, director_title)

    # Finalize First Page
    c.showPage()

    # Second Page
    c.drawImage(template_second_image, 0, 0, width=width, height=height)
    generate_second_page(c, width, height, description_text, objective_text, study_plan_items, codigo_curso, participant_number)

    # Save PDF
    c.save()

# ==============================
# Example Usage
# ==============================
# names = ["Pablo Estigarribia"]
# course = "Programa Ejecutivo en Ciberseguridad"
# date_place = "Montevideo, 6 de diciembre de 2024"
# course_details = "48 horas lectivas | Modalidad híbrida | CPI"
# coordinator_name = "Ing. Cristina Mayr"
# coordinator_title = "Coordinadora del Curso"
# director_name = "MBA Ing. Eduardo Carozo"
# director_title = "Director del Centro de Posgrados en Ingeniería"
# template_image = "assets\certificate_template.jpg"
# template_second_image = "assets\certificate_second_template.jpg"
# signature_images = {"coordinator": "assets\irmaCM.png", "director": "assets\irmaEC.jpg"}
# description_text = "Curso dictado en Montevideo, desde el 23 de agosto al 6 de diciembre de 2024 (48 horas) por el Centro de Posgrados en Ingeniería de la Universidad de Montevideo."
# objective_text = "Los participantes serán capaces de aplicar conocimientos fundacionales y avanzados sobre ciberseguridad en las organizaciones, diseñar estrategias basadas en los principales marcos y estándares existentes, realizar el seguimiento de su implementación, identificar puntos faltantes y analizar soluciones de defensa, además de evaluar y probar medidas de ciberseguridad de manera efectiva."
# study_plan_items = [
#     "Módulo 1: Contexto actual de ciberseguridad, ecosistema y superficie de ataque",
#     "Módulo 2: Amenazas de ciberseguridad e impacto en las organizaciones",
#     "Módulo 3: Definición de una estrategia de Ciberseguridad",
#     "Módulo 4: Roles, funciones y procesos de ciberseguridad",
#     "Módulo 5: Marcos y estándares de ciberseguridad (ISO, NIST, COBIT)",
#     "Módulo 6: Medidas de defensa de ciberseguridad",
#     "Módulo 7: Metodologías de evaluación y auditoría de situación de ciberseguridad",
#     "Módulo 8: Respuesta ante incidentes de ciberseguridad",
#     "Módulo 9: Privacidad de datos, regulaciones y estado del arte",
#     "Módulo 10: Conceptos de ciberseguridad en tecnologías emergentes: IA, Blockchain, IOT y el futuro de la ciberseguridad"
# ]
# codigo_curso = "CPIC202408"

# # Define the relative path to the "certificados" folder
# output_folder = os.path.join(os.getcwd(), "certificados")

# # Ensure the folder exists
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# # Generate certificates
# for i, name in enumerate(names, start=1 ):
#     # Define the output file path within the "certificados" folder
#     output_file = os.path.join(output_folder, f"{name.replace(' ', ' ')} - Programa Ejecutivo en Ciberseguridad.pdf")
    
#     # Call the certificate generation function
#     generate_certificate(
#         name, course, date_place, course_details,
#         coordinator_name, coordinator_title,
#         director_name, director_title,
#         signature_images, output_file,
#         template_image, template_second_image,
#         description_text, objective_text,
#         study_plan_items, codigo_curso, i
#     )
    
#     print(f"Certificate generated for {name}: {output_file}")

