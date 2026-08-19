import random
from datetime import datetime, timedelta

import pandas as pd


def generar_citas(seed, cantidad, configuracion, df_pacientes, df_medicos):

    random.seed(seed)

    registros = []

    # Fechas del periodo
    fecha_inicio = datetime.strptime(
        configuracion["date_range"]["start"],
        "%Y-%m-%d"
    )

    fecha_fin = datetime.strptime(
        configuracion["date_range"]["end"],
        "%Y-%m-%d"
    )

    dias_periodo = (fecha_fin - fecha_inicio).days

    # Pacientes
    pacientes = df_pacientes[["pac_id"]].to_dict("records")

    # Médicos
    medicos = df_medicos[["med_id", "id_sede"]].to_dict("records")

    # Especialidades
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

    # Tipos de cita
    tipos_cita = [
        "Primera vez",
        "Control",
        "Seguimiento",
        "Urgencia"
    ]

    # Estados
    estados_cita = [
        "Atendida",
        "Atendida",
        "Atendida",
        "Cancelada",
        "No asistio",
        "Pendiente"
    ]

    # Generar citas
    for i in range(1, cantidad + 1):

        # Paciente
        paciente = random.choice(pacientes)
        pac_id = paciente["pac_id"]

        # Médico
        medico = random.choice(medicos)
        med_id = medico["med_id"]
        id_sede = medico["id_sede"]

        # Fecha de agendamiento
        dias_agendamiento = random.randint(0, dias_periodo - 31)

        fec_agendamiento = (
            fecha_inicio + timedelta(days=dias_agendamiento)
        )

        # Fecha de cita
        dias_hasta_cita = random.randint(1, 30)

        fec_cita_programada = (
            fec_agendamiento + timedelta(days=dias_hasta_cita)
        )

        # Hora programada
        hora = random.randint(7, 17)

        minutos = random.choice([
            0,
            15,
            30,
            45
        ])

        hra_cita_programada = f"{hora:02d}:{minutos:02d}:00"

        # Estado de la cita
        estado_cita = random.choice(estados_cita)

        # Inicialmente las horas son NULL
        hra_llegada_paciente = None
        hra_inicio_atencion = None

        # Hora de llegada
        if estado_cita in [
            "Atendida",
            "No asistio"
        ]:

            retraso = random.randint(-20, 30)

            hora_programada = datetime.strptime(
                hra_cita_programada,
                "%H:%M:%S"
            )

            hora_llegada = (
                hora_programada +
                timedelta(minutes=retraso)
            )

            hra_llegada_paciente = (
                hora_llegada.strftime("%H:%M:%S")
            )

        # Hora de inicio de atención
        if estado_cita == "Atendida":

            espera = random.randint(5, 60)

            hora_llegada = datetime.strptime(
                hra_llegada_paciente,
                "%H:%M:%S"
            )

            hora_inicio = (
                hora_llegada +
                timedelta(minutes=espera)
            )

            hra_inicio_atencion = (
                hora_inicio.strftime("%H:%M:%S")
            )

        # Especialidad
        esp_solicitada = random.choice(especialidades)

        # Tipo de cita
        tip_cita = random.choice(tipos_cita)

        # Registro
        registro = {
            "id_cita": i,
            "pac_id": pac_id,
            "med_id": med_id,
            "id_sede": id_sede,
            "fec_agendamiento": fec_agendamiento,
            "fec_cita_programada": fec_cita_programada,
            "hra_cita_programada": hra_cita_programada,
            "hra_llegada_paciente": hra_llegada_paciente,
            "hra_inicio_atencion": hra_inicio_atencion,
            "esp_solicitada": esp_solicitada,
            "tip_cita": tip_cita,
            "estado_cita": estado_cita
        }

        registros.append(registro)

    # Crear DataFrame
    df = pd.DataFrame(registros)

    return df

