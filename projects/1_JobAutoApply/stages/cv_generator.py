# stages/cv_generator.py

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from pinecone import Pinecone
from anthropic import Anthropic
from openai import OpenAI
import json
from pathlib import Path
import time

# Cargar variables del archivo .env
load_dotenv()

# Acceder a las claves API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Configurar embeddings y Pinecone
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "profile-index"

# Obtener el índice de Pinecone
index = pc.Index(index_name)

def generate_with_openai(prompt, cv_language="English", max_retries=3, delay=5, model="gpt-4"):
    """
    Genera texto usando modelos de OpenAI.
    :param prompt: Texto inicial para la generación
    :param cv_language: Idioma de respuesta ("English" o "Spanish")
    :param max_retries: Número máximo de reintentos
    :param delay: Segundos entre reintentos
    :param model: Modelo de OpenAI a usar (por defecto: gpt-4)
    :return: Respuesta generada o None en caso de error
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Configuración de idioma
    language_instruction = "Responde en inglés." if cv_language == "English" else "Responde en español."
    messages = [
        {
            "role": "system", 
            "content": f"Eres un especialista en recursos humanos. {language_instruction}"
        },
        {
            "role": "user", 
            "content": prompt
        }
    ]
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.01,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
                   
        except Exception as e:
            print(f"Error en intento {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Reintentando en {delay} segundos...")
                time.sleep(delay)
                
    print("Error: Fallo después de múltiples intentos")
    return None

def generate_with_claude(prompt, cv_language="English", max_retries=3, delay=5):
    """
    Genera texto usando Claude de Anthropic.
    :param prompt: El prompt para enviar a Claude.
    :param cv_language: Idioma en el que se debe generar el texto ("English" o "Spanish").
    :return: Respuesta generada por Claude.
    """
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    # Añadir una instrucción explícita sobre el idioma
    if cv_language == "English":
        language_instruction = "Please respond in English."
    else:
        language_instruction = "Por favor, responde en español."
    
    formatted_prompt = f"\n\nHuman: {prompt}\n{language_instruction}\n\nAssistant:"
    for attempt in range(max_retries):
        try:
            response = client.completions.create(
                prompt=formatted_prompt,
                model="claude-2",
                max_tokens_to_sample=500,
                temperature=0.01
            )
            return response.completion
        except Exception as e:
            print(f"Intento {attempt + 1} fallido. Reintentando en {delay} segundos... Error: {e}")
            time.sleep(delay)
    print("Error: No se pudo generar una respuesta después de varios intentos.")
    return None

def generate_with_deepseek(prompt):
    """
    Genera texto usando DeepSeek.
    :param prompt: El prompt para enviar a DeepSeek.
    :return: Respuesta generada por DeepSeek.
    """
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a human resources advisor."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.01,
        stream=False
    )
    return response.choices[0].message.content.strip()

def generate_cv_direct(job_offer, cv_language="English"):
    """
    Versión optimizada que:
    1. Carga el perfil JSON correspondiente
    2. Extrae palabras clave de la oferta
    3. Genera el CV usando datos estructurados del perfil
    """
    # 1. Determinar archivo de perfil según idioma
    profile_file = "profile_eng.json" if cv_language == "English" else "profile_esp.json"
    profile_path = Path(__file__).parent.parent / profile_file
    
    # 2. Cargar perfil
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
    except Exception as e:
        print(f"Error cargando perfil: {e}")
        return None

    # 3. Extraer palabras clave (versión optimizada)
    keywords, categoria = extract_keywords(job_offer)
    #keywords = extract_keywords(job_offer)
    #print("🔑 Palabras clave identificadas:", keywords)

    # 4. Generar CV con datos estructurados
    cv_prompt = build_cv_prompt(
        profile=profile, 
        job_offer=job_offer, 
        keywords=keywords, 
        lang=cv_language,
        categoria=categoria
    )
    #cv_claude = generate_with_claude(cv_prompt)
    #cv_openai = generate_with_openai(cv_prompt)
    cv_deepseek = generate_with_deepseek(cv_prompt)

    return {
        "keywords": keywords,
        #"claude": cv_claude,
        #"openai": cv_openai,
        "deepseek": cv_deepseek
    }

def extract_keywords(job_offer):
    """Extrae palabras clave técnicas y personales de forma eficiente"""
    prompt = (
        "Extrae SOLO las 20 principales habilidades (15 técnicas, 5 personales) de esta oferta:\n"
        f"Omite cualquier mención de beneficios, cultura de la empresa, compensaciones, salarios o detalles irrelevantes.\n"
        f"Puesto: {job_offer.get('title', '')}\n"
        f"Descripción: {job_offer.get('description', '')}"
        "Formato: lista separada por comas, sin explicaciones"
    )
    response = generate_with_deepseek(prompt)
    keywords = [kw.strip() for kw in response.split(",")][:20]

    title = job_offer.get('title', '').lower()
    prompt_clasificacion = (
        "Clasifica este título de puesto como 'data' o 'telecom'. Responde SOLO con 1 palabra.\n"
        f"Ejemplo 1: 'Data Analyst' → data\n"
        f"Ejemplo 2: 'Fiber Network Engineer' → telecom\n"
        f"Título a clasificar: {title}"
    )
    clasificacion = generate_with_deepseek(prompt_clasificacion).strip().lower()
    # Validación de respuesta
    categoria = 'data' if 'data' in clasificacion else 'telecom' if 'telecom' in clasificacion else 'data'
    return keywords, categoria

def format_experience(experience, keywords):
    """Formatea la experiencia laboral relevante"""
    formatted = []
    for exp in experience[:4]:  # Últimos 3 trabajos
        entry = (
            f"{exp['role']} - {exp['company']} ({exp['period']})\n"
            f"{exp['description']}\n"
            f"Logros:\n"
        )
        # Filtrar logros relevantes
        relevant_achievements = [
            ach for ach in exp['key_achievements'] 
            if any(kw.lower() in ach['result'].lower() for kw in keywords)
        ][:1]  # Máximo 2 logros por puesto
        
        if not relevant_achievements:
            relevant_achievements = exp['key_achievements'][:1]
            
        entry += "\n".join(f"- {ach['result']}" for ach in relevant_achievements)
        formatted.append(entry)
    return "\n\n".join(formatted)

def build_cv_prompt(profile, job_offer, keywords, lang, categoria):
    """Construye prompt de CV filtrando skills por categoría (data/telecom)"""
    # Extraer habilidades SOLO de la categoría relevante (data o telecom)
    skills_categoria = profile['skills'].get(categoria, [])
    my_actual_skills = [skill.lower() for skill in skills_categoria]
    # Filtrar keywords que coincidan con skills de la categoría
    relevant_keywords = [
        kw for kw in keywords 
        if any(kw.lower() in skill_name for skill_name in my_actual_skills)
    ]
    # Identificar skills faltantes específicos de la categoría
    missing_skills = [
        kw for kw in keywords 
        if not any(kw.lower() in skill_name for skill_name in my_actual_skills)
    ]
    print(missing_skills)
    # Lista explícita de habilidades DE LA CATEGORÍA
    explicit_skills_list = "\n".join(
        f"- {skill}"
        for skill in skills_categoria
    )

    return f"""
    Crea un CV profesional completo y FINALIZADO en {lang} que NO SUPERE UNA PÁGINA para el puesto de "{job_offer.get('title', '')}"
    utilizando ÚNICAMENTE la información proporcionada a continuación.
 
    Requerimientos de la oferta de trabajo: {keywords}
    
    --- SÓLO SE REQUIEREN LAS SIGUIENTES SECCIONES: ---    

    --- 1. RESUMEN PROFESIONAL ---
    -  Máximo 4-5 líneas enfocado en {categoria.upper()}
    - 'Utiliza las palabras clave de la oferta de trabajo siempre que sea posible, pero solo si reflejan mi experiencia real.'
    - 'Destaca mis logros y habilidades más relevantes para la vacante.'
    - 'Si no cumplo con algún requisito, enfatiza mis capacidades transferibles y mi disposición para aprender.'
    - 'Sé concreto, claro y profesional, evitando frases genéricas o vacías.'
    - 'El resumen debe estar orientado a lo que puedo aportar a la empresa, no a mis objetivos personales.'

    --- 2. EXPERIENCIA LABORAL EXACTA ---
    {format_experience(profile['experience'], relevant_keywords)}
    (Destacar logros relacionados con {categoria.upper()} y relevante para los requerimientos de la oferta de trabajo)
    
    --- 3. HABILIDADES ({categoria.upper()}) ---
    {explicit_skills_list} y relevante para el SENTIDO de la oferta organizadas por categorías:
    Languages:
    Frameworks:
    Tools:
    Platforms
    Soft Skills:
    
    --- REGLAS ABSOLUTAS ---
    1. EXCLUIR SIEMPRE LOS SIGUIENTES {', '.join(missing_skills)} SKILLS [QUE NO POSEO]
    2. USAR ESTRICTAMENTE LOS TÉRMINOS TÉCNICOS DEL JSON
    
    --- FORMATO ---
    • Markdown compatible con ATS
    • Encabezados: ###
    • Máxima legibilidad en 1 página
    """


def build_cv_prompt_(profile, job_offer, keywords, lang, categoria):
    """Construye prompt de CV filtrando skills por categoría (data/telecom)"""
    #print(keywords)
    # Extraer habilidades SOLO de la categoría relevante (data o telecom)
    skills_categoria = profile['skills'].get(categoria, [])
    my_actual_skills = [skill['name'].lower() for skill in skills_categoria]
    #print(my_actual_skills)
    # Filtrar keywords que coincidan con skills de la categoría
    relevant_keywords = [
        kw for kw in keywords 
        if any(kw.lower() in skill_name for skill_name in my_actual_skills)
    ]
    #print(relevant_keywords)
    # Identificar skills faltantes específicos de la categoría
    missing_skills = [
        kw for kw in keywords 
        if not any(kw.lower() in skill_name for skill_name in my_actual_skills)
    ]
    #print(missing_skills)
    # Lista explícita de habilidades DE LA CATEGORÍA
    explicit_skills_list = "\n".join(
        #f"- {skill['name']} ({skill['years_of_experience']} años)"
        f"- {skill['name']}"
        for skill in skills_categoria
    )
    #print(explicit_skills_list)

    return f"""
    Crea un CV profesional en {lang} que NO SUPERE UNA PÁGINA para el puesto de "{job_offer.get('title', '')}"
    
    --- SÓLO SE REQUIEREN LAS SIGUIENTES SECCIONES: ---    

    --- 1. RESUMEN PROFESIONAL ---
    - 'Máximo 4-6 líneas enfocado en {categoria.upper()}'
    - 'Utiliza las palabras clave de la oferta de trabajo siempre que sea posible, pero solo si reflejan mi experiencia real.'
    - 'Destaca mis logros y habilidades más relevantes para la vacante.'
    - 'Si no cumplo con algún requisito, enfatiza mis capacidades transferibles y mi disposición para aprender.'
    - 'Sé concreto, claro y profesional, evitando frases genéricas o vacías.'
    - 'El resumen debe estar orientado a lo que puedo aportar a la empresa, no a mis objetivos personales.'

    --- 2. EXPERIENCIA LABORAL EXACTA ---
    {format_experience(profile['experience'], relevant_keywords)}
    (Destacar logros relacionados con {categoria.upper()} y relevante para el SENTIDO de los keywords de la oferta)
    
    --- 3. HABILIDADES ({categoria.upper()}) ---
    {explicit_skills_list} y relevante para el SENTIDO de la oferta organizadas por categorías:
    Languages:
    Frameworks:
    Tools:
    Platforms
    Soft Skills:
    
    --- REGLAS ABSOLUTAS ---
    1. EXCLUIR SIEMPRE: {', '.join(missing_skills)} [NO POSEIDOS]
    2. USAR ESTRICTAMENTE LOS TÉRMINOS TÉCNICOS DEL JSON
    
    --- FORMATO ---
    • Markdown compatible con ATS
    • Encabezados: ###
    • Máxima legibilidad en 1 página
    """