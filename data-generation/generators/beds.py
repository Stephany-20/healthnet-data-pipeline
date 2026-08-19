import random
from datetime import datetime, timedelta

import pandas as pd

def generar_camas(seed, cantidad, configuracion, df_sedes):
    random.seed(seed)
    registros = []

    #config.yaml
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

    sedes = df_sedes[
        [
            "id_sede",
            "tip_sede"
        ]
    ].to_dict("records")

    #generar registros
    for i in range(1, cantidad + 1):
        sede = random.choice(sedes)
        id_sede = sede["id_sede"]
        tipo_sede = sede["tip_sede"]

        if tipo_sede == "Hospital":
            tip_unidad = random.choice([
                "General",
                "General",
                "UCI",
                "Cirugía",
                "Urgencias"
            ])
        elif tipo_sede == "Clinica":
            tip_unidad = random.choice([
                "General",
                "General",
                "UCI",
                "Cirugía",
                "Urgencias"               
            ])
        elif tipo_sede == "Centro Medico":
            tip_unidad = random.choice([
                "General",
                "General",
                "Cirugía",
                "Urgencias"               
            ])
        else:
            tip_unidad == random.choice([
                "General",
                "Urgencias"               
            ])

        #capacidad según tipo de sede y unidad

        if tipo_sede == "Hospital":
            if tip_unidad == "General":
                capacidad = random.randint(80,180)
            elif tip_unidad == "UCI":
                capacidad = random.randint(15,40)
            elif tip_unidad == "Cirugía":
                capacidad = random.randint(15,35)
            else:
                capacidad = random.randint(20,60)
        elif tipo_sede == "Clinica":
            if tip_unidad == "General":
                capacidad = random.randint(40,100)
            elif tip_unidad == "UCI":
                capacidad = random.randint(8,25)
            elif tip_unidad == "Cirugía":
                capacidad = random.randint(8,20)
            else:
                capacidad = random.randint(10,35)
        elif tipo_sede == "Centro Medico":
            if tip_unidad == "General":
                capacidad = random.randint(10,30)
            elif tip_unidad == "Cirugía":
                capacidad = random.randint(3,10)
            else:
                capacidad = random.randint(5,15)  
        else:
            if tip_unidad == "General":
                capacidad = random.randint(1,5)
            else:
                capacidad = random.randint(1,5)               

        dias = random.randint(0, dias_periodo - 1)
        horas = random.randint(0, 23)
        minutos = random.randint(0, 59)

        fec_hora_registro = (
            fecha_inicio
            + timedelta(days=dias)
            + timedelta(hours=horas)
            +timedelta(minutes=minutos)
        )

        porcentaje_ocupacion = random.uniform(0.45,0.95)
        num_camas_ocupadas = int(capacidad * porcentaje_ocupacion)
        num_camas_disp = capacidad - num_camas_ocupadas

        registro = {
            "id_registro_cama": i,
            "id_sede": id_sede,
            "tip_unidad": tip_unidad,
            "fec_hora_registro": fec_hora_registro,
            "num_camas_ocupadas": num_camas_ocupadas,
            "num_camas_disp": num_camas_disp
        }

        registros.append(registro)

    df = pd.DataFrame(registros)
    return df