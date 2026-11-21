from pymongo import MongoClient

cliente = MongoClient("mongodb://admin:admin@localhost:27017/")
db = cliente["itaca"]
coleccion = db["cursos"]

pipeline = [
    {"$match": {"nombre_cas": {"$regex": "^(Primero|Segundo)"}}},
    {"$lookup": {"from": "cursos", "localField": "padre", "foreignField": "codigo", "as": "ciclo"}},
    {"$unwind": "$ciclo"},
    {"$lookup": {"from": "ciclo", "localField": "ciclo.padre", "foreignField": "codigo", "as": "grado"}},
    {"$unwind": "$grado"},
    {"$lookup": {"from": "grado", "localField": "grado.padre", "foreignField": "codigo", "as": "familia"}},
    {"$unwind": "$familia"},

    {"$project": {
        "_id": 0,
        "familia": "$familia.nombre_cas",
        "grado": "$grado.nombre_cas",
        "ciclo": "$ciclo.nombre_cas",
        "ciclo_abreviatura": "$ciclo.abreviatura",
        "primseg": {"$arrayElemAt": [{"$split": ["$nombre_cas", " "]}, 0]},
        "curso_codigo": "$codigo",
        "curso_abreviatura": "$abreviatura"
    }},
    {"$out": "curso_planos"}
]

coleccion.aggregate(pipeline)
print("Coleccion cursos_planos creada: ", db["cursos_planos"].count_documents({}), "documentos")