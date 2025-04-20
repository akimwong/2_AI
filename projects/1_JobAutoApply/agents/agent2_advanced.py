# agents/agent2_advanced.py

import json
from stages.advanced_filter import advanced_filter

class Agent2:
    def __init__(self):
        # Cargar los perfiles en ambos idiomas
        self.profile_esp = self.load_profile("profile_esp.json")
        self.profile_eng = self.load_profile("profile_eng.json")

    def load_profile(self, filename):
        """
        Carga el perfil profesional desde un archivo JSON.
        :return: Diccionario con el perfil profesional.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                profile = json.load(file)
            return profile
        except FileNotFoundError:
            print("Error: El archivo {filename} no existe.")
            return {}
        except json.JSONDecodeError:
            print("Error: El archivo {filename} no tiene un formato JSON válido.")
            return {}

    def run(self, filtered_offers):
        """
        Ejecuta el Agente 2: Filtrado avanzado de ofertas.
        :param filtered_offers: Lista de ofertas previamente filtradas por el Agente 1.
        :return: Lista de ofertas que superan el filtrado avanzado.
        """
        print("Ejecutando Agente 2: Filtrado avanzado de ofertas...")

        # Verificar si el perfil se cargó correctamente
        if not self.profile_eng or not self.profile_esp:
        #if not self.profile:
            print("Error: No se pudo cargar el perfil profesional.")
            return []

        # Aplicar filtrado avanzado
        #advanced_offers = advanced_filter(filtered_offers, self.profile)
        advanced_offers = advanced_filter(filtered_offers, self.profile_eng, self.profile_esp)

        return advanced_offers