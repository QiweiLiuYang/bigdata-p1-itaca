import json
from pymongo import MongoClient
from pathlib import Path

cliente = MongoClient("mongodb://admin:admin@localhost:27017/")
db = cliente["itaca"]

RAW = Path(__file__).resolve().parent.parent / "data" / "raw" / "2026-10-29"

def leer_json(nombre: str) -> list[dict]:
    with open(RAW/nombre, encoding="UTF-8") as f:
        return json.load(f)


def insertar(coleccion: str, documento: list[dict]) -> None:
    db.drop_collection(coleccion)
    db[coleccion].insert_many(documento)
    print(f"{coleccion}: Insertado {len(documento)} documentos")


def cargar_contenidos() -> None:
    contenidos = leer_json("contenidos.json")
    documentos = [
        {
            "anyo": c["anyo"],
            "curso": c["curso"],
            "modulo": c["codigo"],
            "nombre_modulo": c["nombre_cas"]
        } for c in contenidos
    ]
    insertar("contenidos", documentos)


def cargar_alumnos() -> None:
    alumnos = leer_json("alumnos.json")
    documentos = [
        {
            "nia": a["nia"],
            "anyo": a["anyo"],
            "curso": a["curso"],
            "turno": a["turno"],
            "grupo": a["grupo"]
        } for a in alumnos
    ]
    insertar("alumnos", documentos)


def cargar_calificaciones() -> None:
    calificaciones = leer_json("calificaciones.json")
    documentos = [
        {
            "nia": c["alumno"],
            "anyo": c["anyo"],
            "curso": c["curso"],
            "modulo": c["contenido"],
            "nota": c["nota_numerica"],
            "evaluacion": c["evaluacion"]
        } for c in calificaciones
    ]
    insertar("calificaciones", documentos)


def cargar_cursos() -> None:
    cursos = leer_json("cursos")
    documentos = [
        {
            "anyo": c["anyo"],
            "codigo": c["codigo"],
            "nombre_curso": c["nombre_cas"],
            "padre": c["padre"]
        } for c in cursos
    ]


if __name__ == "__main__":
    cargar_contenidos()
    cargar_alumnos()
    cargar_calificaciones()
    cargar_cursos()
    print("Carga completada.")