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

def obtener_extension(url):
    nombre_archivo = os.path.basename(url)
    extension = os.path.splitext(nombre_archivo)[1]
    return extension


def extraer_nombre_region(region_option):
    return region_option.text.strip()


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

# Crea la carpeta con la fecha actual
hoy = datetime.datetime.now()
carpeta_fecha = hoy.strftime("%d-%m-%Y")
os.makedirs(carpeta_fecha, exist_ok=True)



url = 'https://ticketplus.cl/s/region-de-coquimbo'
driver.get(url)


list_regiones = {
    1: "I Región de Tarapacá",
    2: "II Región de Antofagasta",
    3: "III Región de Atacama",
    4: "IV Región de Coquimbo",
    5: "V Región de Valparaíso",
    6: "VI Región del Libertador General Bernardo O'Higgins",
    7: "VII Región del Maule",
    8: "VIII Región del Biobío",
    9: "IX Región de la Araucanía",
    10: "X Región de Los Lagos",
    11: "XI Región de Aysén",
    12: "XII Región de Magallanes y Antártica",
    13: "Región Metropolitana de Santiago",
    14: "XIV Región de Los Ríos",
    15: "XV Región de Arica y Parinacota"
}

for id in list_regiones:

    primera_iteracion = True  # Variable para rastrear si es la primera vez que se ingresa a una región
    id_evento = 0
    region_id     = str(id)
    region_nombre = list_regiones[id]

    # Encuentra el elemento select con el id 'region'
    select_element = driver.find_element(By.ID, 'region')
    # Crea un objeto Select y pásale el elemento encontrado
    select = Select(select_element)
    # Obtén la lista de opciones del select
    opciones_region = select.options
    select.select_by_value(str(id))

    formulario_buscador = driver.find_element(By.ID, "buscador2")
    formulario_buscador.submit()


    # Obtener el número total de páginas en el paginador
    paginador = driver.find_element(By.XPATH, '//section[@class="contenedor"]')
    botones_pagina = paginador.find_elements(By.XPATH, '//input[@class="btn-pag"]')

    total_paginas = 0

    # Comprobar si el botón "Última" está presente en la página actual y actualizar el total de páginas si es necesario
    try:
        ultimo_boton = driver.find_element(By.XPATH, '//input[@class="btn-pag" and @value="Última"]')
        if ultimo_boton:
            url_ultimo_boton = ultimo_boton.find_element(By.XPATH, '..').get_attribute('href')
            total_paginas_actualizado = int(url_ultimo_boton.split('page=')[1].split('&')[0])
            if total_paginas_actualizado > total_paginas:
                total_paginas = total_paginas_actualizado
    except NoSuchElementException:
        #esta excepcion es para controlar si el boton ultima no existe
        if botones_pagina:
            total_paginas = int(botones_pagina[-1].get_attribute('value'))
        else:
            total_paginas = 1
       

    




    # Recorrer todas las páginas y extraer los datos de los eventos
    eventos = []
    for pagina in range(1, total_paginas+1):
        time.sleep(5) 
        print(f"Extrayendo datos de la página {pagina}...")
        # Extraer los datos de los eventos en la página actual
        enlaces_eventos = driver.find_elements(By.XPATH, '//section[@id="listado2"]//ul[@id="grid"]//li//a')
        urls_eventos = [enlace.get_attribute('href') for enlace in enlaces_eventos]
        for url in urls_eventos:
            if primera_iteracion:
                # Elimina todas las imágenes de la carpeta antes de comenzar la extracción para esta región
                carpeta_regional = formatear_nombre(f'eventos_{region_id}_{region_nombre}')
                carpeta_imagenes = os.path.join(carpeta_fecha, carpeta_regional)
                archivos_imagenes = glob.glob(f'{carpeta_imagenes}/*.*')  # Encuentra todos los archivos en la carpeta_imagenes
                for archivo in archivos_imagenes:
                    try:
                        os.remove(archivo)  # Elimina el archivo
                    except OSError as e:
                        print(f"Error al eliminar el archivo: {archivo}. Error: {e.strerror}")
                primera_iteracion = False  # Cambiar el valor a False para que no elimine archivos en las siguientes iteraciones en la misma región
            id_evento += 1
            evento_url = url
            
            time.sleep(random.randint(1, 5))
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            titulo_element = soup.find('section', {'class': 'cont-head-ficha'}).find('h3')
            titulo = titulo_element.text.strip() if titulo_element else ''
            fecha_hora_element = soup.find('section', {'class': 'cont-head-ficha'}).find('i', {'class': 'icon-calendar'})
            fecha_hora = fecha_hora_element.next_sibling.strip() if fecha_hora_element else ''
            direccion_element = soup.find('section', {'class': 'cont-head-ficha'}).find('strong')
            direccion_titulo = direccion_element.text.strip() if direccion_element else ''
            direccion_element = soup.find('section', {'class': 'cont-head-ficha'}).find('div', {'class': 'donde'}).find('p')
            direccion_detalle = direccion_element.text.strip().replace('\n', ' ').replace('\t', '') if direccion_element else ''
            #detalle_evento_element = soup.find('section', {'class': 'cont-evento'})
            #detalle_evento = detalle_evento_element.text.strip().replace('\n', ' ').replace('\t', '') if detalle_evento_element else ''  

            ### Agregado: Extracción del detalle del evento utilizando el nuevo método
            detalle_evento_container = soup.find('section', {'class': 'cont-desc'})
            detalle_evento = ''
            if detalle_evento_container:
                detalle_evento_elements = detalle_evento_container.find_all('p')
                for p in detalle_evento_elements:
                    if p.find('iframe') is None and not p.attrs:
                        detalle_evento += p.text.strip().replace('\n', ' ').replace('\t', '') + ' '
            detalle_evento = detalle_evento.strip()

            # Crear un diccionario con la información obtenida
            evento = {
                'titulo': titulo,
                'fecha': fecha_hora.split(' - ')[0],
                'hora': fecha_hora.split(' - ')[1] if len(fecha_hora.split(' - ')) > 1 else '',
                'direccionTitulo': direccion_titulo,
                'direccionDetalle': direccion_detalle,
                'detalleEvento': detalle_evento,
                'imagen':'',
                'evento_url' : evento_url
            }

            slider = soup.find('div', {'id': 'slider'})
            img_element = slider.find('img') if slider else None

            img_url = img_element['src'] if img_element and img_element.get('src') else 'predeterminado/sin_imagen.jpg'

            #img_url = img_element.get('src', 'predeterminado/sin_imagen.jpg') if img_element else 'predeterminado/sin_imagen.jpg'
            #img_url = img_element['src'] if img_element else ''

            # Descargar la imagen y guardarla en la carpeta correspondiente
            if img_url:
                extension_img = obtener_extension(img_url)
                #carpeta_imagenes = os.path.join(carpeta_fecha, f'eventos_{region_id}_{region_nombre}')
                
                carpeta_regional = formatear_nombre(f'eventos_{region_id}_{region_nombre}')
                carpeta_imagenes = os.path.join(carpeta_fecha, carpeta_regional) 
                
                os.makedirs(carpeta_imagenes, exist_ok=True)
                nombre_imagen = formatear_nombre(f'eventos_{region_id}_{region_nombre}_{id_evento}{extension_img}')
                
                
                
                
                ruta_imagen = os.path.join(carpeta_imagenes, nombre_imagen)
                descargar_imagen(img_url, ruta_imagen)
                evento['imagen'] = ruta_imagen

            # Agregar el diccionario a la lista de eventos
            eventos.append(evento)

            # Vuelve a la página anterior antes de pasar al siguiente enlace
            driver.back()

        # Hacer clic en el botón de siguiente página y esperar a que la página se cargue

        if pagina < total_paginas:
            pagina += 1
            url_pagina_siguiente = f'https://www.passline.com/eventos?q=&region={region_id}&comuna=&mes=&page={pagina}'
            driver.get(url_pagina_siguiente)


            print(f"Extrayendo datos de la página {pagina}...")
        else:
            print("No hay más páginas disponibles")


        #if pagina < total_paginas:
        #    siguiente_pagina = driver.find_element(By.XPATH, f'//a[@href="?page={pagina+1}&region=4&comuna=403"]')
        #    siguiente_pagina.click()
        #    time.sleep(5)  # Esperar a que la página se cargue antes de extraer los datos de los eventos de la siguiente página


    # Guarda la lista de eventos en un archivo JSON con el formato "eventos_id_region_nombre_de_la_region.json"
    #nombre_archivo = os.path.join(carpeta_fecha, f'eventos_{region_id}_{region_nombre}.json')
    nombre_archivo_json = formatear_nombre(f'eventos_{region_id}_{region_nombre}.json')
    nombre_archivo = os.path.join(carpeta_fecha, nombre_archivo_json)
    
    
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(eventos, f, ensure_ascii=False, indent=4)

    # Guardar la lista de eventos en un archivo JSON
    ###with open(r"C:\Users\juand\Desktop\EventFind\scraping\scraper_directo\eventos.json", 'w', encoding='utf-8') as f:
    ###    json.dump(eventos, f, ensure_ascii=False, indent=4)