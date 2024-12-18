import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from certificate_generator import generate_certificate
from database_manager import store_certificate_data, initialize_database
from datetime import datetime

initialize_database()

def select_file(label):
    """Opens a file dialog and updates the label with the selected file path."""
    file_path = filedialog.askopenfilename()
    if file_path:
        label.config(text=file_path)

def select_folder(label):
    """Opens a folder dialog and updates the label with the selected folder path."""
    folder_path = filedialog.askdirectory()
    if folder_path:
        label.config(text=folder_path)

def clear_all_fields():
    """Clears all the input fields and resets the labels."""
    names_input.delete("1.0", tk.END)
    course_name_input.delete(0, tk.END)
    date_place_input.delete(0, tk.END)
    course_details_input.delete(0, tk.END)
    coordinator_name_input.delete(0, tk.END)
    coordinator_title_input.delete(0, tk.END)
    director_name_input.delete(0, tk.END)
    director_title_input.delete(0, tk.END)
    description_text_input.delete("1.0", tk.END)
    objective_text_input.delete("1.0", tk.END)
    study_plan_input.delete("1.0", tk.END)
    codigo_curso_input.delete(0, tk.END)
    template_label.config(text="Click to select file")
    template_second_label.config(text="Click to select file")
    coordinator_signature_label.config(text="Click to select file")
    director_signature_label.config(text="Click to select file")
    output_folder_label.config(text="Click to select folder")

from datetime import datetime

def generate_certificates_gui():
    # Get user inputs
    names = names_input.get("1.0", tk.END).strip().split("\n")
    course_name = course_name_input.get()
    date_place = date_place_input.get()
    course_details = course_details_input.get()
    coordinator_name = coordinator_name_input.get()
    coordinator_title = coordinator_title_input.get()
    director_name = director_name_input.get()
    director_title = director_title_input.get()
    description_text = description_text_input.get("1.0", tk.END).strip()
    objective_text = objective_text_input.get("1.0", tk.END).strip()
    study_plan_items = study_plan_input.get("1.0", tk.END).strip().split("\n")
    codigo_curso = codigo_curso_input.get()

    template_image = template_label.cget("text")
    template_second_image = template_second_label.cget("text")
    signature_coordinator = coordinator_signature_label.cget("text")
    signature_director = director_signature_label.cget("text")
    output_folder = output_folder_label.cget("text")

    if not all([template_image, template_second_image, signature_coordinator, signature_director, output_folder]):
        messagebox.showerror("Error", "All file paths and output folder must be selected!")
        return

    signature_images = {
        "coordinator": signature_coordinator,
        "director": signature_director
    }

    # Generate certificates and store in DB
    for i, name in enumerate(names, start=1):
        participant_id = f"{codigo_curso}-{i:03d}"
        output_file = f"{output_folder}/{name.replace(' ', '_')}_certificate.pdf"

        # Generate the certificate
        generate_certificate(
            name=name,
            course_name=course_name,
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

        # Store details in the database
        store_certificate_data(
            participant_name=name,
            course_name=course_name,
            date_of_course=datetime.now().date(),
            participant_id=participant_id,
            certificate_path=output_file
        )

    messagebox.showinfo("Success", "Certificates have been generated and stored in the database!")


# Main GUI
root = tk.Tk()
root.title("Certificate Generator")

# Main Frame with grid layout
main_frame = tk.Frame(root)
main_frame.pack(pady=20, padx=20)

# General Information Section
tk.Label(main_frame, text="Names (one per line):").grid(row=0, column=0, sticky="w", pady=5, padx=10)
names_input = tk.Text(main_frame, height=5, width=40)
names_input.grid(row=1, column=0, pady=5, padx=10)

tk.Label(main_frame, text="Course Name:").grid(row=0, column=1, sticky="w", pady=5, padx=10)
course_name_input = tk.Entry(main_frame, width=40)
course_name_input.grid(row=1, column=1, pady=5, padx=10)

tk.Label(main_frame, text="Date and Place:").grid(row=2, column=0, sticky="w", pady=5, padx=10)
date_place_input = tk.Entry(main_frame, width=40)
date_place_input.grid(row=3, column=0, pady=5, padx=10)

tk.Label(main_frame, text="Course Details:").grid(row=2, column=1, sticky="w", pady=5, padx=10)
course_details_input = tk.Entry(main_frame, width=40)
course_details_input.grid(row=3, column=1, pady=5, padx=10)

# Coordinator and Director Information
tk.Label(main_frame, text="Coordinator Name:").grid(row=4, column=0, sticky="w", pady=5, padx=10)
coordinator_name_input = tk.Entry(main_frame, width=40)
coordinator_name_input.grid(row=5, column=0, pady=5, padx=10)

tk.Label(main_frame, text="Coordinator Title:").grid(row=4, column=1, sticky="w", pady=5, padx=10)
coordinator_title_input = tk.Entry(main_frame, width=40)
coordinator_title_input.grid(row=5, column=1, pady=5, padx=10)

tk.Label(main_frame, text="Director Name:").grid(row=6, column=0, sticky="w", pady=5, padx=10)
director_name_input = tk.Entry(main_frame, width=40)
director_name_input.grid(row=7, column=0, pady=5, padx=10)

tk.Label(main_frame, text="Director Title:").grid(row=6, column=1, sticky="w", pady=5, padx=10)
director_title_input = tk.Entry(main_frame, width=40)
director_title_input.grid(row=7, column=1, pady=5, padx=10)

# Description and Objective Sections
tk.Label(main_frame, text="Description Text:").grid(row=8, column=0, sticky="w", pady=5, padx=10)
description_text_input = tk.Text(main_frame, height=5, width=40)
description_text_input.grid(row=9, column=0, pady=5, padx=10)

tk.Label(main_frame, text="Objective Text:").grid(row=8, column=1, sticky="w", pady=5, padx=10)
objective_text_input = tk.Text(main_frame, height=5, width=40)
objective_text_input.grid(row=9, column=1, pady=5, padx=10)

# Study Plan Section
tk.Label(main_frame, text="Study Plan Items (one per line):").grid(row=10, column=0, sticky="w", pady=5, padx=10)
study_plan_input = tk.Text(main_frame, height=5, width=40)
study_plan_input.grid(row=11, column=0, pady=5, padx=10)

tk.Label(main_frame, text="Course Code:").grid(row=10, column=1, sticky="w", pady=5, padx=10)
codigo_curso_input = tk.Entry(main_frame, width=40)
codigo_curso_input.grid(row=11, column=1, pady=5, padx=10)

# File Selection Sections
tk.Label(main_frame, text="Certificate Template:").grid(row=12, column=0, sticky="w", pady=5, padx=10)
template_label = ttk.Label(main_frame, text="Click to select file", relief="ridge", width=40)
template_label.grid(row=13, column=0, pady=5, padx=10)
template_label.bind("<Button-1>", lambda e: select_file(template_label))

tk.Label(main_frame, text="Second Page Template:").grid(row=12, column=1, sticky="w", pady=5, padx=10)
template_second_label = ttk.Label(main_frame, text="Click to select file", relief="ridge", width=40)
template_second_label.grid(row=13, column=1, pady=5, padx=10)
template_second_label.bind("<Button-1>", lambda e: select_file(template_second_label))

tk.Label(main_frame, text="Coordinator Signature:").grid(row=14, column=0, sticky="w", pady=5, padx=10)
coordinator_signature_label = ttk.Label(main_frame, text="Click to select file", relief="ridge", width=40)
coordinator_signature_label.grid(row=15, column=0, pady=5, padx=10)
coordinator_signature_label.bind("<Button-1>", lambda e: select_file(coordinator_signature_label))

tk.Label(main_frame, text="Director Signature:").grid(row=14, column=1, sticky="w", pady=5, padx=10)
director_signature_label = ttk.Label(main_frame, text="Click to select file", relief="ridge", width=40)
director_signature_label.grid(row=15, column=1, pady=5, padx=10)
director_signature_label.bind("<Button-1>", lambda e: select_file(director_signature_label))

tk.Label(main_frame, text="Output Folder:").grid(row=16, column=0, sticky="w", pady=5, padx=10)
output_folder_label = ttk.Label(main_frame, text="Click to select folder", relief="ridge", width=40)
output_folder_label.grid(row=17, column=0, pady=5, padx=10)
output_folder_label.bind("<Button-1>", lambda e: select_folder(output_folder_label))

# Generate and Clear Buttons
generate_button = tk.Button(main_frame, text="Generate Certificates", command=generate_certificates_gui)
generate_button.grid(row=17, column=1, pady=10, padx=10)

clear_button = tk.Button(main_frame, text="Clear All Fields", command=clear_all_fields)
clear_button.grid(row=16, column=1, pady=15, padx=10)

# Run the application


root.mainloop()
 