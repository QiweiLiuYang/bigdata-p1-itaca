import glob, hashlib, os, json, logging, sys
import xml.etree.ElementTree as ET
from datetime import date

# Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingesta_itaca_xml")


# Carpeta de origen de los datos (En mi sistema WSL está en /mnt/c/Users/qiwei/Downloads/Analisis_Academico/)
ORIGIN = sys.argv[1] if len(sys.argv) == 2 else None


# Información a buscar

TABLAS = ["alumnos", "cursos", "calificaciones", "contenidos"]

CAMPOS = {
    "alumnos": ["NIA", "sexo", "nacionalidad", "provincia", "municipio", "ensenanza", "curso", "grupo", "turno", "linea", "modalidad", "repite", "estado_matricula", "tipo_matricula", "fecha_matricula", "fecha_ingreso_centro"],
    "cursos": ["codigo", "nombre_cas", "nombre_val", "abreviatura", "ensenanza", "padre"],
    "calificaciones": ["evaluacion", "alumno", "ensenanza", "curso", "contenido", "bloque_contenido", "nota_numerica", "tipo_nota"],
    "contenidos": ["codigo", "nombre_cas", "nombre_val", "ensenanza", "curso"]
}

# Parsear xml

def parsear_xml(tabla: str) -> list[dict]:
    registros = []
    CAMPOS_NIA = ["NIA", "alumno"]

    rutas = sorted(glob.glob(f"{ORIGIN}/*/{tabla}.xml"))
    for ruta in rutas:
        raiz = ET.parse(ruta).getroot()
        anyo = raiz.attrib["curso"]
        filas = raiz.find(tabla)

        for fila in filas:
            for campo in CAMPOS_NIA:
                if campo in fila.attrib:
                    fila.attrib[campo] = anonimizar_nia(fila.attrib[campo])
            registros.append({"anyo": anyo} | {key: fila.get(key) for key in CAMPOS[tabla]})

    return registros


def anonimizar_nia(nia: str) -> str:
    return hashlib.sha256(str(nia).encode()).hexdigest()[:10]


def guardar(datos: list, nombre: str) -> None:
    fecha = date.today().isoformat()
    ruta = f"data/raw/{fecha}"
    
    os.makedirs(ruta, exist_ok=True)

    with open(f"{ruta}/{nombre}.json", "w", encoding="UTF-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    logger.info(f"Guardados %d registros en %s", len(datos), ruta)


if __name__ == "__main__":
    if ORIGIN == None:
        logger.error("Has introducido una URI inválida o has introducido más de un argumento")
        exit(1)
    for tabla in TABLAS:
        try:
            guardar(parsear_xml(tabla), tabla)
        except (OSError, ET.ParseError) as e:
            logger.error(str(e))