# HealthNet - End-to-End Data Pipeline

## 1. Sector y plataforma seleccionada

### Sector elegido

Se seleccionó el sector salud porque permite trabajar con diferentes tipos de información relacionada con pacientes, encuentros, citas, médicos, sedes, camas y dispensación de medicamentos.

El sector seleccionado para esta prueba es **Salud y Servicios Médicos**.

El escenario corresponde a una red privada de salud llamada **HealthNet**, que cuenta con 82 sedes distribuidas entre hospitales, clínicas, centros médicos y centros de diagnóstico.

La distribución de las sedes es:

- 3 hospitales de alta complejidad.
- 16 clínicas de mediana complejidad.
- 42 centros médicos ambulatorios.
- 21 centros de diagnóstico especializado.

La operación de HealthNet incluye atención de pacientes, médicos, citas, encuentros médicos, dispensación de medicamentos y gestión de camas.

Para la generación de los datos se tomó como referencia el contexto y las reglas entregadas en la prueba técnica.

### Plataforma cloud seleccionada

La plataforma seleccionada es **Microsoft Azure**.

Se seleccionó Microsoft Azure porque la solución utiliza Azure Data Lake Storage Gen2 como almacenamiento, Azure SQL como fuente de datos y Azure Data Factory para implementar los procesos de integración y transformación de datos.

Para este proyecto se utilizarán principalmente:

- Azure SQL Database como base de datos oriigen.
- Azure Data Lake Storage Gen2 para almacenar las capas Bronze, Silver y Gold.
- Azure Data Factory para realizar la ingesta y orquestación del pipeline.


También se utilizarán herramientas como Python.

---

# 2. Descripción general del proyecto

El objetivo del proyecto es construir un pipeline de datos de principio a fin para una empresa del sector salud.

La solución comienza con datos sintéticos generados en Python. Estos datos representan diferentes procesos de una red hospitalaria.

Después de generar los datos, se cargan en una base de datos Azure SQL, que funciona como fuente origen del pipeline.

Desde Azure SQL los datos serán llevados a Azure Data Lake Storage Gen2 y pasarán por las tres capas de la arquitectura Medallion:

```text
Azure SQL
    |
    v
  Bronze
    |
    v
  Silver
    |
    v
   Gold
```

Cada capa tendrá una responsabilidad diferente.

### Bronze

La capa Bronze conserva los datos prácticamente como vienen de la fuent e (datos originas, crudos).

El objetivo de esta capa es evitar modificar los datos originales y mantener
una copia que pueda utilizarse posteriormente para reprocesar la información.

Las principales fuentes utilizadas son:

- PAC_REGISTRO
- HCE_ENCUENTROS
- RED_SEDES
- MED_PLANTA
- GCM_CAMAS
- AGE_CITAS
- FAR_DISPENSACION

Los archivos se almacenan en formato Parquet dentro de Azure Data Lake Storage Gen2.

La estructura utilizada sigue el siguiente patrón:
```text
bronze/
├── PAC_REGISTRO/
├── HCE_ENCUENTROS/
├── RED_SEDES/
├── MED_PLANTA/
├── GCM_CAMAS/
├── AGE_CITAS/
└── FAR_DISPENSACION/
```

### Silver

La capa Silver contiene los datos después de aplicar procesos de limpieza,
estandarización y validación.

Entre las transformaciones realizadas se encuentran:

- Estandarización de campos de texto.
- Eliminación de espacios innecesarios.
- Conversión de valores a formatos apropiados.
- Validación de identificadores obligatorios.
- Detección de registros duplicados.
- Validación de fechas.
- Separación de registros con anomalías.

### PAC_REGISTRO

Se estandarizó el campo tip_aseguradora y se validó la existencia de
pac_id.

### HCE_ENCUENTROS

Se implementaron controles para detectar:

- Duplicados de id_encuentros.
- Registros con fec_registro anterior a 2025-01-01.
- Registros donde fec_inicio_atencion es anterior a fec_registro.

Los registros que no cumplen las reglas de calidad se envían a una zona
de errores para poder revisarlos posteriormente.

### AGE_CITAS

Se implementaron validaciones para el cálculo del tiempo de espera.

Los registros con hora de llegada nula o tiempos de espera negativos
son tratados como registros de calidad y enviados al flujo de errores.

### Gold

La capa Gold tendrá los datos preparados para análisis y consumo.

En esta capa se construye un modelo dimensional compuesto por dimensiones
y tablas de hechos.

### Dimensiones

Se construyeron las siguientes dimensiones:

- dim_pacientes
- dim_medicos
- dim_sedes

### dim_pacientes

Se calcula el grupo de edad utilizando los siguientes rangos:

- 0-12
- 13-17
- 18-40
- 41-65
- +65

También se estandariza tip_aseguradora utilizando un catálogo controlado (EPS, ASEGURADORA, PARTICULAR).

### dim_medicos

Se combinó información de MED_PLANTA y RED_SEDES para enriquecer
la información de los médicos con los datos de la sede.

También se calcula la experiencia en años utilizando fec_ingreso.

### dim_sedes

Se calcula:

- capacidad_total_camas
- porcentaje_uci

La capacidad total se obtiene a partir de los diferentes tipos de camas
disponibles en la información de sedes.

### Tablas de hechos

Las tablas de hechos contempladas son:

- fact_consultas
- fact_ocupacion_camas
- fact_tiempos_espera
- fact_costos_atencion

---

# 3. Fuentes de datos

Para este escenario se generaron siete fuentes de datos.

Las tablas utilizadas son:

| Tabla | Descripción |
|---|---|
| RED_SEDES | Información de las sedes de HealthNet |
| PAC_REGISTRO | Información de los pacientes |
| MED_PLANTA | Información del personal médico |
| HCE_ENCUENTROS | Encuentros y atenciones médicas |
| GCM_CAMAS | Registro de camas y ocupación |
| FAR_DISPENSACION | Dispensación de medicamentos |
| AGE_CITAS | Información de las citas |

Los datos se generaron en Python y se almacenaron en formato CSV y Parquet.

No se utiliza `POST_DEVOLUCIONES`, ya que aunque aparece mencionada en una parte de la prueba, no se proporcionan los campos para construir esta fuente en el escenario de salud.

---

# 4. Generación de datos

La generación de datos se realizó utilizando Python.

Los scripts están ubicados en:

```text
/data-generation
```

La estructura actual es:

```text
data-generation/
│
├── generators/
│   ├── appointments.py
│   ├── beds.py
│   ├── doctors.py
│   ├── encounters.py
│   ├── facilities.py
│   ├── patients.py
│   └── pharmacy.py
│
├── output/
├── quality/
├── config.yaml
├── main.py
└── load_to_sql.py
```

El archivo `config.yaml` permite centralizar parámetros utilizados durante la generación.

Entre estos parámetros se encuentra el rango de fechas y la semilla utilizada para generar los datos.

Actualmente se trabaja con el siguiente rango:

```yaml
date_range:
  start: "2025-01-01"
  end: "2026-01-01"
```

Esto permite generar información correspondiente a doce meses.

---

# 5. Características de los datos generados

Los datos no fueron generados completamente de forma aleatoria.

Se intentó mantener una relación lógica entre las características de los datos.

Por ejemplo, las sedes tienen diferentes niveles de complejidad y esto se tiene en cuenta al generar información relacionada con las mismas.

También se manejaron los cuatro tipos principales de sede:

- Hospital.
- Clínica.
- Centro médico.
- Centro diagnóstico.

La cantidad de sedes corresponde al escenario entregado:

```text
Hospitales:          3
Clínicas:           16
Centros médicos:    42
Centros diagnóstico:21
Total:              82
```

---

# 6. Calidad de los datos

Como parte de la generación se incluyeron condiciones que permiten probar posteriormente la calidad de los datos.

## Valores nulos

Se incluyeron aproximadamente un 5% de valores nulos en campos que no son críticos.

El objetivo es simular situaciones que pueden aparecer en datos reales y posteriormente tratar estos valores en la capa Silver.

## Anomalías

También se incluyeron anomalías intencionales.

Entre ellas:

- registros duplicados;
- fechas fuera del rango esperado;
- fechas inconsistentes entre diferentes campos.

Estas anomalías serán utilizadas posteriormente para demostrar que el pipeline puede detectarlas y manejarlas.

## Linaje de datos

Para algunos de los campos calculados en la capa Gold se documentó de dónde vienen los datos, qué transformación se realiza y para qué se utiliza el resultado. Esto permite entender el recorrido de la información desde Silver hasta Gold.

### grupo_edad

El campo `grupo_edad` de la tabla `dim_pacientes` se obtiene a partir del campo `fec_nac` de `silver.PAC_REGISTRO`. Primero se calcula la edad del paciente y luego se clasifica en los rangos definidos para la prueba: 0-12, 13-17, 18-40, 41-65 y +65.

El propósito de este campo es facilitar la segmentación de los pacientes por grupo de edad y permitir análisis demográficos en la capa Gold.

### anos_experiencia

El campo `anos_experiencia` de la tabla `dim_medicos` se obtiene a partir del campo `fec_ingreso` de `silver.MED_PLANTA`. Se calcula la diferencia entre la fecha de referencia y la fecha de ingreso del médico para obtener los años de experiencia.

El propósito de este campo es facilitar el análisis de la experiencia de los médicos y permitir utilizar esta información en consultas y análisis de la operación de la red de salud.

### capacidad_total_camas

El campo `capacidad_total_camas` de la tabla `dim_sedes` se obtiene a partir de los diferentes tipos de capacidad de camas disponibles en `silver.RED_SEDES`. Para obtener este valor se realiza la suma de los cuatro tipos de camas registrados para cada sede.

El propósito de este campo es tener una medida consolidada de la capacidad de cada sede y facilitar el análisis de la disponibilidad y capacidad hospitalaria.


### tasa_ocupacion

El campo `tasa_ocupacion` de `fact_ocupacion_camas` se calcula utilizando los campos `num_camas_ocupadas` y `num_camas_disp` provenientes de `silver.GCM_CAMAS`. La fórmula utilizada es la cantidad de camas ocupadas dividida entre la suma de camas ocupadas y camas disponibles.

El propósito de este campo es medir el nivel de ocupación de las camas y permitir posteriormente clasificar el estado de ocupación de cada sede y tipo de unidad.

### tiempo_espera_min

El campo `tiempo_espera_min` de `fact_tiempos_espera` se obtiene a partir de `hra_llegada_paciente` y `hra_inicio_atencion` de `silver.AGE_CITAS`. Se calcula la diferencia entre la hora de inicio de atención y la hora de llegada del paciente, expresada en minutos.

El propósito de este campo es medir el tiempo que espera un paciente antes de ser atendido. Solo se consideran las citas atendidas y los registros con tiempos negativos se envían a la tabla de errores.

---

# 7. Formatos utilizados

Los datos sintéticos se generan en dos formatos:

```text
CSV
Parquet
```

El formato CSV facilita la revisión de los datos y el formato Parquet será utilizado posteriormente para procesamiento y almacenamiento en el Data Lake.

---

# 8. Base de datos origen

Los datos sintéticos serán cargados en:

```text
Azure SQL Database
```

La base de datos utilizada para el proyecto es:

```text
healthnetdb
```

La base de datos funciona como la fuente origen del pipeline.

La estructura de las tablas se creó teniendo en cuenta las siete fuentes generadas.

Por el momento se utilizan claves primarias para identificar los registros.

---

# 9. Arquitectura de la solución

La arquitectura final del proyecto será:

```text
                 PYTHON
                   |
                   v
            Datos sintéticos
                   |
                   v
              Azure SQL
             Fuente origen
                   |
                   v
          Azure Data Factory
                   |
                   v
              ADLS Gen2
                   |
        +----------+----------+
        |          |          |
        v          v          v
     BRONZE     SILVER      GOLD
        |          |          |
        |          |          |
        |          |          +--> Modelo analítico
        |          |
        |          +-------------> Datos limpios
        |
        +------------------------> Datos originales
```

---

# 10. Estructura del repositorio

La estructura final esperada del proyecto es:

```text
healthnet_data_pipeline/
│
├── infra/
│
├── data-generation/
│
├── pipelines/
│
├── orchestration/
│
├── docs/
│
├── README.md
│
└── CHANGELOG.md
```

### `/data-generation`

Contiene los scripts utilizados para generar los datos sintéticos y el archivo de configuración.

### `/infra`

Contendrá el código de Infraestructura como Código utilizado para crear los recursos de Azure.

### `/pipelines`

Contendrá el código relacionado con las transformaciones de las capas Bronze, Silver y Gold.

### `/orchestration`

Contendrá la definición de los procesos de orquestación.

### `/docs`

Contendrá la documentación del proyecto, incluyendo:

- diagrama de arquitectura;
- diagrama entidad-relación;
- catálogo de datos;
- evidencias necesarias.

---

# 11. Infraestructura de Azure

Para la solución se utilizarán recursos de Azure que permitan implementar el pipeline completo.

Entre ellos:

- Resource Group.
- Storage Account con ADLS Gen2.
- Contenedor Bronze.
- Contenedor Silver.
- Contenedor Gold.
- Azure Data Factory.

### Data Flows implementados

### Bronze

- DF_SQL_TO_BRONZE_PAC_REGISTRO
- DF_SQL_TO_BRONZE_HCE_ENCUENTROS
- DF_SQL_TO_BRONZE_RED_SEDES
- DF_SQL_TO_BRONZE_MED_PLANTA
- DF_SQL_TO_BRONZE_GCM_CAMAS
- DF_SQL_TO_BRONZE_AGE_CITAS
- DF_SQL_TO_BRONZE_FAR_DISPENSACION

### Silver

- DF_BRONZE_TO_SILVER_PAC_REGISTRO
- DF_BRONZE_TO_SILVER_HCE_ENCUENTROS
- DF_BRONZE_TO_SILVER_RED_SEDES
- DF_BRONZE_TO_SILVER_MED_PLANTA
- DF_BRONZE_TO_SILVER_GCM_CAMAS
- DF_BRONZE_TO_SILVER_AGE_CITAS
- DF_BRONZE_TO_SILVER_FAR_DISPENSACION

### Gold

- DF_SILVER_TO_GOLD_DIM_PACIENTES
- DF_SILVER_TO_GOLD_DIM_MEDICOS
- DF_SILVER_TO_GOLD_DIM_SEDES
- DF_SILVER_TO_GOLD_FACT_CONSULTAS
- DF_SILVER_TO_GOLD_FACT_OCUPACION_CAMAS
- DF_SILVER_TO_GOLD_FACT_TIEMPOS_ESPERA
- DF_SILVER_TO_GOLD_FACT_COSTOS_ATENCION

---

# 12. Despliegue

El despliegue de la solución se realizó por etapas. Primero se generaron los datos sintéticos desde ```text/data-generation``` y se cargaron en Azure SQL. Después, mediante Azure Data Factory, se configuraron los pipelines para llevar la información desde SQL hacia la capa Bronze en Azure Data Lake Storage Gen2. Luego se ejecutaron los Data Flows para limpiar y validar los datos y pasarlos a Silver, y finalmente se construyeron las dimensiones y tablas de hechos de la capa Gold para su análisis.


El orden general será:

```text
1. Generar datos
2. Crear Azure SQL
3. Cargar datos en Azure SQL
4. Crear infraestructura Azure
5. Configurar Bronze
6. Configurar Silver
7. Configurar Gold
```

---

# 13. Cómo ejecutar la generación de datos

Desde la carpeta `data-generation`:

```bash
python main.py
```

Los archivos generados se guardan en:

```text
data-generation/output/
```

---

# 14. Cómo cargar los datos en Azure SQL

La carga de datos se realizará mediante el script:

```text
data-generation/load_to_sql.py
```

Este script se conectará a Azure SQL utilizando autenticación de Azure y cargará los archivos generados.

Las credenciales no deben escribirse directamente dentro del código.

---

# 15. Evidencias

Durante el desarrollo se irán guardando evidencias de los principales pasos.

Entre ellas:

- generación de datos;
- cantidad de registros por tabla;
- carga en Azure SQL;
- recursos creados en Azure;
- ejecución del pipeline;
- funcionamiento de Bronze;
- validaciones de Silver;
- resultados de Gold;

Las evidencias finales se organizarán dentro de `/docs`.

---

# 16. Estado actual del proyecto

Actualmente ya se completó la generación de las siete fuentes sintéticas.

También se creó la cuenta de almacenamiento con ADLS Gen2 y la base de datos Azure SQL.

Los siete archivos CSV ya están disponibles en:

```text
data-generation/output/
```
Se completó la carga de estos archivos en Azure SQL y  partir de estas fuentes se implementó el flujo de datos en Azure Data Factory utilizando la arquitectura por capas Bronze, Silver y Gold.

### Bronze
Se implementaron los Data Flows para llevar la información desde las fuentes SQL hacia la zona Bronze:
- DF_SQL_TO_BRONZE_PAC_REGISTRO 
- DF_SQL_TO_BRONZE_HCE_ENCUENTROS 
- DF_SQL_TO_BRONZE_RED_SEDES 
- DF_SQL_TO_BRONZE_MED_PLANTA 
- DF_SQL_TO_BRONZE_GCM_CAMAS 
- DF_SQL_TO_BRONZE_AGE_CITAS 
- DF_SQL_TO_BRONZE_FAR_DISPENSACION 
Los archivos se están almacenando en ADLS Gen2 en la estructura correspondiente a la zona Bronze.

### Silver
También se implementaron los Data Flows para transformar y validar la información de Bronze antes de llevarla a Gold:
- DF_BRONZE_TO_SILVER_PAC_REGISTRO 
- DF_BRONZE_TO_SILVER_HCE_ENCUENTROS 
- DF_BRONZE_TO_SILVER_RED_SEDES 
- DF_BRONZE_TO_SILVER_MED_PLANTA 
- DF_BRONZE_TO_SILVER_GCM_CAMAS 
- DF_BRONZE_TO_SILVER_AGE_CITAS 
- DF_BRONZE_TO_SILVER_FAR_DISPENSACION 
En esta capa se realizaron transformaciones de limpieza y validación. Por ejemplo, en PAC_REGISTRO se estandarizó el campo de aseguradora y se validaron registros con pac_id nulo.
En HCE_ENCUENTROS se implementaron validaciones para detectar registros duplicados y problemas relacionados con las fechas. Los registros que presentan anomalías se separan de los registros válidos para no llevar datos inconsistentes directamente a Silver.

### Gold
En la capa Gold se empezó a construir el modelo dimensional y las tablas de hechos de acuerdo con las reglas de negocio del ejercicio.

Dimensiones completadas
- DF_SILVER_TO_GOLD_DIM_PACIENTES
- DF_SILVER_TO_GOLD_DIM_MEDICOS
- DF_SILVER_TO_GOLD_DIM_SEDES

En dim_pacientes se implementó la lógica para calcular el grupo de edad y estandarizar la información de aseguradora.

En dim_medicos se realizó el enriquecimiento con la información de RED_SEDES y se calculó la experiencia de los médicos a partir de la fecha de ingreso.

En dim_sedes se calculó la capacidad total de camas a partir de los diferentes tipos de camas disponibles y el porcentaje de UCI sobre la capacidad total.

Tablas de hechos completadas
- DF_SILVER_TO_GOLD_FACT_CONSULTAS
- DF_SILVER_TO_GOLD_FACT_OCUPACION_CAMAS
- DF_SILVER_TO_GOLD_FACT_TIEMPOS_ESPERA
- DF_SILVER_TO_GOLD_FACT_COSTOS_ATENCION

fact_consultas se construyó a partir de HCE_ENCUENTROS, calculando el tiempo de estancia y estandarizando el diagnóstico CIE-10 a tres caracteres. También se realizó el cruce con dim_medicos para poder aplicar las reglas relacionadas con la especialidad médica.

fact_ocupacion_camas se calcula la tasa de ocupación a partir de las camas ocupadas y las camas disponibles. También se agregó la clasificación del estado de ocupación teniendo en cuenta el tipo de unidad y los umbrales definidos para cada caso.

Los estados se clasifican así:

- GENERAL: Critico cuando supera el 88% de ocupación.
- CIRUGIA: Critico cuando supera el 88%.
- UCI: Critico cuando supera el 85%.
- URGENCIAS: Critico cuando supera el 90%.
- Precaucion: cuando la ocupación es igual o superior al 80% y no llega al nivel crítico.
- Normal: cuando la ocupación es menor al 80%.

Esta lógica se implementó en el Data Flow mediante condiciones que primero revisan el tipo de unidad y luego comparan la tasa de ocupación con el umbral correspondiente.

fact_tiempos_espera se calcula el tiempo de espera entre la llegada del paciente y el inicio de la atención. Se aplican las reglas de negocio para considerar únicamente las citas atendidas que cumplen las validaciones. Los registros con tiempos de espera negativos se consideran inconsistencias y se envían a una tabla de errores, mientras que los registros válidos continúan hacia fact_tiempos_espera`.

fact_costos_atencion está actualmente construida a partir de FAR_DISPENSACION y HCE_ENCUENTROS. Se realiza el cruce por id_encuentro, se calcula el costo de los medicamentos y se prepara la información para obtener el costo total agrupado por diagnóstico y tipo de consulta.

### Pipelines
Los Data Flows de Bronze y Silver ya fueron integrados en sus respectivos pipelines para que el proceso pueda ejecutarse de forma completa y no solamente mediante Data Preview.

La idea del flujo completo es:

```text
Azure SQL
    |
    v
  Bronze
    |
    v
  Silver
    |
    v
   Gold
```

---

# 21. Notas importantes

- No se deben subir contraseñas, tokens ni claves al repositorio.
- Los datos sintéticos se generan utilizando una semilla fija.
- El pipeline debe poder ejecutarse nuevamente sin generar duplicados.
- Las anomalías generadas intencionalmente deben ser detectadas o manejadas por el pipeline.
- La información sensible debe protegerse durante el procesamiento.

---

# 22. Autor

Proyecto desarrollado como parte de la prueba técnica de Ingeniería de Datos.

**Autor:** Esteffany Giraldo Duran

**Fecha:** 2026