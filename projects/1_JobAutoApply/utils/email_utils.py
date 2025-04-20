# utils/email_utils.py

import base64
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def get_gmail_service():
    """
    Obtiene el servicio de Gmail.
    :return: Servicio de Gmail autenticado.
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE')  # Archivo JSON de credenciales de Google
    TOKEN_FILE = 'token.json'

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def normalize_job_link(link):
    """Normaliza el enlace de la oferta de empleo."""
    parsed_url = urlparse(link)
    # Eliminar parámetros de seguimiento (query y fragment)
    clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return clean_url

def extract_job_links_from_email(service):
    """Extrae los enlaces de ofertas de empleo de LinkedIn recibidos hoy."""
    # Obtener la fecha de hoy en formato YYYY/MM/DD
    today = datetime.now().strftime('%Y/%m/%d')
    # Definir una fecha concreta para pruebas (por ejemplo, 15 de marzo de 2025)
    #today = datetime(2025, 3, 11).strftime('%Y/%m/%d')  # Cambia la fecha según necesites
    #today = datetime(2025, 3, 20).strftime('%Y/%m/%d') 

    # Buscar correos recibidos hoy
    results = service.users().messages().list(userId='me', q=f'after:{today}').execute()
    messages = results.get('messages', [])
    job_links = set()  # Usamos un conjunto para evitar duplicados

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        payload = msg['payload']
        headers = payload.get('headers', [])
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')

        # Extraer el cuerpo del correo
        if 'parts' in payload:
            parts = payload['parts']
            for part in parts:
                if part['mimeType'] == 'text/html':
                    data = part['body']['data']
                    html_content = base64.urlsafe_b64decode(data).decode('utf-8')
                    soup = BeautifulSoup(html_content, 'html.parser')
                    # Buscar enlaces de ofertas de empleo en LinkedIn
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if '/comm/jobs/view/' in href:  # Filtramos solo enlaces de ofertas de empleo
                            normalized_link = normalize_job_link(href)  # Normalizar el enlace
                            job_links.add(normalized_link)  # Usamos add() para evitar duplicados
        else:
            # Si el correo no tiene partes, extraer directamente del cuerpo
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            soup = BeautifulSoup(body, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/comm/jobs/view/' in href:  # Filtramos solo enlaces de ofertas de empleo
                    normalized_link = normalize_job_link(href)  # Normalizar el enlace
                    job_links.add(normalized_link)  # Usamos add() para evitar duplicados

    # Verificar si hay enlaces
    if not job_links:
        #print("No se encontraron ofertas nuevas en los correos de hoy.")
        return None  # Devolver None si no hay enlaces

    return list(job_links)  # Convertimos el conjunto a una lista