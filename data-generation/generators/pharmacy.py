import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


# ============================================================
# GENERAR DISPENSACIONES POR BLOQUES
# ============================================================

def generar_dispensaciones(
    seed,
    cantidad,
    configuracion,
    df_encuentros,
    carpeta_salida,
    tamano_bloque=100000
):

    print("")
    print("=" * 60)
    print("INICIANDO GENERACIÓN DE DISPENSACIONES")
    print("=" * 60)

    inicio_total = time.time()

    # --------------------------------------------------------
    # Configuración
    # --------------------------------------------------------

    cantidad_total = cantidad

    print(f"Cantidad total a generar: {cantidad_total:,}")
    print(f"Tamaño de bloque: {tamano_bloque:,}")
    print(f"Cantidad de encuentros disponibles: {len(df_encuentros):,}")

    # --------------------------------------------------------
    # Crear carpeta de salida
    # --------------------------------------------------------

    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(
        parents=True,
        exist_ok=True
    )

    archivo_csv = (
        carpeta_salida /
        "FAR_DISPENSACION.csv"
    )

    archivo_parquet = (
        carpeta_salida /
        "FAR_DISPENSACION.parquet"
    )

    # --------------------------------------------------------
    # Eliminar archivos anteriores
    # --------------------------------------------------------

    if archivo_csv.exists():
        archivo_csv.unlink()
        print("Archivo CSV anterior eliminado.")

    if archivo_parquet.exists():
        archivo_parquet.unlink()
        print("Archivo Parquet anterior eliminado.")

    # --------------------------------------------------------
    # Preparar fechas de encuentros UNA SOLA VEZ
    # --------------------------------------------------------

    print("")
    print("Preparando fechas de encuentros...")

    df_encuentros = df_encuentros.copy()

    df_encuentros["fec_registro"] = pd.to_datetime(
        df_encuentros["fec_registro"]
    )

    print("Fechas preparadas.")

    # --------------------------------------------------------
    # Medicamentos
    # --------------------------------------------------------

    medicamentos = [
        {
            "codigo": "MED001",
            "nombre": "Acetaminofen 500 mg",
            "valor": 2500
        },
        {
            "codigo": "MED001",
            "nombre": "Acetaminofen 500 mg",
            "valor": 2500
        },
        {
            "codigo": "MED002",
            "nombre": "Ibuprofeno 400 mg",
            "valor": 3500
        },
        {
            "codigo": "MED003",
            "nombre": "Amoxicilina 500 mg",
            "valor": 8500
        },
        {
            "codigo": "MED004",
            "nombre": "Omeprazol 20 mg",
            "valor": 4200
        },
        {
            "codigo": "MED005",
            "nombre": "Losartan 50 mg",
            "valor": 52200
        },
        {
            "codigo": "MED006",
            "nombre": "Metformina 850 mg",
            "valor": 4800
        },
        {
            "codigo": "MED007",
            "nombre": "Atorvastatina 20 mg",
            "valor": 6500
        },
        {
            "codigo": "MED008",
            "nombre": "Azitromicina 500 mg",
            "valor": 11000
        },
        {
            "codigo": "MED009",
            "nombre": "Diclofenaco 50 mg",
            "valor": 3000
        },
        {
            "codigo": "MED010",
            "nombre": "Salbutamol 100 mg",
            "valor": 7200
        }
    ]

    tipos_prescripcion = [
        "Ambulatoria",
        "Hospitalaria",
        "Urgencias"
    ]

    # --------------------------------------------------------
    # Generador aleatorio
    # --------------------------------------------------------

    rng = np.random.default_rng(seed)

    # --------------------------------------------------------
    # Preparar Parquet
    # --------------------------------------------------------

    parquet_writer = None

    # --------------------------------------------------------
    # Variables de control
    # --------------------------------------------------------

    registros_generados = 0
    numero_bloque = 0

    try:

        # ====================================================
        # PROCESAMIENTO POR BLOQUES
        # ====================================================

        while registros_generados < cantidad_total:

            numero_bloque += 1

            inicio_bloque = time.time()

            # ------------------------------------------------
            # Determinar tamaño del bloque
            # ------------------------------------------------

            registros_restantes = (
                cantidad_total -
                registros_generados
            )

            cantidad_bloque = min(
                tamano_bloque,
                registros_restantes
            )

            print("")
            print("-" * 60)

            print(
                f"Bloque {numero_bloque}"
            )

            print(
                f"Registros del bloque: "
                f"{cantidad_bloque:,}"
            )

            print(
                f"Progreso antes: "
                f"{registros_generados:,} / "
                f"{cantidad_total:,}"
            )

            # ------------------------------------------------
            # Seleccionar encuentros
            # ------------------------------------------------
            #
            # IMPORTANTE:
            # No usamos df.sample() 2 millones de veces.
            #
            # Seleccionamos todos los encuentros del bloque
            # de una sola vez.
            # ------------------------------------------------

            indices = rng.integers(
                0,
                len(df_encuentros),
                size=cantidad_bloque
            )

            encuentros = (
                df_encuentros
                .iloc[indices]
                .reset_index(drop=True)
            )

            # ------------------------------------------------
            # Medicamentos
            # ------------------------------------------------

            indices_medicamentos = rng.integers(
                0,
                len(medicamentos),
                size=cantidad_bloque
            )

            codigos_medicamentos = [
                medicamentos[i]["codigo"]
                for i in indices_medicamentos
            ]

            nombres_medicamentos = [
                medicamentos[i]["nombre"]
                for i in indices_medicamentos
            ]

            valores_base = np.array([
                medicamentos[i]["valor"]
                for i in indices_medicamentos
            ])

            # ------------------------------------------------
            # Cantidad medicamento
            # ------------------------------------------------

            cantidades = rng.choice(
                [1, 2, 3, 4, 5],
                size=cantidad_bloque,
                p=[
                    0.35,
                    0.30,
                    0.20,
                    0.10,
                    0.05
                ]
            )

            # ------------------------------------------------
            # Variación precio
            # ------------------------------------------------

            variaciones = rng.uniform(
                0.90,
                1.10,
                size=cantidad_bloque
            )

            valores_unitarios = (
                valores_base *
                variaciones
            ).astype(int)

            # ------------------------------------------------
            # Fechas de dispensación
            # ------------------------------------------------

            dias_despues = rng.integers(
                0,
                4,
                size=cantidad_bloque
            )

            fechas_dispensacion = (
                encuentros["fec_registro"]
                +
                pd.to_timedelta(
                    dias_despues,
                    unit="D"
                )
            )

            # ------------------------------------------------
            # Tipo de prescripción
            # ------------------------------------------------

            tipos = rng.choice(
                tipos_prescripcion,
                size=cantidad_bloque
            )

            # ------------------------------------------------
            # ID de dispensación
            # ------------------------------------------------

            id_inicio = (
                registros_generados + 1
            )

            id_fin = (
                registros_generados +
                cantidad_bloque + 1
            )

            ids_dispensacion = np.arange(
                id_inicio,
                id_fin
            )

            # ------------------------------------------------
            # Crear DataFrame del bloque
            # ------------------------------------------------

            df_bloque = pd.DataFrame({

                "id_diapensacion":
                    ids_dispensacion,

                "id_encuentros":
                    encuentros[
                        "id_encuentros"
                    ].values,

                "pac_id":
                    encuentros[
                        "pac_id"
                    ].values,

                "id_sede":
                    encuentros[
                        "id_sede"
                    ].values,

                "fec_dispensacion":
                    fechas_dispensacion.values,

                "cod_medicamento":
                    codigos_medicamentos,

                "nom_medicamento":
                    nombres_medicamentos,

                "cantidad":
                    cantidades,

                "vr_unitario":
                    valores_unitarios,

                "tip_prescripcion":
                    tipos
            })

            # ------------------------------------------------
            # ESCRIBIR CSV
            # ------------------------------------------------

            if registros_generados == 0:

                # Primer bloque:
                # escribe encabezados

                df_bloque.to_csv(
                    archivo_csv,
                    index=False,
                    mode="w"
                )

            else:

                # Siguientes bloques:
                # agrega debajo de lo anterior

                df_bloque.to_csv(
                    archivo_csv,
                    index=False,
                    mode="a",
                    header=False
                )

            # ------------------------------------------------
            # ESCRIBIR PARQUET
            # ------------------------------------------------

            tabla_parquet = (
                pa.Table.from_pandas(
                    df_bloque,
                    preserve_index=False
                )
            )

            if parquet_writer is None:

                parquet_writer = pq.ParquetWriter(
                    archivo_parquet,
                    tabla_parquet.schema
                )

            parquet_writer.write_table(
                tabla_parquet
            )

            # ------------------------------------------------
            # Actualizar contador
            # ------------------------------------------------

            registros_generados += (
                cantidad_bloque
            )

            # ------------------------------------------------
            # Tiempo del bloque
            # ------------------------------------------------

            tiempo_bloque = (
                time.time() -
                inicio_bloque
            )

            # ------------------------------------------------
            # Porcentaje
            # ------------------------------------------------

            porcentaje = (
                registros_generados /
                cantidad_total
            ) * 100

            # ------------------------------------------------
            # Velocidad
            # ------------------------------------------------

            velocidad = (
                cantidad_bloque /
                tiempo_bloque
            )

            print(
                f"Bloque terminado en: "
                f"{tiempo_bloque:.2f} segundos"
            )

            print(
                f"Velocidad: "
                f"{velocidad:,.0f} registros/segundo"
            )

            print(
                f"Progreso: "
                f"{registros_generados:,} / "
                f"{cantidad_total:,} "
                f"({porcentaje:.2f}%)"
            )

            # ------------------------------------------------
            # Liberar DataFrame del bloque
            # ------------------------------------------------

            del df_bloque
            del encuentros

    finally:

        # ----------------------------------------------------
        # Cerrar Parquet
        # ----------------------------------------------------

        if parquet_writer is not None:
            parquet_writer.close()

    # ========================================================
    # TIEMPO TOTAL
    # ========================================================

    tiempo_total = (
        time.time() -
        inicio_total
    )

    print("")
    print("=" * 60)
    print("GENERACIÓN TERMINADA")
    print("=" * 60)

    print(
        f"Total registros: "
        f"{registros_generados:,}"
    )

    print(
        f"Tiempo total: "
        f"{tiempo_total:.2f} segundos"
    )

    print(
        f"Tiempo total: "
        f"{tiempo_total / 60:.2f} minutos"
    )

    if tiempo_total > 0:

        velocidad_total = (
            registros_generados /
            tiempo_total
        )

        print(
            f"Velocidad promedio: "
            f"{velocidad_total:,.0f} "
            f"registros/segundo"
        )

    print("")
    print("Archivos generados:")

    print(
        f"CSV:      {archivo_csv}"
    )

    print(
        f"Parquet:  {archivo_parquet}"
    )

    print("")

    return True