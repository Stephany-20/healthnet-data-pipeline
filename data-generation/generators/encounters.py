import random
from datetime import datetime, timedelta

import pandas as pd 

def generar_encuentros(seed, cantidad, configuracion, pacientes, medicos):
    random.seed(seed)
    encuentros = []

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

    #IDs existentes

    pacientes_ids = pacientes["pac_id"].tolist()
    medicos_ids = medicos["med_id"].tolist()
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

    # CIE-10

    diagnosticos = [
        "J06.9",
        "I10",
        "E11.9",
        "K21.9",
        "M54.5",
        "J18.9",
        "N39.0",
        "R51.9",
        "G43.9",
        "I25.1",
        "K29.7",
        "S93.4",
        "H10.9",
        "L20.9"
    ]

    #procedimientos 

    procedimientos =[
        "890201",
        "890301",
        "881202",
        "902210",
        "930101",
        "930801",
        "901101",
        "895101"
    ]

    #estados de factura

    estados_factura =[
        "Pagada",
        "Pendiente",
        "Objetada",
        "Anulada"
    ]

    #generar encuentros

    for i in range(1, cantidad + 1):

        #paciente
        pac_id = random.choice(pacientes_ids)
        #médico
        med_id = random.choice(medicos_ids)
        medico = medicos[medicos["med_id"] == med_id].iloc[0]
        #sede médico
        id_sede = int(medico["id_sede"])
        #fecha de registro
        dias = random.randint(0, dias_periodo - 1)
        fec_registro = (fecha_inicio+timedelta(days=dias))
        #hora aprox. registro
        hora = random.randint(7,20)
        minuto = random.randint(0,59)
        fec_registro = fec_registro.replace(hour=hora,minute=minuto,second=0)
        #inicio atención
        minutos_espera = random.randint(10,180)
        fec_inicio_atencion = (fec_registro + timedelta(minutes=minutos_espera))
        #egreso
        horas_atencion = random.randint(1,8)
        fec_egreso = (fec_inicio_atencion + timedelta(hours=horas_atencion))
        #tipo consulta
        if random.randint(1,100) <= 65:
            tip_consulta = "Control"
        else:
            tip_consulta = "Primera vez"
        #especialidad atendida
        esp_atendida = medico["esp_principal"]
        #diagnóstico principal y secundario
        diag_principal = random.choice(diagnosticos)
        diag_secundario = random.choice(diagnosticos)
        #procedimiento
        cod_procedimiento = random.choice(procedimientos)
        #valor facturado
        if tip_consulta == "Primera vez":
            vr_facturado = random.randint(80000,250000)
        else:
            vr_facturado = random.randint(50000,180000)
        #estado factura
        numero_factura = random.randint(1,100)

        if numero_factura <= 75:
            estado_factura = "Pagada"
        elif numero_factura <= 90:
            estado_factura = "Pendiente"
        elif numero_factura <=97:
            estado_factura = "Objetada"
        else:
            estado_factura = "Anulada"

        encuentro = {
            "id_encuentros": i,
            "pac_id":pac_id,
            "med_id": med_id,
            "id_sede": id_sede,
            "fec_registro": fec_registro,
            "fec_inicio_atencion": fec_inicio_atencion,
            "fec_egreso": fec_egreso,
            "tip_consulta": tip_consulta,
            "esp_atendida": esp_atendida,
            "diag_principal_cie10": diag_principal,
            "diag_sec1_cie10": diag_secundario,
            "cod_procedimiento": cod_procedimiento,
            "vr_facturado": vr_facturado,
            "estado_factura": estado_factura
        }

        encuentros.append(encuentro)

    df = pd.DataFrame(encuentros)
    return df