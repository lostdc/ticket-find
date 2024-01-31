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
from pprint import pprint
from dotenv import load_dotenv
import pymongo
import boto3

# Cargar variables de entorno desde el archivo .env
load_dotenv()
# Obtener las variables de entorno necesarias
mongodb_host      = os.getenv("MONGODB_HOST", "mongodb")
mongodb_port      = os.getenv("MONGODB_PORT", "27017")
mongodb_user      =  os.getenv("MONGODB_USER", "mongodb")
mongodb_password  = os.getenv("MONGODB_PASSWORD", "pass1234")
mongodb_database  = os.getenv("MONGODB_DATABASE", "event_find_db")

#variables de entorno aws
bucket_name       = os.getenv("BUCKET_NAME", "event-find")
# Crear un cliente de S3


s3 = boto3.client(
    's3',
    aws_access_key_id       = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key   = os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Construir la URI de conexión considerando si el puerto está presente o no
if mongodb_port:
    mongodb_uri = f"mongodb://{mongodb_user}:{mongodb_password}@{mongodb_host}:{mongodb_port}/{mongodb_database}"
else:
    mongodb_uri = f"mongodb+srv://{mongodb_user}:{mongodb_password}@{mongodb_host}/{mongodb_database}?retryWrites=true&w=majority"

# Construir la URI de conexión utilizando 'mongodb+srv://' y especificando 'admin' como base de datos para la autenticación
mongodb_uri = f"mongodb+srv://{mongodb_user}:{mongodb_password}@{mongodb_host}/admin?retryWrites=true&w=majority"

# Conectarse a la base de datos MongoDB
cliente = pymongo.MongoClient(mongodb_uri)
db = cliente[mongodb_database]

regiones = list(db["regiones"].find())

# Inicializamos la variable list_regiones como un diccionario vacío
list_regiones = {}

# Traemos los datos de la base de datos MongoDB
regiones = list(db["regiones"].find())

# Iteramos sobre los datos de la base de datos y los agregamos a list_regiones
for idx, region in enumerate(regiones, start=1):
    list_regiones[idx] = {"nombre": region['nombre'], "link": region['link']}


# Configura las opciones de Chrome para el modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecuta Chrome en modo headless
chrome_options.add_argument("--no-sandbox")  # Desactiva el modo sandbox para Chrome
chrome_options.add_argument("--disable-dev-shm-usage")  # Evita problemas en contenedores

# Inicializa el driver de Chrome con las opciones configuradas
driver = webdriver.Chrome(options=chrome_options)

hoy = datetime.datetime.now()
carpeta_fecha = hoy.strftime("%d-%m-%Y")
os.makedirs(carpeta_fecha, exist_ok=True)

fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")


eventos = []
id_evento = 0
eventos_activos_urls = []
help.escribir_log("Inicio del proceso de scraping", fecha_actual)

for id_region, region in list_regiones.items():
    url = region["link"]

    driver.get(url)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    
    event_divs = [div for div in soup.find_all("div", {"class": "col-xs-6 col-md-3 m-b-xs p-x-xs element-item"})
              if div.get('style') != "display: none;"]

    event_links = []
    for div in event_divs:
        link = div.find("a")["href"]
        evento_url = f"https://ticketplus.cl{link}"
        # Verifica si el evento ya existe en la base de datos
        evento_existente = coleccion_eventos.find_one({"evento_url": evento_url})
        if evento_existente:
            # Si existe, actualiza solo el campo 'activo' a True y continua con el siguiente
            coleccion_eventos.update_one({"_id": evento_existente["_id"]}, {"$set": {"activo": True}})
            continue

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
        imagen_url = event_json['image'].replace("https://ticketplus.cl/", "", 1) 

        evento_url = event_json['url']
        latitud = event_json['location']['geo']['latitude']
        longitud = event_json['location']['geo']['longitude']

        #img_element = soup.find('img', {'alt': titulo})
        img_element = imagen_url
        if img_element:
            #img_url = img_element['src'].split('?')[0]
            img_url = img_element.split('?')[0]
            extension_img = help.obtener_extension(img_url)

            #subir a s3 borrar parte local
            #en la siguiente local borrar
            carpeta_regional = help.formatear_nombre(f'eventos_{id_region}_{region["nombre"]}')
            carpeta_imagenes = os.path.join(carpeta_fecha, carpeta_regional)

            os.makedirs(carpeta_imagenes, exist_ok=True)
            nombre_imagen = help.formatear_nombre(f'eventos_{id_region}_{region["nombre"]}_{id_evento}{extension_img}')
            ruta_imagen = os.path.join(carpeta_imagenes, nombre_imagen)
            help.descargar_imagen(img_url, ruta_imagen)

            # Define la ruta en S3 donde quieres guardar la imagen
            s3_file_path = f"eventos/{carpeta_fecha}/{carpeta_regional}/{nombre_imagen}"
            print(s3_file_path)

            # Subir la imagen a S3
            help.subir_imagen_s3(img_url, bucket_name, s3_file_path, s3)


            # Actualiza el JSON con la ruta de la imagen en S3
            ruta_imagen_json = f"{s3_file_path}"
            ruta_imagen_json_s23 = f"https://event-find.s3.amazonaws.com/{s3_file_path}"


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
            'id_region': id_region,
            'region': region["nombre"],
            'direccionTitulo': direccion_titulo,
            'direccionDetalle': direccion_detalle,
            'detalleEvento': detalle_evento,
            #'imagen': ruta_imagen_json,  # Actualiza el valor de la propiedad imagen en el JSON
            'imagen' : ruta_imagen_json_s23,
            'evento_url': evento_url,
            'lat': latitud,  # Agrega la latitud
            'long': longitud,  # Agrega la longitud
            'logo' : 'logo_ticketplus.png',
            'fecha_obtencion' : carpeta_fecha,
            'activo' : True,
            'ubicacion_geo': {  # Agrega la ubicación en formato GeoJSON
                'type': 'Point',
                'coordinates': [float(longitud), float(latitud)]
            }
        }
        eventos.append(evento)

        #aqui realizaremos un corte para ingresar solo uno y probar
        # Acceder a la colección 'eventos'
        coleccion_eventos = db.eventos
        # Insertar el documento en la colección
        help.verificar_y_actualizar_evento(evento, coleccion_eventos)
        coleccion_eventos.insert_one(evento)


driver.quit()
help.escribir_log("Finalización del proceso de scraping", fecha_actual)


