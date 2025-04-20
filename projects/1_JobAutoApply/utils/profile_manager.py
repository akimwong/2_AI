# utils/profile_manager.py

import json
import os
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

# Configurar embeddings y Pinecone
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "profile-index"

# Crear el índice si no existe
if index_name not in pc.list_indexes().names():
    print(f"Creando índice '{index_name}' en Pinecone...")
    pc.create_index(
        name=index_name,
        dimension=1536,  # Dimensión de los embeddings (depende del modelo de OpenAI)
        metric="cosine",  # Métrica de similitud
        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
    )

# Obtener el índice
index = pc.Index(index_name)

def load_profile(filename):
    """
    Carga el perfil profesional desde un archivo JSON.
    :param filename: Nombre del archivo JSON (por ejemplo, "profile_eng.json").
    :return: Diccionario con el perfil profesional.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error al cargar el perfil desde {filename}: {e}")
        return {}


def create_documents_from_profile(profile, language):
    documents = []

    # Habilidades (skills)
    for category in ["data", "telecom"]:
        for skill in profile["skills"][category]:
            documents.append(Document(
                page_content=f"Skill: {skill}",
                metadata={
                    "type": "skill",
                    "category": category,
                    "text": f"Skill: {skill}",
                    "language": language
                }
            ))

    # Experiencia laboral (experience)
    for experience in profile["experience"]:
        # Handle description which could be string or list
        description = experience["description"]
        if isinstance(description, list):
            description_str = " ".join(description)
        else:
            description_str = description

        # Convertir cada logro (dict) en un string formateado
        achievements_str_list = []
        for ach in experience["key_achievements"]:
            metrics_str = ", ".join(ach["metrics"])
            achievement_text = (
                f"Title: {ach['title']}\n"
                f"Context: {ach['context']}\n"
                f"Action: {ach['action']}\n"
                f"Result: {ach['result']}\n"
                f"Metrics: {metrics_str}\n"
                f"Year: {ach['year']}"
            )
            achievements_str_list.append(achievement_text)

        achievements_str = "\n\n".join(achievements_str_list)

        # Construir el contenido final para esta experiencia
        page_content = (
            f"Role: {experience['role']}\n"
            f"Company: {experience['company']}\n"
            f"Period: {experience['period']}\n"
            f"Description: {description_str}\n"
            f"Key Achievements:\n{achievements_str}"
        )

        documents.append(Document(
            page_content=page_content,
            metadata={
                "type": "experience",
                "text": f"Role: {experience['role']}",
                "language": language
            }
        ))

    # Educación (education) - now simple strings
    for education in profile["education"]:
        documents.append(Document(
            page_content=f"Education: {education}",
            metadata={
                "type": "education",
                "text": f"Education: {education}",
                "language": language
            }
        ))

    # Certificaciones (certifications) - now simple strings
    for certification in profile["certifications"]:
        documents.append(Document(
            page_content=f"Certification: {certification}",
            metadata={
                "type": "certification",
                "text": f"Certification: {certification}",
                "language": language
            }
        ))

    # Idiomas (languages) - now simple strings
    for language_item in profile["languages"]:
        documents.append(Document(
            page_content=f"Language: {language_item}",
            metadata={
                "type": "language",
                "text": f"Language: {language_item}",
                "language": language
            }
        ))
    return documents

def upload_profile_to_pinecone(profile, language):
    """Sube el perfil a Pinecone."""
    documents = create_documents_from_profile(profile, language)
    for i, doc in enumerate(documents):
        embedding = embeddings.embed_query(doc.page_content)
        index.upsert(
            vectors=[{
                "id": f"{language}-{i}",  # ID único (por ejemplo, "eng-0", "esp-1")
                "values": embedding,
                "metadata": doc.metadata
            }]
        )
    print(f"Perfil en {language} cargado en Pinecone.")

def initialize_profiles():
    """
    Carga los perfiles en inglés y español y los sube a Pinecone.
    """
    profile_eng = load_profile("profile_eng.json")
    profile_esp = load_profile("profile_esp.json")
    if profile_eng:
        upload_profile_to_pinecone(profile_eng, "eng")
    if profile_esp:
        upload_profile_to_pinecone(profile_esp, "esp")

# Ejecutar la inicialización de perfiles al importar este módulo
#initialize_profiles()