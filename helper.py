import os
import unicodedata
import datetime
import requests
import shutil
import time
import re
import datetime
import html


def limpiar_cadena(cadena):
    # Reemplaza los caracteres no válidos con espacios en blanco
    cadena_limpia = re.sub(r'[^\x00-\x7F]+', ' ', cadena)
    # Codifica la cadena en UTF-8
    cadena_utf8 = cadena_limpia.encode('utf-8', 'ignore').decode('utf-8')
    return cadena_utf8

def formatear_nombre(nombre):
    nombre = nombre.lower()
    nombre = nombre.replace(" ", "_")
    nombre = unicodedata.normalize("NFKD", nombre).encode("ASCII", "ignore").decode("ASCII")
    return nombre

def quitar_html(nombre):
    # Decodifica entidades HTML
    nombre = html.unescape(nombre)
    return nombre

def limpiar_y_formatear_nombre(nombre):
    # Decodifica entidades HTML
    nombre = html.unescape(nombre)
    # Luego aplica la función formatear_nombre
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

#def subir_imagen_s3(url, bucket_name, s3_file_path, s3_client):
#    if url == 'predeterminado/sin_imagen.jpg':
#        return
#    respuesta = requests.get(url, stream=True)
#    if respuesta.status_code == 200:
#        print (respuesta.status_code)
#        respuesta.raw.decode_content = True
#        # Sube directamente a S3
#        s3_client.upload_fileobj(respuesta.raw, bucket_name, s3_file_path)
#    time.sleep(1)

def subir_imagen_s3(url, bucket_name, s3_file_path, s3_client):
    if url == 'predeterminado/sin_imagen.jpg':
        return
    respuesta = requests.get(url, stream=True)
    if respuesta.status_code == 200:
        respuesta.raw.decode_content = True
        s3_client.upload_fileobj(respuesta.raw, bucket_name, s3_file_path)
    time.sleep(1)

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



def escribir_log(mensaje):
    fecha_actual = datetime.datetime.now()
    fecha_formateada = fecha_actual.strftime("%d-%m-%Y")

    # Crear la ruta de la carpeta siguiendo la estructura log/log-30-01-2024/
    carpeta_log = os.path.join("log", f"log-{fecha_formateada}")
    os.makedirs(carpeta_log, exist_ok=True)

    # Nombre del archivo de log como log_fecha.txt
    nombre_archivo_log = f"log_{fecha_actual.strftime('%Y-%m-%d')}.txt"
    ruta_archivo_log = os.path.join(carpeta_log, nombre_archivo_log)

    # Mensaje completo con fecha y hora
    mensaje_completo = f"{fecha_actual.strftime('%Y-%m-%d %H:%M:%S')} - {mensaje}\n"

    # Escribir en el archivo de log
    with open(ruta_archivo_log, 'a', encoding='utf-8') as archivo_log:
        archivo_log.write(mensaje_completo)

    # Imprimir el mensaje en la consola
    print(mensaje_completo)



def limpiar_nombre_archivo(nombre):
    # Decodificar entidades HTML
    nombre = html.unescape(nombre)
    
    # Reemplazar caracteres especiales con un subrayado o eliminarlos
    nombre = nombre.replace('"', '')  # Elimina comillas dobles
    nombre = nombre.replace("'", '')  # Elimina apóstrofos
    nombre = nombre.replace('&', 'y')  # Reemplaza '&' con 'y'
    
    # Opcional: reemplazar espacios con guiones para mejorar la legibilidad de la URL
    nombre = nombre.replace(' ', '_')
    
    # Eliminar o reemplazar otros caracteres especiales según sea necesario
    # nombre = re.sub(r'[^\w\s-]', '', nombre)  # Ejemplo usando expresiones regulares para mantener solo letras, números, guiones y espacios
    
    return nombre