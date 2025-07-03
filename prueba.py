from descripciones.gestor_descripciones import GestorDescripciones
from db_manager import DBManager

prompt = (
    "Visually analyze the person in the image and generate a detailed description, "
    "structured into clear sections. Use bold titles followed by bullet point lists. "
    "The sections should include:\n\n"
    "**General Appearance**, **Face**, **Hair**, **Clothing**, **Accessories**, "
    "**Posture**, **Actions**, **Environment**, **Other Details**.\n\n"
    "Be clear and avoid repeating the same information in multiple sections. Use a clean and professional style."
)

estructura = {
    "ID": "INT PRIMARY KEY",
    "Imagen_cuerpo": "VARCHAR(50)",
    "Imagen_cara": "VARCHAR(50)",
    "Descripcion": "TEXT",
    "Fecha_registro": "DATETIME"
}

db = DBManager("registro_personas", estructura)
gestor_descripciones = GestorDescripciones(prompt, db)

gestor_descripciones.describir_con_coglvm("Personas_Detectadas\persona_1\Cuerpo\Cuerpo_1_2025-07-03_12-18-55-045167.jpg", 1, prompt)