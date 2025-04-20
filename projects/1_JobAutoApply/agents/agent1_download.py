# agents/agent1_download.py

from stages.download_offers import download_offers
from utils.email_utils import get_gmail_service
from stages.initial_filter import initial_filter

class Agent1:
    def __init__(self):
        # Obtener el servicio de Gmail
        self.gmail_service = get_gmail_service()

    def run(self):
        """
        Ejecuta el Agente 1: Descarga y filtrado inicial de ofertas.
        :return: Lista de ofertas filtradas.
        """
        print("Ejecutando Agente 1: Descarga y filtrado inicial de ofertas...")

        # Descargar ofertas
        job_offers = download_offers(self.gmail_service)

        # Verificar si hay ofertas filtradas
        if not job_offers:
            return  # Terminar el programa si no hay ofertas

        # Aplicar filtrado inicial
        filtered_offers = initial_filter(job_offers)

        return filtered_offers