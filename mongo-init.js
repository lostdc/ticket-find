//db = db.getSiblingDB('EventFindDB');
//db.createCollection('miColeccionInicial');
//db.miColeccionInicial.insert({ initialized: true });

db = db.getSiblingDB('event_find_db'); // Crear o seleccionar la base de datos event_find_bd

// Crear la colección "regiones" si no existe
if (!db.getCollectionNames().includes("regiones")) {
    db.createCollection("regiones");





}

// Crear la colección "eventos" si no existe
if (!db.getCollectionNames().includes("eventos")) {
    db.createCollection("eventos");
}

// Datos de las regiones
var regionesData = [
    {
        _id: 1,
        nombre: "I Región de Tarapacá",
        link: "https://ticketplus.cl/s/region-de-tarapaca"
    },
    {
        _id: 2,
        nombre: "II Región de Antofagasta",
        link: "https://ticketplus.cl/s/region-de-antofagasta"
    },
    {
        _id: 3,
        nombre: "III Región de Atacama",
        link: "https://ticketplus.cl/s/region-de-atacama"
    },
    {
        _id: 4,
        nombre: "IV Región de Coquimbo",
        link: "https://ticketplus.cl/s/region-de-coquimbo"
    },
    {
        _id: 5,
        nombre: "V Región de Valparaíso",
        link: "https://ticketplus.cl/s/region-de-valparaiso"
    },
    {
        _id: 6,        
        nombre: "VI Región del Libertador General Bernardo O'Higgins",
        link: "https://ticketplus.cl/s/region-del-libertador-general-bernardo-o-higgins"
    },
    {
        _id: 7,
        nombre: "VII Región del Maule",
        link: "https://ticketplus.cl/s/region-del-maule"
    },
    {
        _id: 8,
        nombre: "VIII Región del Biobío",
        link: "https://ticketplus.cl/s/region-del-bio-bio"
    },
    {
        _id: 9,
        nombre: "IX Región de la Araucanía",
        link: "https://ticketplus.cl/s/region-de-la-araucania"
    },
    {
        _id: 10,
        nombre: "X Región de Los Lagos",
        link: "https://ticketplus.cl/s/region-de-los-lagos"
    },
    {
        _id: 11,
        nombre: "XI Región de Aysén",
        link: "https://ticketplus.cl/s/region-de-aysen"
    },
    {
        _id: 12,
        nombre: "XII Región de Magallanes y Antártica",
        link: "https://ticketplus.cl/s/region-de-magallanes-y-de-la-antartica-chilena"
    },
    {
        _id: 13,
        nombre: "Región Metropolitana de Santiago",
        link: "https://ticketplus.cl/s/region-metropolitana"
    },
    {
        _id: 14,
        nombre: "XIV Región de Los Ríos",
        link: "https://ticketplus.cl/s/region-de-los-rios"
    },
    {
        _id: 15,
        nombre: "XV Región de Arica y Parinacota",
        link: "https://ticketplus.cl/s/region-de-arica-y-parinacota"
    }
];

// Insertar los datos en la colección "regiones"
db.regiones.insert(regionesData);

// Mensaje de confirmación
print("Base de datos event_find_db inicializada con la colección regiones.");

