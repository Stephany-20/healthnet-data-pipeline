# CHANGELOG

En este archivo voy registrando los cambios importantes realizados durante el desarrollo del proyecto HealthNet.

---

## [2026-08-13]

**Autor:** Esteffany Giraldo

### Generación de datos

- Se creó la estructura inicial del proyecto.
- Se creó la carpeta `data-generation`.
- Se crearon los scripts para generar datos sintéticos.
- Se generaron las fuentes `RED_SEDES`, `PAC_REGISTRO`, `MED_PLANTA`, `HCE_ENCUENTROS`, `GCM_CAMAS`, `FAR_DISPENSACION` y `AGE_CITAS`.
- Se generaron los archivos de salida en formato CSV y Parquet.
- Se creó el archivo `config.yaml` para manejar la configuración de generación de datos.
- Se agregó el archivo `main.py` para ejecutar el proceso completo de generación.

### Calidad de datos

- Se realizaron validaciones básicas sobre los datos generados.
- Se revisaron registros duplicados.
- Se revisaron fechas fuera del rango esperado.
- Se identificaron fechas inconsistentes en la fuente `HCE_ENCUENTROS`.
- Se dejó identificado que el campo `id_eps` puede venir vacío dependiendo del tipo de aseguramiento del paciente.

### Base de datos

- Se creó el servidor de Azure SQL `sql-healthnet-01`.
- Se creó la base de datos `healthnetdb`.
- Se crearon las tablas para almacenar las fuentes generadas.
- Se configuró la conexión desde Python hacia Azure SQL.

### Carga de datos

- Se creó el script `load_to_sql.py`.
- Se configuró la conexión utilizando `pyodbc`.
- Se utilizaron variables de entorno para manejar el usuario y la contraseña de Azure SQL.
- Se cargaron los datos desde archivos CSV y Parquet.
- Se implementó la carga por lotes para las tablas con mayor cantidad de registros.
- Se agregó una validación para evitar insertar nuevamente registros que ya existen en la base de datos.

### Azure Data Factory

- Se creó Azure Data Factory `adf-healthnet-01`.
- Se crearon los datasets necesarios para realizar la ingesta.
- Se crearon pipelines para mover los datos desde Azure SQL hacia la zona Bronze.
- Se realizó la carga de los archivos Parquet en la zona Bronze.
- Se creó el primer Data Flow para el procesamiento desde Bronze hacia Silver.
- Se configuraron transformaciones de limpieza, validación y mapeo de datos.


## [2026-08-16]

**Autor:** Esteffany Giraldo

### Capa Silver

- Se terminaron los Data Flows para procesar las fuentes desde Bronze hacia Silver.
- Se eliminaron registros duplicados cuando fue necesario.
- Se realizaron validaciones de campos obligatorios.
- Se estandarizaron formatos de datos.
- Se trataron valores nulos según las reglas de cada fuente.
- Se aplicaron las reglas de calidad definidas para los datos.
- Se trataron las anomalías identificadas en `HCE_ENCUENTROS`.
- Los resultados procesados se almacenaron en formato Parquet en la zona Silver.

## [2026-08-17]

**Autor:** Esteffany Giraldo

### Capa Gold

- Se creó la dimensión `dim_pacientes`.
- Se agregó el cálculo del grupo de edad.
- Se creó la dimensión `dim_medicos`.
- Se enriqueció la información de los médicos con los datos de las sedes.
- Se creó la dimensión `dim_sedes`.
- Se calculó la capacidad total de camas y el porcentaje de camas UCI.
- Se crearon las tablas de hechos requeridas para el análisis.
- Se aplicaron las reglas de negocio definidas para la capa Gold.

