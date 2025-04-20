# utils/linkedin_utils.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from langdetect import detect, LangDetectException
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import os
import re

def setup_selenium_driver():
    """
    Configura y devuelve una instancia del driver de Selenium.
    :return: Instancia de Selenium WebDriver.
    """
    GECKO_DRIVER_PATH = os.getenv('GECKO_DRIVER_PATH')  # Ruta al GeckoDriver
    
    # Configurar opciones del navegador
    options = Options()
    options.set_preference("permissions.default.image", 2)  # No cargar imágenes
    options.set_preference("javascript.enabled", True)  # Habilitar JavaScript
    options.set_preference("network.http.use-cache", True)  # Usar caché    
    
    #print(f"Ruta de GeckoDriver: {GECKO_DRIVER_PATH}")  # Mensaje de depuración
    service = Service(GECKO_DRIVER_PATH)
    driver = webdriver.Firefox(service=service)
    return driver

def login_to_linkedin(driver):
    """
    Inicia sesión en LinkedIn.
    :param driver: Instancia de Selenium WebDriver.
    """
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')  # Tu email de LinkedIn
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')  # Tu contraseña de LinkedIn

    driver.get('https://www.linkedin.com/login')
    time.sleep(2)  # Esperar a que la página cargue

    # Ingresar credenciales
    driver.find_element(By.ID, 'username').send_keys(LINKEDIN_EMAIL)
    driver.find_element(By.ID, 'password').send_keys(LINKEDIN_PASSWORD)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(3)  # Esperar a que la sesión se inicie

def extract_linkedin_job_description(html_content):
    """Extrae todo el texto de la descripción del puesto."""
    soup = BeautifulSoup(html_content, 'html.parser')
    full_text = ""

    # Identificar el contenedor de la descripción
    description_container = soup.find('div', class_='jobs-description__content')
    if not description_container:
        description_container = soup.find('div', class_='jobs-box__html-content')
    
    if description_container:
        # Extraer todo el texto del contenedor
        full_text = description_container.get_text(separator="\n").strip()

    return full_text

def extract_linkedin_publication_date(driver):
    """Extrae y convierte la fecha de publicación de la oferta."""
    try:
        # Intentar extraer la fecha relativa normal (sin "Reposted")
        try:
            date_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "tvm__text--low-emphasis")]//span[contains(text(), "ago")]'))
            )
            date_text = date_element.text.strip()
        except:
            # Si no se encuentra, buscar en el caso de "Reposted"
            date_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "tvm__text--positive")]//span[contains(text(), "ago")]'))
            )
            date_text = date_element.text.strip()

        # Convertir el texto en una fecha concreta
        publication_date = convert_relative_linkedin_date_to_actual_date(date_text)
        return publication_date
    except Exception as e:
        print(f"Error al extraer la fecha de publicación: {e}")
        return "No disponible"

def convert_relative_linkedin_date_to_actual_date(relative_date):
    """Convierte una fecha relativa (ej. 'hace 5 días') en una fecha concreta."""
    today = datetime.now()

    # Convertir a minúsculas para manejar mayúsculas y minúsculas
    relative_date = relative_date.lower()

    # Extraer el número de la cadena
    try:
        time_ago = int(''.join(filter(str.isdigit, relative_date)))  # Extraer solo dígitos
    except ValueError:
        print(f"Formato de fecha no reconocido: {relative_date}")
        return "No disponible"

    # Manejo de horas
    if "hora" in relative_date or "hour" in relative_date:
        return (today - timedelta(hours=time_ago)).strftime("%Y-%m-%d")

    # Manejo de días
    elif "día" in relative_date or "day" in relative_date:
        return (today - timedelta(days=time_ago)).strftime("%Y-%m-%d")

    # Manejo de semanas
    elif "semana" in relative_date or "week" in relative_date:
        return (today - timedelta(weeks=time_ago)).strftime("%Y-%m-%d")

    # Manejo de meses
    elif "mes" in relative_date or "month" in relative_date:
        return (today - timedelta(days=time_ago * 30)).strftime("%Y-%m-%d")

    # Si no se reconoce el formato
    else:
        print(f"Formato de fecha no reconocido: {relative_date}")
        return "No disponible"

def extract_linkedin_job_details(driver, link):
    """Extrae los detalles de la oferta de trabajo en LinkedIn."""
    job_details = {}

    try:
        # Extraer el código de referencia desde la URL
        job_details['reference_code'] = link  # Usamos la URL completa
    except Exception as e:
        job_details['reference_code'] = "No disponible"
        print(f"Error al extraer el código de referencia: {e}")

    try:
        # Extraer el nombre de la empresa
        company_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details-jobs-unified-top-card__company-name")]//a'))
        )
        job_details['company'] = company_element.text.strip()
    except Exception as e:
        job_details['company'] = "No disponible"
        print(f"Error al extraer el nombre de la empresa: {e}")

    try:
        # Extraer el título del puesto
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//h1[contains(@class, "t-24") and contains(@class, "t-bold")]'))
        )
        job_details['title'] = title_element.text
    except Exception as e:
        job_details['title'] = "No disponible"
        print(f"Error al extraer el título: {e}")

    try:
        # Extraer la ubicación
        location_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details-jobs-unified-top-card__primary-description-container")]//span[contains(@class, "tvm__text--low-emphasis")]'))
        )
        job_details['location'] = location_element.text.strip()
    except Exception as e:
        job_details['location'] = "No disponible"
        print(f"Error al extraer la ubicación: {e}")

    try:
        # Extraer la fecha de publicación
        job_details['publication_date'] = extract_linkedin_publication_date(driver)
    except Exception as e:
        job_details['publication_date'] = "No disponible"
        print(f"Error al extraer la fecha de publicación: {e}")

    try:
        # Extraer todo el texto del contenedor job-insight
        job_insight_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//li[contains(@class, "job-details-jobs-unified-top-card__job-insight")]'))
        )
        # Extraer todos los bloques de texto dentro del contenedor
        text_blocks = job_insight_element.find_elements(By.XPATH, './/span[@dir="ltr"]')
        # Unir los bloques de texto con un separador (por ejemplo, "|")
        job_insight_text = " | ".join(block.text.strip() for block in text_blocks if block.text.strip())
        job_details['job_insights'] = job_insight_text

    except Exception as e:
        job_details['job_insights'] = "No disponible"
        print(f"Error al extraer el texto del contenedor job-insight: {e}")

    try:
        # Extraer la descripción del puesto
        job_details['description'] = extract_linkedin_job_description(driver.page_source)
    except Exception as e:
        job_details['description'] = "No disponible"
        print(f"Error al extraer la descripción del puesto: {e}")

    try:
        # Detectar el idioma de la descripción del puesto
        if job_details['description'] != "No disponible":
            language = detect(job_details['description'])
            job_details['language'] = language
        else:
            job_details['language'] = "No disponible"
    except LangDetectException as e:
        job_details['language'] = "No disponible"
        print(f"Error al detectar el idioma: {e}")
       
    return job_details