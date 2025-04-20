# stages/download_offers.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.email_utils import extract_job_links_from_email
from utils.linkedin_utils import setup_selenium_driver, login_to_linkedin, extract_linkedin_job_details
import time

def download_offers(service):
    """
    Descarga y procesa ofertas de empleo.
    :param service: Servicio de Gmail.
    :return: Lista de ofertas (cada oferta es un diccionario con detalles).
    """
    # Extraer enlaces de ofertas de los correos electrónicos
    job_links = extract_job_links_from_email(service)
    if not job_links:
        print("No se encontraron ofertas nuevas en los correos de hoy.")
        return []  # Si no hay ofertas, retornar una lista vacía y no hacer nada más

    # Configurar Selenium e iniciar sesión en LinkedIn (solo si hay ofertas)
    driver = setup_selenium_driver()
    login_to_linkedin(driver)

    # Navegar a cada enlace y extraer detalles de la oferta
    job_offers = []
    for link in job_links:
        try:
            print(f"Navegando a: {link}")
            driver.get(link)

            # Esperar a que la página cargue completamente
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Intentar hacer clic en el botón "See more"
            try:
                see_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//footer//button[.//span[text()='See more']]"))
                )
                see_more_button.click()
                time.sleep(2)  # Esperar a que el contenido adicional cargue
            except Exception as e:
                print(f"No se pudo encontrar el botón 'See more' en {link}: {e}")

            # Extraer detalles de la oferta
            try:
                job_details = extract_linkedin_job_details(driver, link)
                job_offers.append(job_details)
            except Exception as e:
                print(f"Error al extraer detalles de la oferta en {link}: {e}")

        except Exception as e:
            print(f"Error al navegar a {link}: {e}")
            continue  # Continuar con la siguiente oferta si hay un error

    # Cerrar el navegador (solo si se abrió)
    driver.quit()

    # Mostrar las ofertas descargadas
    print("\nOfertas descargadas:")
    for offer in job_offers:
        print(f"- Reference Code: {offer.get('reference_code', 'No disponible')}, Company: {offer.get('company', 'No disponible')}, Location: {offer.get('location', 'No disponible')}, Language: {offer.get('language', 'No disponible')}")

    return job_offers