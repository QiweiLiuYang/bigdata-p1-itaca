from pymongo import MongoClient

cliente = MongoClient("mongodb://admin:admin@localhost:27017/")
db = cliente["itaca"]
coleccion = db["contenidos"]

pipeline = [
    {"$lookup": {
        "from": "cursos_planos",
        "let": {"curso": "$curso", "ensenanza": "$ensenanza"},
        "pipeline": [
            {"$match": {
                "$expr": {
                    "$and": [
                        {"$eq": ["$curso_codigo", "$$curso"]},
                    ]
                }
            }},
            {"$project": {"_id": 0}}
        ],
        "as": "curso_datos"
    }},
    {"$unwind": {"path": "$curso_datos", "preserveNullAndEmptyArrays": True}},
    {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$$ROOT", "$curso_datos"]}}},
    {"$project": {"curso_datos": 0}},
    {"$out": "modulos"}
]

coleccion.aggregate(pipeline)
db["modulos"].create_index([("modulo", 1), ("anyo", 1), ("curso", 1)], unique=True)
print("Colección modulos creada: ", db["modulos"].count_documents({}), "documentos")