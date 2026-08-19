import random
import hashlib
from datetime import datetime, timedelta

import pandas as pd 

def generar_medicos(seed,cantidad, configuracion):
    random.seed(seed)
    medicos = []

    #82 sedes que ya creé
    sedes = list(range(1,83))

    especialidades = [
        "Medicina General",
        "Medicina Interna",
        "Pediatria",
        "Cardiologia",
        "Cirugia General",
        "Urgencias",
        "Ginecologia",
        "Traumatologia",
        "Dermatologia",
        "Oftalmologia",
        "Anestesiologia"
    ]

    contratos = [
        "Planta",
        "Prestacion de Servicios",
        "Temporal"
    ]

    jornadas = [
        "Diurna",
        "Nocturna",
        "Mixta"
    ]

    estados = [
        "Activo",
        "Inactivo"
    ]

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

    #generar médicos
    for i in range(1, cantidad + 1):
        #especialidad principal
        especialidad_principal = random.choice(especialidades)
        #especialidad secundario
        especialidad_secundaria = random.choice(especialidades)

        while(especialidad_secundaria == especialidad_principal):
            especialidad_secundaria = random.choice(especialidades)

        #fecha ingreso
        anios_antiguedad = random.randint(0,15)
        dias_antiguedad = (anios_antiguedad * 365)
        

        fecha_ingreso =(fecha_fin-timedelta(days=dias_antiguedad))

        #tipo de contrato

        numero_contrato = random.randint(1,100)

        if numero_contrato <= 60:
            tip_contrato = "Planta"
        elif numero_contrato <= 90:
            tip_contrato = "Prestacion de Servicios"
        else:
            tip_contrato = "Temporal"

        #jornada
        numero_jornada = random.randint(1,100)
        if numero_contrato <= 50:
            jornada = "Diurna"
        elif numero_jornada <= 75:
            jornada = "Mixta"
        else:
            jornada = "Nocturna"

        #estado

        numero_estado = random.randint(1,100)
        if numero_estado <= 90:
            estado_activo = "Activo"
        else:
            estado_activo = "Inactivo"


        medico = {
            "med_id": i,
            "esp_principal": especialidad_principal,
            "esp_secundaria": especialidad_secundaria,
            "id_sede": random.choice(sedes),
            "fec_ingreso": fecha_ingreso.date(),
            "tip_contrato": tip_contrato,
            "jornada": jornada,
            "estado_activo": estado_activo
        }

        medicos.append(medico)

    df = pd.DataFrame(medicos)
    return df