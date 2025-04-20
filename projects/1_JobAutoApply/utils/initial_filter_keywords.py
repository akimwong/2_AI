# utils/initial_filter_keywords.py

import re

# Lista de palabras clave para el filtrado inicial (título)
rejected_titles = [
    "junior",  # Ejemplo: descartar ofertas que contengan "Junior"
    "intern",  # Ejemplo: descartar ofertas que contengan "Intern"
    "trainee",  # Ejemplo: descartar ofertas que contengan "Trainee"
    "student",
    "marketing",
    "director",
    "beca",
    "senior",
    "Ciberseguridad",
    "Cybersecurity",
    "Presales",
]

# Lista de ubicaciones aceptadas
accepted_locations_ = [
    "madrid",  # Aceptar ofertas en Madrid
    "unión europea",  # Aceptar ofertas en la Unión Europea
    "european union",
    "ue",  # Aceptar ofertas en la UE (abreviatura)
    #"spain",  # Aceptar ofertas en España
    #"españa",  # Equivalente en español
]

# Lista de ubicaciones aceptadas con regex
accepted_locations_x = [
    r"\bmadrid\b",  # Aceptar "madrid" como palabra completa
    r"\bunión europea\b",  # Aceptar "unión europea" como frase completa
    r"\beuropean union\b",  # Aceptar "european union" como frase completa
    r"\bue\b",  # Aceptar "ue" como palabra completa
    r"(^|\W)spain($|\W)",  # Aceptar "spain" como palabra completa
    r"(^|\W)españa($|\W)",  # Aceptar "españa" como palabra completa
]

# Lista de títulos aceptados (por ejemplo, "Data analyst")
accepted_titles = [
    "data analyst",  # Aceptar ofertas con este título
    "analista de datos",  # Equivalente en español
    "data visualization",
    "artificial intelligence",
    "inteligencia artificial",
    "ai",
    "genai",
    "generative ai",
    "data scientist",
    "machine learning",
    "científico de datos",
    "project manager",
    "ftth",
    "fibra óptica",
    "fiber optic",
    "telecomunicaciones",
    "telecommunications",
]

# Lista de palabras clave positivas (si aparecen en el título o descripción, la oferta es aceptada)
positive_keywords = [
    "data analyst",  # Palabra clave positiva
    "analista de datos",  # Equivalente en español
    "python",  # Otra palabra clave positiva
    "sql",  # Otra palabra clave positiva
    "data visualization",
    "ftth",
    "fibra óptica",
    "fiber optic",
    "telecomunicaciones",
    "telecommunications",
]