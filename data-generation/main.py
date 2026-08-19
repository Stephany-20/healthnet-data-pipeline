from pathlib import Path

import pandas as pd
import yaml
import time

from generators.facilities import generar_sedes
from generators.patients import generar_pacientes
from generators.doctors import generar_medicos
from generators.encounters import generar_encuentros
from quality.anomalies import (agregar_nulos,agregar_duplicados,agregar_fechas_fuera_rango,agregar_fechas_inconsistentes)
from generators.beds import generar_camas
from generators.pharmacy import generar_dispensaciones
from generators.appointments import generar_citas

def cargar_configuracion():
    ruta = Path(__file__).parent / "config.yaml"

    with open(ruta, "r", encoding="utf-8") as archivo:
        configuracion = yaml.safe_load(archivo)
    return configuracion

def main():
    configuracion = cargar_configuracion()

    semilla = configuracion["project"]["seed"]

    cantidad_sedes = configuracion["volumes"]["RED_SEDES"]

    cantidad_pacientes = configuracion["volumes"]["PAC_REGISTRO"]

    cantidad_medicos = configuracion["volumes"]["MED_PLANTA"]

    cantidad_encuentros = configuracion["volumes"]["HCE_ENCUENTROS"]

    porcentaje_nulos = configuracion["data_quality"]["null_percentage"]

    cantidad_camas = configuracion["volumes"]["GCM_CAMAS"]

    cantidad_dispensacion = configuracion["volumes"]["FAR_DISPENSACION"]

    cantidad_citas = configuracion["volumes"]["AGE_CITAS"]

    carpeta_salida = Path(__file__).parent / "output"

    carpeta_salida.mkdir(exist_ok=True)

    print("Generando sedes...")

    df_sedes = generar_sedes(semilla, cantidad_sedes)

    print("Cantidad de sedes: ", len(df_sedes))

    archivo_csv = carpeta_salida / "RED_SEDES.csv"

    df_sedes.to_csv(archivo_csv, index=False)

    archivo_parquet = carpeta_salida / "RED_SEDES.parquet"

    df_sedes.to_parquet(archivo_parquet, index=False)

    print("Archivo CSV creado.")
    print("Archivo Parquet creado.")

    print("Generando pacientes...")
    df_pacientes = generar_pacientes(semilla, cantidad_pacientes, configuracion)
    print("Cantidad de pacientes: ", len(df_pacientes))
    df_pacientes.to_csv(
        carpeta_salida / "PAC_REGISTRO.csv", index=False
    )
    df_pacientes.to_parquet(
        carpeta_salida / "PAC_REGISTRO.parquet", index=False
    )
    print("Pacientes generados.")

    print("Generando médicos...")
    df_medicos = generar_medicos(semilla, cantidad_medicos, configuracion)
    print("Cantidad de médicos: ", len(df_medicos))
    df_medicos.to_csv(carpeta_salida / "MED_PLANTA.csv", index=False)
    df_medicos.to_parquet(carpeta_salida / "MED_PLANTA.parquet", index=False)
    print("Médicos generados.")
    
    print("Generando encuentros...")
    df_encuentros = generar_encuentros(semilla, cantidad_encuentros,configuracion, df_pacientes,df_medicos)
    print("Cantidad encuentros: ", len(df_encuentros))
    
    df_encuentros = agregar_nulos( df_encuentros, porcentaje_nulos)
    df_encuentros = agregar_duplicados(df_encuentros)
    df_encuentros = agregar_fechas_fuera_rango(df_encuentros)
    df_encuentros = agregar_fechas_inconsistentes(df_encuentros)
    print("Cantidad encuentros: ", len(df_encuentros))
    df_encuentros.to_csv(
            carpeta_salida / "HCE_ENCUENTROS.csv", index=False
        )
    df_encuentros.to_parquet(
            carpeta_salida / "HCE_ENCUENTROS.parquet", index=False
        )
    print("Encuentros generados.")


    
    print("Generando camas...")
    df_camas = generar_camas(semilla, cantidad_camas,configuracion,df_sedes)
    print("Cantidad camas: ", len(df_camas))
    df_camas.to_csv(carpeta_salida / "GCM_CAMAS.csv", index=False)
    df_camas.to_parquet(carpeta_salida / "GCM_CAMAS.parquet")
    print("Camas generadas.")

    print("")
    print("=" * 60)
    print("FAR_DISPENSACION")
    print("=" * 60)

    inicio_main = time.time()

    print(
        "Generando dispensaciones..."
    )

    resultado = generar_dispensaciones(
        seed=semilla,
        cantidad=cantidad_dispensacion,
        configuracion=configuracion,
        df_encuentros=df_encuentros,
        carpeta_salida=carpeta_salida,
        tamano_bloque=100000
    )

    tiempo_main = (
        time.time() -
        inicio_main
    )

    print("")
    print("=" * 60)

    if resultado:

        print(
            "PROCESO FINALIZADO CORRECTAMENTE"
        )

        print(
            f"Tiempo total MAIN: "
            f"{tiempo_main / 60:.2f} minutos"
        )

    else:

        print(
            "EL PROCESO TERMINÓ CON ERROR"
        )

    print("=" * 60)


    print("Generando citas...")
    df_citas = generar_citas(semilla,cantidad_citas,configuracion,df_pacientes, df_medicos)
    print("Cantidad citas: ", len(df_citas))
    df_citas.to_csv(
            carpeta_salida / "AGE_CITAS.csv", index=False
            )
    df_citas.to_parquet(
            carpeta_salida / "AGE_CITAS.parquet", index=False
        )
    print("Citas generadas.")
    


if __name__=="__main__":
    main()