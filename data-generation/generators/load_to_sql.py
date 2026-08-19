import pyodbc
import os
import pandas as pd

servidor = "sql-healthnet-01.database.windows.net"
base_datos = "healthnetdb"

usuario = os.environ["SQL_USER"]
password = os.environ["SQL_PASSWORD"]


conexion = (
    "Driver={ODBC Driver 17 for SQL Server};"
    f"Server={servidor};"
    f"Database={base_datos};"
    f"UID={usuario};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)



def limpiar_valor(valor):

    if pd.isna(valor):
        return None

    return valor


def cargar_por_lotes(
    conexion_sql,
    df,
    nombre_tabla,
    columna_id,
    columnas,
    sql,
    tamaño_lote=1000
):

    print("\nCargando:", nombre_tabla)
    print("Registros encontrados:", len(df))

    registros_insertados = 0
    registros_existentes = 0

    for inicio in range(0, len(df), tamaño_lote):

        fin = inicio + tamaño_lote

        lote = df.iloc[inicio:fin]

        ids = lote[columna_id].tolist()
        

        placeholders = ",".join(
            "?" for _ in ids
        )

        consulta = f"""
        SELECT {columna_id}
        FROM {nombre_tabla}
        WHERE {columna_id} IN ({placeholders})
        """

        resultados = conexion_sql.execute(
            consulta,
            *ids
        ).fetchall()

        ids_existentes = {
            fila[0]
            for fila in resultados
        }

        filas_insertar = []

        for _, fila in lote.iterrows():

            id_actual = fila[columna_id]

            if id_actual not in ids_existentes:

                valores = []

                for columna in columnas:

                    valor = limpiar_valor(
                        fila[columna]
                    )

                    valores.append(valor)

                filas_insertar.append(
                    tuple(valores)
                )

            else:

                registros_existentes += 1

        
        if len(filas_insertar) > 0:

            cursor = conexion_sql.cursor()

            cursor.fast_executemany = True

            cursor.executemany(
                sql,
                filas_insertar
            )

            cursor.close()

            registros_insertados += len(
                filas_insertar
            )

        conexion_sql.commit()

        print(
            f"Procesados: {min(fin, len(df))} / {len(df)}"
        )

    print("Carga terminada:", nombre_tabla)
    print(
        "Registros insertados:",
        registros_insertados
    )
    print(
        "Registros que ya existían:",
        registros_existentes
    )

try:
    conexion_sql = pyodbc.connect(conexion)

    print("Conexión exitosa con Azure SQL")

    #RED_SEDES

    archivo = "output/RED_SEDES.csv"
    df_sedes = pd.read_csv(archivo)
    print("Registros encontrados:", len(df_sedes))

    registros_insertados = 0
    registros_existentes = 0

    for _, fila in df_sedes.iterrows():

        consulta = """
        SELECT COUNT(*)
        FROM RED_SEDES
        WHERE id_sede = ?
        """
        resultado = conexion_sql.execute(
            consulta,
            fila["id_sede"]
        ).fetchone()

        if resultado[0] == 0:

            sql = """
            INSERT INTO RED_SEDES(
                id_sede,
                nom_sede,
                tip_sede,
                id_ciudad,
                id_pais,
                cap_camas_gen,
                cap_camas_uci,
                cap_camas_cirugia,
                cap_camas_urg,
                nivel_complejidad)
                VALUES(?,?,?,?,?,?,?,?,?,?)
            """
            conexion_sql.execute(
                sql,
                fila["id_sede"],
                fila["nom_sede"],
                fila["tip_sede"],
                fila["id_ciudad"],
                fila["id_pais"],
                fila["cap_camas_gen"],
                fila["cap_camas_uci"],
                fila["cap_camas_cirugia"],
                fila["cap_camas_urg"],
                fila["nivel_complejidad"]
            )
            registros_insertados += 1
        else:

            registros_existentes += 1

    conexion_sql.commit()

    print("RED_SEDES cargada.")
    print("Registros insertados:", registros_insertados)
    print("Registros que ya existían:", registros_existentes)

#MED_PLANTA
    print("\nCargando MED_PLANTA...")

    df_medicos = pd.read_csv("output/MED_PLANTA.csv")
    print("Registros encontrados:", len(df_medicos))

    registros_insertados = 0
    registros_existentes = 0

    for _, fila in df_medicos.iterrows():

        consulta = """
        SELECT COUNT(*)
        FROM MED_PLANTA
        WHERE med_id = ?
        """
        resultado = conexion_sql.execute(
            consulta,
            fila["med_id"]
        ).fetchone()

        if resultado[0] == 0:

            sql = """
            INSERT INTO MED_PLANTA(
                med_id,
                esp_principal,
                esp_secundaria,
                id_sede,
                fec_ingreso,
                tip_contrato,
                jornada,
                estado_activo)
                VALUES(?,?,?,?,?,?,?,?)
            """
            conexion_sql.execute(
                sql,
                fila["med_id"],
                fila["esp_principal"],
                fila["esp_secundaria"],
                fila["id_sede"],
                fila["fec_ingreso"],
                fila["tip_contrato"],
                fila["jornada"],
                fila["estado_activo"]
            )
            registros_insertados += 1
        else:

            registros_existentes += 1

    conexion_sql.commit()

    print("MED_PLANTA cargada.")
    print("Registros insertados:", registros_insertados)
    print("Registros que ya existían:", registros_existentes) 

#PAC_REGISTRO
    print("\nCargando PAC_REGISTRO...")

    df_pacientes = pd.read_parquet(
        "output/PAC_REGISTRO.parquet"
    )

    sql_pacientes = """
    INSERT INTO PAC_REGISTRO (
        pac_id,
        tip_doc,
        num_doc_hash,
        fec_nac,
        genero,
        id_ciudad_res,
        tip_aseguradora,
        id_eps,
        estrato_socioec,
        fec_primer_atencion,
        activo
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cargar_por_lotes(
        conexion_sql,
        df_pacientes,
        "PAC_REGISTRO",
        "pac_id",
        [
            "pac_id",
            "tip_doc",
            "num_doc_hash",
            "fec_nac",
            "genero",
            "id_ciudad_res",
            "tip_aseguradora",
            "id_eps",
            "estrato_socioec",
            "fec_primer_atencion",
            "activo"
        ],
        sql_pacientes,
        1000
    )

#GCM_CAMAS
    print("\nLeyendo GCM_CAMAS.parquet...")

    df_camas = pd.read_parquet(
        "output/GCM_CAMAS.parquet"
    )

    sql_camas = """
    INSERT INTO GCM_CAMAS (
        id_registro_cama,
        id_sede,
        tip_unidad,
        fec_hora_registro,
        num_camas_ocupadas
    )
    VALUES (?, ?, ?, ?, ?)
    """

    cargar_por_lotes(
        conexion_sql,
        df_camas,
        "GCM_CAMAS",
        "id_registro_cama",
        [
            "id_registro_cama",
            "id_sede",
            "tip_unidad",
            "fec_hora_registro",
            "num_camas_ocupadas"
        ],
        sql_camas,
        1000
    )

#HCE_ENCUENTROS
    print("\nLeyendo HCE_ENCUENTROS.parquet...")

    df_encuentros = pd.read_parquet(
        "output/HCE_ENCUENTROS.parquet"
    )

    sql_encuentros = """
    INSERT INTO HCE_ENCUENTROS (
        id_encuentros,
        pac_id,
        med_id,
        id_sede,
        fec_registro,
        fec_inicio_atencion,
        fec_egreso,
        tip_consulta,
        esp_atendida,
        diag_principal_cie10,
        diag_sec1_cie10,
        cod_procedimiento,
        vr_facturado,
        estado_factura
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cargar_por_lotes(
        conexion_sql,
        df_encuentros,
        "HCE_ENCUENTROS",
        "id_encuentros",
        [
            "id_encuentros",
            "pac_id",
            "med_id",
            "id_sede",
            "fec_registro",
            "fec_inicio_atencion",
            "fec_egreso",
            "tip_consulta",
            "esp_atendida",
            "diag_principal_cie10",
            "diag_sec1_cie10",
            "cod_procedimiento",
            "vr_facturado",
            "estado_factura"
        ],
        sql_encuentros,
        1000
    )

#FAR_DISPENSACION
    print("\nLeyendo FAR_DISPENSACION.parquet...")

    df_dispensacion = pd.read_parquet(
        "output/FAR_DISPENSACION.parquet"
    )

    sql_dispensacion = """
    INSERT INTO FAR_DISPENSACION (
        id_diapensacion,
        id_encuentros,
        pac_id,
        id_sede,
        fec_dispensacion,
        cod_medicamento,
        nom_medicamento,
        cantidad,
        vr_unitario,
        tip_prescripcion
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cargar_por_lotes(
        conexion_sql,
        df_dispensacion,
        "FAR_DISPENSACION",
        "id_diapensacion",
        [
            "id_diapensacion",
            "id_encuentros",
            "pac_id",
            "id_sede",
            "fec_dispensacion",
            "cod_medicamento",
            "nom_medicamento",
            "cantidad",
            "vr_unitario",
            "tip_prescripcion"
        ],
        sql_dispensacion,
        1000
    )

  #AGE_CITAS

    print("\nLeyendo AGE_CITAS.parquet...")

    df_citas = pd.read_parquet(
        "output/AGE_CITAS.parquet"
    )

    sql_citas = """
    INSERT INTO AGE_CITAS (
        id_cita,
        pac_id,
        med_id,
        id_sede,
        fec_agendamiento,
        fec_cita_programada,
        hra_cita_programada,
        hra_llegada_paciente,
        hra_inicio_atencion,
        esp_solicitada,
        tip_cita,
        estado_cita
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cargar_por_lotes(
        conexion_sql,
        df_citas,
        "AGE_CITAS",
        "id_cita",
        [
            "id_cita",
            "pac_id",
            "med_id",
            "id_sede",
            "fec_agendamiento",
            "fec_cita_programada",
            "hra_cita_programada",
            "hra_llegada_paciente",
            "hra_inicio_atencion",
            "esp_solicitada",
            "tip_cita",
            "estado_cita"
        ],
        sql_citas,
        1000
    )

except Exception as error:
    print(error)