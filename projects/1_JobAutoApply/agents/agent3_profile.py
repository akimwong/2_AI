# agents/agent3_profile.py

from utils.profile_manager import index  # Importa el índice de Pinecone
from stages.cv_generator import generate_cv_direct

class Agent3:
    def __init__(self):
        self.cv_languages = {"en": "English", "es": "Spanish"}
    
    def generate_cv(self, job_offer):
        lang = job_offer.get("language", "en").lower()[:2]
        if lang not in self.cv_languages:
            return None
            
        return {
            "cv": generate_cv_direct(
                job_offer,
                self.cv_languages[lang]
            )
        }