# main.py

import os
from dotenv import load_dotenv
from agents.agent1_download import Agent1
from agents.agent2_advanced import Agent2
from agents.agent3_profile import Agent3

# Cargar variables del archivo .env
load_dotenv()

def main():
    """Función principal."""
    # Ejecutar Agente 1: Descarga y filtrado inicial
    agent1 = Agent1()
    filtered_offers = agent1.run()

    # Verificar si hay ofertas filtradas
    if not filtered_offers:
        return  # Terminar el programa si no hay ofertas
    
    # Ejecutar Agente 2: Filtrado avanzado
    agent2 = Agent2()
    advanced_offers = agent2.run(filtered_offers)

    # Verificar si hay ofertas avanzadas
    if not advanced_offers:
        print("No hay ofertas avanzadas para generar CVs.")
        return  # Terminar el programa si no hay ofertas avanzadas
    
    # Ejecutar Agente 3: Generación de CVs personalizados
    agent3 = Agent3()
    for offer in advanced_offers:
        print(f"\nGenerando CV para la oferta: {offer.get('title', 'Sin título')}")
        cv = agent3.generate_cv(offer)
        if cv:
            print("\nCurrículum generado:")
            print(cv)
        else:
            print("Error: No se pudo generar el CV para esta oferta.")

if __name__ == '__main__':
    main()