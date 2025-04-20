# stages/initial_filter.py

import re
from utils.initial_filter_keywords import rejected_titles
from utils.initial_filter_keywords import accepted_titles, positive_keywords


def is_location_accepted(location):
    """
    Verifica si la ubicación cumple con las condiciones deseadas.
    - Acepta "Madrid, Spain" o "Madrid, Community of Madrid, Spain".
    - Acepta "Spain" o "España" solos.
    - Acepta otras ubicaciones como "Unión Europea", "European Union", o "UE".
    """
    location = location.lower()

    # Condición 1: "Madrid" + "Spain"
    if "madrid" in location and "spain" in location:
        return True

    # Condición 2: "Spain" o "España" solos
    #if re.search(r"(^|\W)spain($|\W)", location) or re.search(r"(^|\W)españa($|\W)", location):
    #    return True
    # Condición 2: "Spain" o "España" solos (sin otras palabras)
    if re.fullmatch(r"spain|españa", location.strip()):
        return True

    # Condición 3: Otras ubicaciones aceptadas (Unión Europea, European Union, UE)
    other_accepted_locations = [
        r"\bunión europea\b",
        r"\beuropean union\b",
        r"\bue\b",
        r"\balcobendas\b",
    ]
    if any(re.search(pattern, location) for pattern in other_accepted_locations):
        return True

    return False



def initial_filter(job_offers):
    """
    Filtra ofertas basándose en palabras clave en el título y ubicación.
    - Descarta ofertas con palabras clave no deseadas en el título.
    - Acepta ofertas en ubicaciones específicas (Madrid o Unión Europea).
    """
    filtered_offers = []

    for offer in job_offers:
        title = offer.get('title', '').lower()  # Convertir el título a minúsculas
        location = offer.get('location', '').lower()  # Convertir la ubicación a minúsculas
        description = offer.get('description', '').lower()  # Convertir la descripción a minúsculas
       

        # 1. Verificar si la oferta contiene palabras clave positivas
        has_positive_keyword = any(
            re.search(rf'\b{re.escape(keyword.lower())}\b', title) or
            re.search(rf'\b{re.escape(keyword.lower())}\b', description)
            for keyword in positive_keywords
        )

        # 2. Verificar si el título está en la lista de títulos aceptados
        has_accepted_title = any(
            re.search(rf'\b{re.escape(keyword.lower())}\b', title)
            for keyword in accepted_titles
        )

        # 3. Verificar si la ubicación es aceptada
        #has_accepted_location = any(
        #    re.search(rf'\b{re.escape(keyword.lower())}\b', location)
        #    for keyword in accepted_locations
        #)
        has_accepted_location = is_location_accepted(location)

        # 4. Verificar si el título contiene palabras clave no deseadas
        has_rejected_title = any(
            re.search(rf'\b{re.escape(keyword.lower())}\b', title)
            for keyword in rejected_titles
        )

        # Aceptar la oferta si:
        # - Tiene una palabra clave positiva O un título aceptado
        # - Y no tiene un título no deseado
        # - Y está en una ubicación aceptada
        if (has_positive_keyword or has_accepted_title) and not has_rejected_title and has_accepted_location:
            filtered_offers.append(offer)

    print("filtro inicial:")
    # Mostrar las ofertas descargadas
    for offer in filtered_offers:
        
        print(f"- Reference Code: {offer.get('reference_code', 'No disponible')}, Company: {offer.get('company', 'No disponible')}")

    return filtered_offers

def initial_filter_(job_offers):
    """
    Filtra ofertas basándose en palabras clave en el título y ubicación.
    Devuelve una tupla con (ofertas_filtradas, reporte_rechazos)
    """
    filtered_offers = []
    rejection_reasons = {}  # Diccionario para almacenar motivos de rechazo
    
    for offer in job_offers:
        ref_code = offer.get('reference_code', 'NO_REF')
        rejection_reasons[ref_code] = []
        
        title = offer.get('title', '').lower()
        location = offer.get('location', '').lower()
        description = offer.get('description', '').lower()
        
        # 1. Verificar palabras clave positivas
        positive_kw_found = []
        for keyword in positive_keywords:
            kw = keyword.lower()
            if (re.search(rf'\b{re.escape(kw)}\b', title) or 
                re.search(rf'\b{re.escape(kw)}\b', description)):
                positive_kw_found.append(kw)
        
        has_positive_keyword = bool(positive_kw_found)
        
        # 2. Verificar títulos aceptados
        accepted_title_found = []
        for keyword in accepted_titles:
            kw = keyword.lower()
            if re.search(rf'\b{re.escape(kw)}\b', title):
                accepted_title_found.append(kw)
        
        has_accepted_title = bool(accepted_title_found)
        
        # 3. Verificar ubicación
        has_accepted_location = is_location_accepted(location)
        if not has_accepted_location:
            rejection_reasons[ref_code].append(f"Ubicación no aceptada: {location}")
        
        # 4. Verificar títulos rechazados
        rejected_title_found = []
        for keyword in rejected_titles:
            kw = keyword.lower()
            if re.search(rf'\b{re.escape(kw)}\b', title):
                rejected_title_found.append(kw)
        
        has_rejected_title = bool(rejected_title_found)
        if has_rejected_title:
            rejection_reasons[ref_code].append(f"Título contiene palabras no deseadas: {', '.join(rejected_title_found)}")
        
        # Lógica de aceptación
        condition1 = has_positive_keyword or has_accepted_title
        condition2 = not has_rejected_title
        condition3 = has_accepted_location
        
        if condition1 and condition2 and condition3:
            filtered_offers.append(offer)
            # Registrar qué criterios positivos cumplió
            acceptance_details = []
            if positive_kw_found:
                acceptance_details.append(f"Palabras clave positivas: {', '.join(positive_kw_found)}")
            if accepted_title_found:
                acceptance_details.append(f"Títulos aceptados: {', '.join(accepted_title_found)}")
            rejection_reasons[ref_code].append(f"ACEPTADA: {'; '.join(acceptance_details)}")
        else:
            # Registrar qué condiciones faltaron
            missing_conditions = []
            if not condition1:
                missing_conditions.append("No tiene palabras clave positivas ni título aceptado")
            if not condition2:
                missing_conditions.append("Tiene título no deseado")
            if not condition3:
                missing_conditions.append("Ubicación no aceptada")
            
            if missing_conditions:
                rejection_reasons[ref_code].append(f"Rechazada por: {', '.join(missing_conditions)}")

    # Generar reporte detallado
    print("\n=== REPORTE DE FILTRADO INICIAL ===")
    for ref_code, reasons in rejection_reasons.items():
        print(f"\nOferta {ref_code}:")
        for reason in reasons:
            print(f"  - {reason}")
    
    print(f"\nTotal ofertas ingresadas: {len(job_offers)}")
    print(f"Ofertas aceptadas: {len(filtered_offers)}")
    print(f"Ofertas rechazadas: {len(job_offers) - len(filtered_offers)}")
    
    return filtered_offers, rejection_reasons