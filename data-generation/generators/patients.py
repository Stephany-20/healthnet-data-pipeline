import random
import hashlib
from datetime import datetime, timedelta

import pandas as pd 

def generar_pacientes(seed, cantidad, configuracion):
    random.seed(seed)

    pacientes = []

    #ciudades que uso en RED_SEDES
    ciudades = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
    ]

    tipos_documento =[
        "CC",
        "CE",
        "TI"
    ]

    generos =[
        "F",
        "M"
    ]



 # crear las 42 EPS y aseguradoras

    entidades = []

    cantidad_eps = configuracion["aseguradoras"]["eps"]
    cantidad_aseguradoras = configuracion["aseguradoras"]["aseguradoras"]

    for i in range(1, cantidad_eps + 1):
        entidad = {
            "id": i,
            "nombre": "EPS HealthNet "+ str(i)
        }

        entidades.append(entidad)

    for i in range(1, cantidad_aseguradoras + 1):
        numero = cantidad_eps + i
        entidad = {
            "id": numero,
            "nombre": "Aseguradora HealthNet" + str(i)
        }
        entidades.append(entidad)

# fechas tomadas desde config.yaml
    fecha_inicio = datetime.strptime(
        configuracion["date_range"]["start"], 
        "%Y-%m-%d"
        )

    fecha_fin = datetime.strptime(
        configuracion["date_range"]["end"],
        "%Y-%m-%d"
    )

    dias_periodo = (
        fecha_fin - fecha_inicio
    ).days

#crear pacientes

    for i in range(1, cantidad + 1):
        #edad
        numero_edad = random.randint(1,100)
        if numero_edad <= 8:
            edad = random.randint(0,17)
        elif numero_edad <= 70:
            edad = random.randint(18,64)
        elif numero_edad <=90:
            edad = random.randint(65,79)
        else:
            edad = random.randint(80,95)

        #fecha de nacimiento

        fecha_referencia = fecha_fin

        fecha_nacimiento =(
            fecha_referencia - timedelta(days=edad * 365)
        )

        #primera atencion

        dias_desde_inicio = random.randint(
            0,
            dias_periodo - 1
        )
        fecha_primera_atencion = (
            fecha_inicio + timedelta(days=dias_desde_inicio)
        )

        #documento 

        tipo_documento = random.choice(tipos_documento)

        documento = str(10000000 + i)

        texto_documento = (tipo_documento + documento)

        documento_hash = hashlib.sha256(texto_documento.encode()).hexdigest()

        # ciudad

        ciudad = random.choice(ciudades)

        #tipo de financiación

        numero_financiacion = random.randint(1,100)

        if numero_financiacion <= 68:
            #68% financiado EPS/Aseguradoras
            if random.randint(1,100) <= 50:
                tipo_aseguradora = "EPS"
            else: 
                tipo_aseguradora = "Aseguradora"

            entidad = random.choice(entidades)
            id_eps = entidad["id"]
        else:
            #32% corresponde a particulares y otras fuentes
            tipo_aseguradora = "Particular"
            id_eps = None

        #estrato

        estrato = random.randint(1,6)

        #paciente activo

        activo = random.choices( [1,0], weights=[90,10])[0]

        paciente ={
            "pac_id": i,
            "tip_doc": tipo_documento,
            "num_doc_hash": documento_hash,
            "fec_nac": fecha_nacimiento.date(),
            "genero": random.choice(generos),
            "id_ciudad_res": ciudad,
            "tip_aseguradora": tipo_aseguradora,
            "id_eps": id_eps,
            "estrato_socioec": estrato,
            "fec_primer_atencion": fecha_primera_atencion.date(),
            "activo": activo
        }

        pacientes.append(paciente)

    df = pd.DataFrame(pacientes)

    return df