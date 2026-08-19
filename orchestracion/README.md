## Orquestación

La orquestación se implementó mediante Azure Data Factory. Se creó un pipeline por fuente de datos para ejecutar de forma secuencial el procesamiento desde la fuente SQL hasta la capa Silver.

Por ejemplo, para `PAC_REGISTRO`, el pipeline ejecuta primero el proceso de carga hacia Bronze y, una vez finalizado, ejecuta el Data Flow encargado de transformar y validar la información hacia Silver.

La estructura general es:

```text
Azure SQL
    ↓
Bronze
    ↓
Silver