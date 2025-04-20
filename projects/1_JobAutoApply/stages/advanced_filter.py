# stages/advanced_filter.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def advanced_filter(filtered_offers, profile_eng, profile_esp):
    """
    Filtra las ofertas de empleo basándose en un perfil profesional.
    :param filtered_offers: Lista de ofertas previamente filtradas.
    :param profile_eng: Perfil profesional en inglés.
    :param profile_esp: Perfil profesional en español.
    :return: Lista de ofertas que superan el filtrado avanzado.
    """
    advanced_offers = []

    for offer in filtered_offers:
        # Determinar el idioma de la oferta
        language = offer.get("language", "").lower()

        # Seleccionar el perfil adecuado
        if language == "es":
            profile = profile_esp
        elif language == "en":
            profile = profile_eng
        else:
            print(f"Idioma no reconocido en la oferta: {language}")
            continue

        # Extraer información del perfil seleccionado
        profile_skills_data = profile["skills"]["data"]  # Ya es una lista de strings
        profile_skills_telecom = profile["skills"]["telecom"]  # Ya es una lista de strings
        profile_target_roles = profile["preferences"]["target_roles"]
        profile_preferred_industries = profile["preferences"]["preferred_industries"]
        profile_experience = [
            " ".join(exp["description"]) + " | Achievements: " + " | ".join(
                f"{ach['title']} - {ach['result']}"
                for ach in exp["key_achievements"]
                )
                for exp in profile["experience"]
        ]

        # Combinar habilidades de datos y experiencia en un solo texto para el perfil
        profile_text_data = " ".join(profile_skills_data + profile_experience)

        # Combinar habilidades de telecomunicaciones y experiencia en un solo texto para el perfil
        profile_text_telecom = " ".join(profile_skills_telecom + profile_experience)

        # Preparar texto de la oferta
        title = offer.get("title", "")
        description = offer.get("description", "")
        offer_text = f"{title} {description}"

        # Calcular similitud entre el perfil (datos) y la oferta
        vectorizer_data = TfidfVectorizer()
        tfidf_matrix_data = vectorizer_data.fit_transform([profile_text_data, offer_text])
        cosine_similarity_data = cosine_similarity(tfidf_matrix_data[0:1], tfidf_matrix_data[1:]).flatten()[0]

        # Calcular similitud entre el perfil (telecom) y la oferta
        vectorizer_telecom = TfidfVectorizer()
        tfidf_matrix_telecom = vectorizer_telecom.fit_transform([profile_text_telecom, offer_text])
        cosine_similarity_telecom = cosine_similarity(tfidf_matrix_telecom[0:1], tfidf_matrix_telecom[1:]).flatten()[0]

        # Filtrar ofertas basadas en la similitud y preferencias
        if any(role.lower() in title.lower() for role in profile_target_roles):
            if cosine_similarity_data > 0.55:  # Umbral de similitud para datos
                advanced_offers.append(offer)
        elif any(industry.lower() in description.lower() for industry in profile_preferred_industries):
            if cosine_similarity_telecom > 0.55:  # Umbral de similitud para telecomunicaciones
                advanced_offers.append(offer)

    print("Filtro avanzado:")
    for offer in advanced_offers:
        print(f"- Reference Code: {offer.get('reference_code', 'No disponible')}, Company: {offer.get('company', 'No disponible')}")

    return advanced_offers