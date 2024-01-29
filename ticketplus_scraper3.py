import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import random
import datetime
from selenium.common.exceptions import NoSuchElementException
import os.path
import unicodedata
import shutil
import glob
import helper as help
from selenium.webdriver.chrome.options import Options

import pymongo


list_regiones = {
    1: {"nombre": "I Región de Tarapacá", "link": "https://ticketplus.cl/s/region-de-tarapaca"},
    2: {"nombre": "II Región de Antofagasta", "link": "https://ticketplus.cl/s/region-de-antofagasta"},
    3: {"nombre": "III Región de Atacama", "link": "https://ticketplus.cl/s/region-de-atacama"},
    4: {"nombre": "IV Región de Coquimbo", "link": "https://ticketplus.cl/s/region-de-coquimbo"},
    5: {"nombre": "V Región de Valparaíso", "link": "https://ticketplus.cl/s/region-de-valparaiso"},
    6: {"nombre": "VI Región del Libertador General Bernardo O'Higgins", "link": "https://ticketplus.cl/s/region-del-libertador-general-bernardo-o-higgins"},
    7: {"nombre": "VII Región del Maule", "link": "https://ticketplus.cl/s/region-del-maule"},
    8: {"nombre": "VIII Región del Biobío", "link": "https://ticketplus.cl/s/region-del-bio-bio"},
    9: {"nombre": "IX Región de la Araucanía", "link": "https://ticketplus.cl/s/region-de-la-araucania"},
    10: {"nombre": "X Región de Los Lagos", "link": "https://ticketplus.cl/s/region-de-los-lagos"},
    11: {"nombre": "XI Región de Aysén", "link": "https://ticketplus.cl/s/region-de-aysen"},
    12: {"nombre": "XII Región de Magallanes y Antártica", "link": "https://ticketplus.cl/s/region-de-magallanes-y-de-la-antartica-chilena"},
    13: {"nombre": "Región Metropolitana de Santiago", "link": "https://ticketplus.cl/s/region-metropolitana"},
    14: {"nombre": "XIV Región de Los Ríos", "link": "https://ticketplus.cl/s/region-de-los-rios"},
    15: {"nombre": "XV Región de Arica y Parinacota", "link": "https://ticketplus.cl/s/region-de-arica-y-parinacota"}
}

#esta no es necesaria en docker
#chrome_driver_path = r"C:\Users\juand\Desktop\EventFind\herramientas_desarrollo\chromedriver-win64\chromedriver.exe"
#options = webdriver.ChromeOptions()

# Configura las opciones de Chrome para el modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecuta Chrome en modo headless
chrome_options.add_argument("--no-sandbox")  # Desactiva el modo sandbox para Chrome
chrome_options.add_argument("--disable-dev-shm-usage")  # Evita problemas en contenedores

#no van en docker
#options.add_argument('--incognito')
#options.add_argument('--ignore-certificate-errors')
#service = Service(executable_path=chrome_driver_path, options=options)
#driver = webdriver.Chrome(service=service)

# Inicializa el driver de Chrome con las opciones configuradas
driver = webdriver.Chrome(options=chrome_options)

hoy = datetime.datetime.now()
carpeta_fecha = hoy.strftime("%d-%m-%Y")
os.makedirs(carpeta_fecha, exist_ok=True)

eventos = []
id_evento = 0

for id_region, region in list_regiones.items():
    url = region["link"]
    driver.get(url)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    event_divs = soup.find_all("div", {"class": "col-xs-6 col-md-3 m-b-xs p-x-xs element-item"})

    event_links = []
    for div in event_divs:


        link = div.find("a")["href"]
        event_links.append(f"https://ticketplus.cl{link}")

    eventos = []
    id_evento = 0  # Inicializa el contador para cada región

    for link in event_links:
        id_evento += 1
        driver.get(link)
        time.sleep(3)

        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')

        script_element = soup.find('script', {'type': 'application/ld+json'})

        try:
            event_json = json.loads(script_element.string)
        except Exception as e:
            # Si no se puede cargar el JSON, lo guarda en un archivo de registro
            print(f"Error al cargar JSON en evento {id_evento}: {str(e)}")
            nombre_archivo_log = f'error_carga_json_evento_{id_region}_{region["nombre"]}_{id_evento}.json'
            ruta_archivo_log = os.path.join(carpeta_fecha, nombre_archivo_log)
            with open(ruta_archivo_log, 'w', encoding='utf-8') as f:
                f.write(f"Error al cargar JSON en evento {id_evento}: {str(e)}\n\n")
                f.write(script_element.string)
            continue

        event_json = json.loads(script_element.string)

        titulo = event_json['name']
        try:
            fecha_hora = event_json['startDate']
        except KeyError:
            fecha_hora = ''

        direccion_titulo = event_json['location']['name']
        direccion_detalle = event_json['location']['address']['streetAddress']
        detalle_evento = help.limpiar_cadena(event_json['description'].replace('\n', ' '))
        imagen_url = event_json['image']
        evento_url = event_json['url']
        latitud = event_json['location']['geo']['latitude']
        longitud = event_json['location']['geo']['longitude']

        img_element = soup.find('img', {'alt': titulo})
        if img_element:
            img_url = img_element['src'].split('?')[0]

            extension_img = help.obtener_extension(img_url)
            carpeta_regional = help.formatear_nombre(f'eventos_{id_region}_{region["nombre"]}')
            carpeta_imagenes = os.path.join(carpeta_fecha, carpeta_regional)
            os.makedirs(carpeta_imagenes, exist_ok=True)
            nombre_imagen = help.formatear_nombre(f'eventos_{id_region}_{region["nombre"]}_{id_evento}{extension_img}')
            ruta_imagen = os.path.join(carpeta_imagenes, nombre_imagen)
            help.descargar_imagen(img_url, ruta_imagen)

            # Cambiar el formato de la ruta de la imagen en el JSON
            ruta_imagen_json = f"assets/eventos/{carpeta_fecha}/images/{carpeta_regional}/{nombre_imagen}".replace("\\", "/")
        else:
            ruta_imagen_json = ''

        latitud = event_json['location']['geo']['latitude']
        longitud = event_json['location']['geo']['longitude']

        evento = {
            'titulo': titulo,
            'fecha': fecha_hora.split('T')[0],
            'hora': fecha_hora.split('T')[1] if len(fecha_hora.split('T')) > 1 else '',
            'direccionTitulo': direccion_titulo,
            'direccionDetalle': direccion_detalle,
            'detalleEvento': detalle_evento,
            'imagen': ruta_imagen_json,  # Actualiza el valor de la propiedad imagen en el JSON
            'evento_url': evento_url,
            'lat': latitud,  # Agrega la latitud
            'long': longitud,  # Agrega la longitud
            'logo' : 'logo_ticketplus.png'
        }
        eventos.append(evento)


    nombre_archivo_json = help.formatear_nombre(f'eventos_{id_region}_{region["nombre"]}.json')
    nombre_archivo = os.path.join(carpeta_fecha, nombre_archivo_json)
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        # Escribe la lista de eventos en el archivo JSON
        json.dump(eventos, f, ensure_ascii=False, indent=4)
        f.write('\n')

driver.quit()
