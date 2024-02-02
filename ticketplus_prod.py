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
from urllib.parse import urljoin
from mongo_helper import conectar_mongo
from s3_helper import conectar_s3, subir_imagen_s3



def procesar_evento(evento, s3, db, bucket_name, carpeta_fecha, intentos=3, update = False ,evento_existente =False ):
    max_intentos = 5
    try:
        coleccion_eventos = db.eventos
        # Verificar si el evento ya existe
        #print("evento a insertar")
        #pprint(evento)

        if(update):
            coleccion_eventos.update_one({"_id": evento_existente["_id"]}, {"$set": {"activo": True}})
            help.escribir_log("El evento ya existe actualizamos")
        else:
                print("El evento no existe lo registramos")
                # Procesar la descarga de la imagen y subirla a S3
                img_url = evento['img_ticketplus']
                #img_url = img_url.split('?')[0]  # Limpia la URL de la imagen
                nombre_imagen = help.limpiar_y_formatear_nombre(f"evento_{evento['id_region']}_{evento['titulo']}.jpg")
                s3_file_path = f"eventos/{carpeta_fecha}/{nombre_imagen}"

                # Subir la imagen a S3 y actualizar la ruta de la imagen en el evento
                subir_imagen_s3(img_url, bucket_name, s3_file_path, s3)
                evento['imagen'] = f"https://event-find.s3.amazonaws.com/{s3_file_path}"

                # Insertar el evento en MongoDB
                print("este es el evento que insertaremos")
                pprint(evento)
                coleccion_eventos.insert_one(evento)
    except Exception as e:
        if intentos < max_intentos:
            help.escribir_log("reintento: " + str(intentos))
            time.sleep(2 ** intentos)  # Backoff exponencial
            procesar_evento(evento, s3, db, bucket_name, carpeta_fecha, intentos + 1)
        else:
            # Log de errores
            help.escribir_log(f"Error en evento {evento['titulo']}: {str(e)}")



try:
    # Cargar variables de entorno desde el archivo .env
    load_dotenv()
    #variables de entorno aws
    bucket_name       = os.getenv("BUCKET_NAME", "event-find")
    # Crear un cliente de S3
    s3 = conectar_s3()
    db = conectar_mongo()

    regiones = list(db["regiones"].find())

    # Inicializamos la variable list_regiones como un diccionario vacío
    list_regiones = {}

    # Traemos los datos de la base de datos MongoDB
    regiones = list(db["regiones"].find())
    coleccion_eventos = db.eventos

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
    driver.set_page_load_timeout(60)  

    
    hoy = datetime.datetime.now()

    carpeta_fecha = hoy.strftime("%d-%m-%Y")
    os.makedirs(carpeta_fecha, exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")

    eventos = []
    id_evento = 0
    eventos_activos_urls = []
    help.escribir_log("Inicio del proceso de scraping")

    for id_region, region in list_regiones.items():

        help.escribir_log(f"Iniciando scraping para la región: {region['nombre']}")
        url = region["link"]

        driver.get(url)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        
        event_divs = [div for div in soup.find_all("div", {"class": "col-xs-6 col-md-3 m-b-xs p-x-xs element-item"})
                if div.get('style') != "display: none;"]

        event_links = []
        for div in event_divs:
            link = div.find("a")["href"]
            base_url = "https://ticketplus.cl"

            #ESTE ES EL LINK DEL EVENTO
            evento_url = urljoin(base_url, link)
            print("imprimimos el link con el evento")
            pprint(evento_url)

            #evento_url = f"https://ticketplus.cl{link}"

         
            # Verifica si el evento ya existe en la base de datos
            evento_existente = coleccion_eventos.find_one({"evento_url": evento_url})
            print("existe o no el evento? NONE no existe, objeto si existe ")
            pprint(evento_existente)
            if evento_existente:
                # Si existe, actualiza solo el campo 'activo' a True y continua con el siguiente
                
                procesar_evento(None, s3, db, bucket_name, carpeta_fecha,3, True, evento_existente)
                #coleccion_eventos.update_one({"_id": evento_existente["_id"]}, {"$set": {"activo": True}})
                #help.escribir_log("El evento ya existe")
                continue

            event_links.append(evento_url)

        eventos = []
        id_evento = 0  # Inicializa el contador para cFada región

        print("event links")
        pprint(event_links)
  

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

            #evento_url = event_json['url'] este debe estar weando
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
                carpeta_regional = help.limpiar_y_formatear_nombre(f'eventos_{id_region}_{region["nombre"]}')


                carpeta_imagenes = os.path.join(carpeta_fecha, carpeta_regional)
                #os.makedirs(carpeta_imagenes, exist_ok=True)


                nombre_imagen = help.limpiar_y_formatear_nombre(f'eventos_{id_region}_{region["nombre"]}_{id_evento}{extension_img}')


            
                #ruta_imagen = os.path.join(carpeta_imagenes, nombre_imagen)
                #help.descargar_imagen(img_url, ruta_imagen)

                # Define la ruta en S3 donde quieres guardar la imagen
                s3_file_path = f"eventos/{carpeta_fecha}/{carpeta_regional}/{nombre_imagen}"

                # Subir la imagen a S3
                ###subir_imagen_s3(img_url, bucket_name, s3_file_path, s3)


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
                'titulo': help.quitar_html(titulo),
                'fecha': fecha_hora.split('T')[0],
                'hora': fecha_hora.split('T')[1] if len(fecha_hora.split('T')) > 1 else '',
                'id_region': id_region,
                'region': region["nombre"],
                'direccionTitulo': direccion_titulo,
                'direccionDetalle': direccion_detalle,
                'detalleEvento': help.quitar_html(detalle_evento),
                #'imagen': ruta_imagen_json,  # Actualiza el valor de la propiedad imagen en el JSON
                'imagen' : ruta_imagen_json_s23,
                'img_ticketplus' : img_url,
                'evento_url': link,
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


            # Llamar a procesar_evento en lugar de la lógica de inserción directa

            #aqui falta img_url porque la saca de evento que es incorrecto no hay nada que descargar de hay

            procesar_evento(evento, s3, db, bucket_name, carpeta_fecha, 3,False)


            #eventos.append(evento)

            #aqui realizaremos un corte para ingresar solo uno y probar
            # Acceder a la colección 'eventos'
            #coleccion_eventos = db.eventos
            #coleccion_eventos.insert_one(evento)


    driver.quit()
    help.escribir_log("Finalización del proceso de scraping")

except Exception as e:
    fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")
    help.escribir_log(f"Error general en el programa: {str(e)}")
    raise





