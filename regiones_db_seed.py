import os
from dotenv import load_dotenv
import pymongo

# Cargar variables de entorno desde el archivo .env
load_dotenv()
# Obtener las variables de entorno necesarias

mongodb_host      = os.getenv("MONGODB_HOST", "mongodb")
mongodb_port      = os.getenv("MONGODB_PORT", "27017")
mongodb_user      =  os.getenv("MONGODB_USER", "mongodb")
mongodb_password  = os.getenv("MONGODB_PASSWORD", "pass1234")
mongodb_database  = os.getenv("MONGODB_DATABASE", "regiones")
#mongodb_uri       = f"mongodb://{mongodb_user}:{mongodb_password}@{mongodb_host}:{mongodb_port}/{mongodb_database}"

# Construir la URI de conexión
mongodb_uri       = f"mongodb://{mongodb_user}:{mongodb_password}@{mongodb_host}:{mongodb_port}"


# Datos de las regiones
list_regiones = {
    1:  {"nombre": "I Región de Tarapacá", "link": "https://ticketplus.cl/s/region-de-tarapaca"},
    2:  {"nombre": "II Región de Antofagasta", "link": "https://ticketplus.cl/s/region-de-antofagasta"},
    3:  {"nombre": "III Región de Atacama", "link": "https://ticketplus.cl/s/region-de-atacama"},
    4:  {"nombre": "IV Región de Coquimbo", "link": "https://ticketplus.cl/s/region-de-coquimbo"},
    5:  {"nombre": "V Región de Valparaíso", "link": "https://ticketplus.cl/s/region-de-valparaiso"},
    6:  {"nombre": "VI Región del Libertador General Bernardo O'Higgins", "link": "https://ticketplus.cl/s/region-del-libertador-general-bernardo-o-higgins"},
    7:  {"nombre": "VII Región del Maule", "link": "https://ticketplus.cl/s/region-del-maule"},
    8:  {"nombre": "VIII Región del Biobío", "link": "https://ticketplus.cl/s/region-del-bio-bio"},
    9:  {"nombre": "IX Región de la Araucanía", "link": "https://ticketplus.cl/s/region-de-la-araucania"},
    10: {"nombre": "X Región de Los Lagos", "link": "https://ticketplus.cl/s/region-de-los-lagos"},
    11: {"nombre": "XI Región de Aysén", "link": "https://ticketplus.cl/s/region-de-aysen"},
    12: {"nombre": "XII Región de Magallanes y Antártica", "link": "https://ticketplus.cl/s/region-de-magallanes-y-de-la-antartica-chilena"},
    13: {"nombre": "Región Metropolitana de Santiago", "link": "https://ticketplus.cl/s/region-metropolitana"},
    14: {"nombre": "XIV Región de Los Ríos", "link": "https://ticketplus.cl/s/region-de-los-rios"},
    15: {"nombre": "XV Región de Arica y Parinacota", "link": "https://ticketplus.cl/s/region-de-arica-y-parinacota"}
}


# Conectarse a la base de datos MongoDB
cliente = pymongo.MongoClient(mongodb_uri)

# Crear una colección llamada 'regiones' en la base de datos
db = cliente[mongodb_database]
coleccion = db["regiones"]

# Insertar las regiones en la colección
for region_id, region_data in list_regiones.items():
    coleccion.insert_one({"_id": region_id, **region_data})



# Obtener todas las regiones desde la colección 'regiones'
regiones = list(db["regiones"].find())

# Imprimir las regiones
for region in regiones:
    print(f"Nombre: {region['nombre']}, Link: {region['link']}")


# Cerrar la conexión a MongoDB
cliente.close()

print("La base de datos y la colección 'regiones' se han creado y las regiones se han insertado en MongoDB.")
print()