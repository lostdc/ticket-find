from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener las credenciales y la información de conexión
mongodb_host = os.getenv("MONGODB_HOST")
mongodb_user = os.getenv("MONGODB_USER")
mongodb_password = os.getenv("MONGODB_PASSWORD")
mongodb_database = os.getenv("MONGODB_DATABASE")
mongodb_port = os.getenv("MONGODB_PORT")

# Construir la URI de conexión considerando si el puerto está presente o no
if mongodb_port:
    uri = f"mongodb://{mongodb_user}:{mongodb_password}@{mongodb_host}:{mongodb_port}/{mongodb_database}"
else:
    uri = f"mongodb+srv://{mongodb_user}:{mongodb_password}@{mongodb_host}/{mongodb_database}?retryWrites=true&w=majority"


# Construir la URI de conexión utilizando 'mongodb+srv://' y especificando 'admin' como base de datos para la autenticación
uri = f"mongodb+srv://{mongodb_user}:{mongodb_password}@{mongodb_host}/admin?retryWrites=true&w=majority"

# Conectar a MongoDB
client = MongoClient(uri)
db = client[mongodb_database]

# Conectar a MongoDB
client = MongoClient(uri)
db = client[mongodb_database]

# Crear colecciones si no existen
colecciones = db.list_collection_names()
if 'regiones' not in colecciones:
    db.create_collection('regiones')

if 'eventos' not in colecciones:
    db.create_collection('eventos')

# Datos de regiones
regiones_data = [
        {
        "_id": 1,
        "nombre": "I Región de Tarapacá",
        "link": "https://ticketplus.cl/s/region-de-tarapaca"
    },
    {
        "_id": 2,
        "nombre": "II Región de Antofagasta",
        "link": "https://ticketplus.cl/s/region-de-antofagasta"
    },
    {
        "_id": 3,
        "nombre": "III Región de Atacama",
        "link": "https://ticketplus.cl/s/region-de-atacama"
    },
    {
        "_id": 4,
        "nombre": "IV Región de Coquimbo",
        "link": "https://ticketplus.cl/s/region-de-coquimbo"
    },
    {
        "_id": 5,
        "nombre": "V Región de Valparaíso",
        "link": "https://ticketplus.cl/s/region-de-valparaiso"
    },
    {
        "_id": 6,        
        "nombre": "VI Región del Libertador General Bernardo O'Higgins",
        "link": "https://ticketplus.cl/s/region-del-libertador-general-bernardo-o-higgins"
    },
    {
        "_id": 7,
        "nombre": "VII Región del Maule",
        "link": "https://ticketplus.cl/s/region-del-maule"
    },
    {
        "_id": 8,
        "nombre": "VIII Región del Biobío",
        "link": "https://ticketplus.cl/s/region-del-bio-bio"
    },
    {
        "_id": 9,
        "nombre": "IX Región de la Araucanía",
        "link": "https://ticketplus.cl/s/region-de-la-araucania"
    },
    {
        "_id": 10,
        "nombre": "X Región de Los Lagos",
        "link": "https://ticketplus.cl/s/region-de-los-lagos"
    },
    {
        "_id": 11,
        "nombre": "XI Región de Aysén",
        "link": "https://ticketplus.cl/s/region-de-aysen"
    },
    {
        "_id": 12,
        "nombre": "XII Región de Magallanes y Antártica",
        "link": "https://ticketplus.cl/s/region-de-magallanes-y-de-la-antartica-chilena"
    },
    {
        "_id": 13,
        "nombre": "Región Metropolitana de Santiago",
        "link": "https://ticketplus.cl/s/region-metropolitana"
    },
    {
        "_id": 14,
        "nombre": "XIV Región de Los Ríos",
        "link": "https://ticketplus.cl/s/region-de-los-rios"
    },
    {
        "_id": 15,
        "nombre": "XV Región de Arica y Parinacota",
        "link": "https://ticketplus.cl/s/region-de-arica-y-parinacota"
    }
    # Añade aquí el resto de tus datos...
]

# Insertar datos en la colección 'regiones'
db.regiones.insert_many(regiones_data)

print("Base de datos event_find_db inicializada con la colección regiones.")
