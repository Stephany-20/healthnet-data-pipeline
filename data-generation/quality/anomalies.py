import pandas as pd
import random
from datetime import timedelta

def agregar_nulos(df, porcentaje):
    cantidad_registros = len(df)

    cantidad_nulos = int(
        cantidad_registros * porcentaje
    )
    campos = [
        "diag_sec1_cie10",
        "cod_procedimiento"
    ]
    for campo in campos:
        indices = random.sample(
            range(cantidad_registros),
            cantidad_nulos
        )
        df.loc[
            indices, 
            campo
        ] = None
    return df

def agregar_duplicados(df):
    cantidad = 100

    duplicados = df.sample(n=cantidad,random_state=10)
    df = pd.concat([df, duplicados], ignore_index=True)

    return df

def agregar_fechas_fuera_rango(df):
    indices = df.sample(n=100, random_state=20).index

    df.loc[indices, "fec_registro"] = pd.Timestamp("2024-01-15")

    return df

def agregar_fechas_inconsistentes(df):
    indices = df.sample(n=100,random_state=30).index
    for indice in indices:
        fecha = df.loc[indice , "fec_registro"]
        df.loc[indice, "fec_inicio_atencion"] = fecha - timedelta(minutes=30)
    return df
