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
from selenium.common.exceptions import NoSuchElementException
import os.path
import glob


def formatear_nombre(nombre):
    nombre = nombre.lower()
    nombre = nombre.replace(" ", "_")
    nombre = unicodedata.normalize("NFKD", nombre).encode("ASCII", "ignore").decode("ASCII")
    return nombre

def formatear_fecha(fecha_str):
    formatos_fecha = [
        '%A %d de %B %Y',  # Ejemplo: "Viernes 31 de Marzo 2023"
        '%d de %B %Y',  # Ejemplo: "07 de Abril 2023"
        '%d de %B %Y a las %H:%M',  # Ejemplo: "10 de Agosto 2023 a las 11:00"
        'Desde el %d de %B %Y a las %H:%M hasta el %d de %B %Y a las %H:%M',  # Ejemplo: "Desde el 18 de Mayo 2023 a las 11:00 hasta el 23 de Julio 2023 a las 21:00"
        '%d de %B %Y desde las %H:%M',  # Ejemplo: "19 de Mayo 2023 desde las 21:00"
    ]

    for formato in formatos_fecha:
        try:
            fecha = datetime.strptime(fecha_str, formato)
            return fecha.strftime('%Y-%m-%d')
        except ValueError:
            continue

    return ''

def formatear_hora(hora_str):
    formatos_hora = [
        '%H:%M hrs.',  # Ejemplo: "22:00 hrs."
        'a las %H:%M',  # Ejemplo: "a las 11:00"
        'desde las %H:%M',  # Ejemplo: "desde las 21:00"
    ]

    for formato in formatos_hora:
        try:
            hora = datetime.strptime(hora_str, formato)
            return hora.strftime('%H:%M')
        except ValueError:
            continue

    return ''

def descargar_imagen(url, ruta_destino):
    if url == 'predeterminado/sin_imagen.jpg':
        return
    respuesta = requests.get(url, stream=True)
    if respuesta.status_code == 200:
        with open(ruta_destino, 'wb') as f:
            respuesta.raw.decode_content = True
            shutil.copyfileobj(respuesta.raw, f)
    time.sleep(1)

def obtener_extension(url):
    nombre_archivo = os.path.basename(url)
    extension = os.path.splitext(nombre_archivo)[1]
    return extension

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

chrome_driver_path = r"C:\Users\juand\Desktop\EventFind\herramientas_desarrollo\chromedriver_win32\chromedriver.exe"
options = webdriver.ChromeOptions()
options.add_argument('--incognito')
service = Service(executable_path=chrome_driver_path,options=options)
driver = webdriver.Chrome(service=service)

hoy = datetime.datetime.now()
carpeta_fecha = hoy.strftime("%d-%m-%Y")
os.makedirs(carpeta_fecha, exist_ok=True)

url = 'https://ticketplus.cl/s/region-de-coquimbo'
driver.get(url)

html_content = driver.page_source
soup = BeautifulSoup(html_content, "html.parser")
event_divs = soup.find_all("div", {"class": "col-xs-6 col-md-3 m-b-xs p-x-xs element-item"})

event_links = []
for div in event_divs:
    link = div.find("a")["href"]
    event_links.append(f"https://ticketplus.cl{link}")

eventos = []
id_evento = 0

for link in event_links:
    id_evento += 1
    driver.get(link)
    time.sleep(3)

    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')

    script_element = soup.find('script', {'type': 'application/ld+json'})
    event_json = json.loads(script_element.string)

    titulo = event_json['name']
    fecha_hora = event_json['startDate']
    direccion_titulo = event_json['location']['name']
    direccion_detalle = event_json['location']['address']['streetAddress']
    detalle_evento = event_json['description']
    imagen_url = event_json['image']
    evento_url = event_json['url']

    img_element = soup.find('img', {'alt': titulo})
    if img_element:
        img_url = img_element['src'].split('?')[0]

        extension_img = obtener_extension(img_url)
        carpeta_regional = formatear_nombre(f'eventos_region_id_region_nombre')
        carpeta_imagenes = os.path.join(carpeta_fecha, carpeta_regional)
        os.makedirs(carpeta_imagenes, exist_ok=True)
        nombre_imagen = formatear_nombre(f'eventos_region_id_region_nombre_{id_evento}{extension_img}')
        ruta_imagen = os.path.join(carpeta_imagenes, nombre_imagen)
        descargar_imagen(img_url, ruta_imagen)
    else:
        ruta_imagen = ''

    evento = {
        'titulo': titulo,
        'fecha': fecha_hora.split('T')[0],
        'hora': fecha_hora.split('T')[1] if len(fecha_hora.split('T')) > 1 else '',
        'direccionTitulo': direccion_titulo,
        'direccionDetalle': direccion_detalle,
        'detalleEvento': detalle_evento,
        'imagen': ruta_imagen,
        'evento_url': evento_url
    }

    eventos.append(evento)

# Abre el archivo JSON en modo "append"
nombre_archivo_json = formatear_nombre(f'eventos_region_id_region_nombre.json')
nombre_archivo = os.path.join(carpeta_fecha, nombre_archivo_json)
with open(nombre_archivo, 'a', encoding='utf-8') as f:
    # Escribe la lista de eventos en el archivo JSON
    json.dump(eventos, f, ensure_ascii=False, indent=4)
    f.write('\n')

# No olvides cerrar el driver al final del proceso
#driver.quit()

