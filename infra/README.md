# Infraestructura

La solución utiliza los siguientes componentes principales de Azure:

- Azure Data Factory
- Azure Data Lake Storage Gen2
- Azure SQL / fuente SQL utilizada para la extracción

La infraestructura necesaria incluye:

- Cuenta de almacenamiento.
- Contenedores de datos.
- Azure Data Factory.
- Linked Services.
- Datasets.
- Data Flows.
- Pipelines.

La configuración completa de infraestructura debe ser desplegada antes
de ejecutar los pipelines.

## Azure Data Lake Storage Gen2

Se utilizó Azure Data Lake Storage Gen2 como almacenamiento de las diferentes capas del pipeline.

Estructura utilizada:

- bronze/
- silver/
- gold/
- errors/

## Azure SQL

Azure SQL se utilizó como fuente de datos para los procesos de ingesta hacia la capa Bronze.

Las fuentes corresponden a las siete tablas sintéticas utilizadas en la prueba.

## Despliegue

1. Crear el Resource Group.
2. Crear la cuenta de Azure Data Lake Storage Gen2.
3. Crear los contenedores requeridos.
4. Crear Azure Data Factory.
5. Configurar los Linked Services.
6. Crear los datasets.
7. Publicar los Data Flows.
8. Publicar los pipelines.
