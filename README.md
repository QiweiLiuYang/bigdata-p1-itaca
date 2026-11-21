# Proyecto 1 - ITACA

## Descripción y objetivo

El objetivo será construir un **dashboard** (cuadro de mandos) de análisis académico usando **Power BI** a partir de datos *"reales"* en formato **XML** extraídos de la plataforma **ITACA** de la **Consellería de Educación**.

## Arquitectura

Usaremos una arquitectura **Batch**.

Tecnologías usadas:
- MongoDB
- Spark
- Airflow
- Power BI 

```mermaid
graph LR
    A[Fuente de datos] --> B[Modelado]
    B --> C[Data Lake]
    C --> D[ETL con Spark]
    D --> E[Automatización del pipeline]
    E --> F[Dashboard]
    F --> G[Modelo predictivo]
```

## Fuentes de datos

Cuatro tablas exportadas de ITACA como ficheros XML:
- Alumnos
- Contenidos
- Calificaciones
- Cursos

De los cuales consumiremos las siguientes columnas:
| Tabla | Contenido | Campos Clave |
| --- | --- | --- |
| Alumnos | Un registro por alumno y año académico | NIA, sexo, nacionalidad, provincia, municipio, ensenanza, curso, grupo, turno, linea,modalidad, repite, estado_matricula, tipo_matricula, fecha_matricula, fecha_ingreso_centro |
| Contenidos | Módulos que se imparten en cada curso | codigo, nombre_cas, nombre_val, ensenanza, curso |
| Calificaciones | Nota de cada alumno en cada módulo y evaluación | evaluacion, alumno, ensenanza, curso, contenido,bloque_contenido, nota_numerica, tipo_nota |
| Cursos | Catálogo jerarquico de cursos y ciclos formativos | codigo, nombre_cas, nombre_val, abreviatura, ensenanza, padre |


| Fuente | URL / Origen | Formato | Frecuencia actualización | Licencia | Última ingesta |
| --- | --- | --- | --- | --- | --- |
| AULES | ITACA | XML | Única | SIN LICENCIA | 29/10/2026 |

>[!NOTE]
La tabla de arriba no es definitivo, se irá actualizando a medida que avance el proyecto.

## Estructura del repositorio

Estas son las carpetas del repositorio:

| Carpeta | Contenido |
| --- | --- |
| dashboard/ | Vacía de momento |
| etl | Scripts de carga y transformación en MongoDB |
| docs | Capturas de las prácticas |
| data/curated | Vacía de momento |
| data/processed | Vacía de momento |
| data/raw | Resultados en .json de la ingesta |
| ingesta | Scripts para ingestar |

## Entorno

### Anclar la versión de python del entorno

Usamos pyenv para que siempre use la misma versión:
`pyenv local 3.14.4`

### Crear el entorno

Usaremos un entorno aislado para no tener conflictos con los paquetes.
`python -m venv .venv`

Lo activamos con:
`source .venv/bin/activate`

Lo desactivamos escribiendo `deactivate` en la terminal.

### Requisitos del proyecto

Los requisitos están recogidos en **requirements.txt**. Se instala con:
`pip install -r requirements.txt`

### Como desplegar el entorno

Con el **.env.example** que nos descargaremos, lo copiamos al que utiliza el repositorio y cumplimentamos los datos que sean necesarios.
`cp .env.example .env`

Levantamos los contenedores en modo *detached* con:
`docker compose up -d`

Para mirar que contenedores tenemos:
`docker compose ps`

Para parar el contenedor con:
>[!WARNING]
Perderemos los datos que no estén guardados en volumenes persistidos

`docker compose down`

## Como realizar la ingesta

Para realizar la ingesta, deberás de tener tus datos estructurado en una carpeta general y dentro de ella una/unas carpetas con el curso (por ejemplo 2021-22) y dentro de ella los 4 ficheros xml. Con esta estructura:
```
Carpeta
    2021-22
        alumnos.xml
        ...
    2022-23
        alumnos.xml
        ...
    ...
```

Ejecutas el siguiente comando desde la raíz del proyecto:
`python ingesta/ingesta_itaca_xml.py ruta`
Donde **ruta** es la ruta absoluta/relativa a donde tengas la carpeta con los datos.

El resultado quedará en la carpeta **data/raw**

## Como cargar los datos en MongoDB

Con los contenedores levantados (`docker compose up -d`), ejecutamos desde la raíz del proyecto **en este orden**:

```bash
python etl/cargar_mongodb.py       # carga los 4 JSON de data/raw y crea los índices
python etl/aplanar_cursos.py       # aplana los cursos -> cursos_planos
python etl/modulos_con_curso.py    # mete el curso aplanado en cada módulo -> modulos
```

Se puede repetir la carga sin duplicar datos, porque cada colección se borra antes de insertarla.

Para comprobar los datos:
- Mongo Express en http://localhost:8081
- mongosh con `docker exec -it bigdata-mongo mongosh -u admin -p admin --authenticationDatabase admin itaca`

## Bitácora de prácticas

> Cumplimentar al finalizar la práctica

### Bloque 0 - Entorno

- Objetivo: Crear la estructura básica del proyecto
- Pasos realizados: 
  - Creación del repositorio
  - Creación de las carpetas
  - Creación del README.md
  - Creación del docker-compose.yml
  - Creación del entorno con pyenv y venv
- Problemas encontrados y solución: Ningún problema encontrado
- Resultado: Este mismo [repositorio](https://github.com/QiweiLiuYang/bigdata-p1-itaca). ![Foto repositorio](<resources/img/Captura repositorio.png>)

### Bloque 1 - Ingesta batch

- Objetivo: Ingestar los distintos archivos xml para transformarlos a JSON
- Pasos realizados:
    1. Descargarse los datos
    2. Crear el script ingesta_itaca_xml.py
    3. Lectura de atributos con el paquete **xml.etree.ElementTree**
    4. Uso de comodines especiales en la búsqueda de ficheros con el paquete **glob**
    5. Anonimización de NIA con el paquete **hashlib**
    6. Registrar logs con el paquete **logging**
    7. Probar si funciona
- Problemas encontrados y solución: 
    1. **findtext** devolvía **None** porque los datos están en los atributos, usé **get()** para acceder a los atributos
    2. **e.msg** no existe en **OSError** y se solucionó conviertiendolo a texto con **str(e)**
- Resultado: ![Código python](<resources/img/Resultados bloque 1.png>)

### Bloque 2 - Bases de datos NoSQL

- Objetivo: Cargar en **MongoDB** los datos ingestados en el Bloque 1
- Pasos realizados:
    1. Añadir **mongo** y **mongo-express** al docker-compose.yml con usuario admin
    2. Crear **cargar_mongodb.py** que carga los 4 JSON, pasa la nota a número y crea los índices
    3. Crear **aplanar_cursos.py** que aplana la jerarquía de cursos con **$lookup** y lo guarda en cursos_planos
    4. Crear **modulos_con_curso.py** que mete el curso aplanado en cada módulo y lo guarda en modulos
    5. Crear **numero_registros.py** para comparar los registros de los JSON con MongoDB
    6. Verificar la carga con mongosh
- Problemas encontrados y solución: en [Incidencias resueltas](#incidencias-resueltas)
- Resultado: en [Verificación de la carga](#verificación-de-la-carga)

#### Índices

- **calificaciones** por curso, anyo y evaluacion, que es el filtro que más se usa
- **calificaciones** por nia, para buscar las notas de un alumno
- **alumnos** por nia y anyo, no único porque hay alumnos repetidos el mismo año (bajas y nuevas matrículas)
- **contenidos** y **modulos** por modulo, anyo y curso, único porque el mismo módulo sale en varios cursos

Con índice la consulta mira 666 documentos y sin índice los 106814.

![Uso de índices](docs/imagenes_bloque2/uso_de_indices_mongosh.png)

#### Verificación de la carga

1. El número de documentos coincide con los JSON

![Documentos por colección](docs/imagenes_bloque2/documentos_coleccion_coincide_con_ingestados.png)

2. Consulta de las notas de un curso. Las notas van de 0 a 10 y los módulos son de ese curso

![Consultas](docs/imagenes_bloque2/consultas_mongosh.png)

3. Nota media por grupo en la 2ª evaluación, se ejecuta sin errores

![Nota media por grupo](docs/imagenes_bloque2/nota_media_mongosh.png)

4. Módulos con el curso embebido en Mongo Express

![Módulos en Mongo Express](docs/imagenes_bloque2/modulos_mongo_express.png)

#### Decisiones sobre los datos

- La nota pasa a número porque si no la media salía null. Las notas en blanco se quedan en null
- En **modulos_con_curso.py** solo uno por curso_codigo porque la condición de grado con ensenanza de la teoría nunca se cumple
- En la nota media uso **$limit 1** en el $lookup para no contar dos veces a los alumnos repetidos
- En la nota media quito los alumnos sin grupo
- Las notas sin alumno se quedan fuera por el $unwind
- Las colecciones se borran antes de cargarlas para no duplicar datos

### Bloque 3 - Data Lake

- Objetivo: [ ]
- Pasos realizados: [ ]
- Problemas encontrados y solución: [ ]
- Resultado: [ ]

### Bloque 4 - Procesamiento con Spark

- Objetivo: [ ]
- Pasos realizados: [ ]
- Problemas encontrados y solución: [ ]
- Resultado: [ ]

<!--
### Bloque 5 - Streaming con Kafka

- Objetivo: [ ]
- Pasos realizados: [ ]
- Problemas encontrados y solución: [ ]
- Resultado: [ ]
-->

<!--
### Bloque 6 - FIWARE e IoT

- Objetivo: [ ]
- Pasos realizados: [ ]
- Problemas encontrados y solución: [ ]
- Resultado: [ ]
-->

### Bloque 7 - Orquestación, calidad y gobierno

- Objetivo: [ ]
- Pasos realizados: [ ]
- Problemas encontrados y solución: [ ]
- Resultado: [ ]

| Nombre | Ubicación | Descripción | Esquema | Frecuencia | Responsable | Sensibilidad |
| --- | --- | --- | --- | --- | --- | --- |
| [tabla] | [ruta / colección] | [] | [] | [] | [] | [baja / media / alta] |

### Bloque 8 - Visualización

- Objetivo: [ ]
- Pasos realizados: [ ]
- Problemas encontrados y solución: [ ]
- Resultado: [ ]

### Bloque 9 - Inteligencia Artificial

- Objetivo: [ ]
- Pasos realizados: [ ]
- Problemas encontrados y solución: [ ]
- Resultado: [tabla de métricas]

<!--
### Bloque 10 - Nube

- Objetivo: [ ]
- Pasos realizados: [ ]
- Problemas encontrados y solución: [ ]
- Resultado: [ ]
-->

### Decisiones técnicas

Las 2–3 decisiones de diseño más importantes, con la alternativa descartada. Te servirán para la defensa (Bloque 11, apartado 3).

| Decisión | Alternativa descartada | Motivo |
| --- | --- | --- |
| Obtener y añadir anyo desde el nodo raíz **centro** y su atributo **curso** en el XML | No incluirlo | Si no se incluye, los 5 años se mezclarían dentro del mismo fichero |
| Índice `alumnos(nia, anyo)` no único | Índice único, como propone la práctica | Hay alumnos repetidos el mismo año por bajas y nuevas matrículas, así que no se puede crear |

### Incidencias resueltas

| Problema | Causa | Solución |
| --- | --- | --- |
| Los módulos no recibían los datos del curso | La condición `grado == ensenanza` nunca se cumple | Unir solo por `curso_codigo` |
| `DuplicateKeyError` al crear el índice único de `alumnos` | Alumnos repetidos el mismo año | Índice no único |
| La nota media salía `null` | `nota` se guardaba como texto | Pasar a `float` y dejar en `null` las notas en blanco, porque `float(" ")` falla |

## Resultado final

> Capturas del dashboard y del modelo, y enlace al vídeo o a la demo si la hay.