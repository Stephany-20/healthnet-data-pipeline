import random
import pandas as pd

def generar_sedes(seed, cantidad):
    random.seed(seed)

    sedes = []

    ciudades = [
        ("Bogota", 1, 1),
        ("Medellin", 2, 1),
        ("Cali", 3, 1),
        ("Barranquilla", 4, 1),
        ("Cartagena", 5, 1),
        ("Pereira", 6, 1),
        ("Manizales", 7, 1),
        ("Armenia", 8, 1),
        ("Lima", 9, 2),
        ("Quito", 10, 3),
    ]

    tipos_sede = []

    for i in range(3):
        tipos_sede.append("Hospital")

    for i in range(16):
        tipos_sede.append("clinica")

    for i in range(42):
        tipos_sede.append("Centro Medico")

    for i in range(21): 
        tipos_sede.append("Centro Diagnostico")

    random.shuffle(tipos_sede)

    for i in range(1, cantidad + 1):
        ciudad = random.choice(ciudades)
        tipo = tipos_sede[i - 1]

        if tipo == "Hospital":
            camas_general = random.randint(100, 300)
            camas_uci = random.randint(30, 80)
            camas_cirugia = random.randint(15, 40)
            camas_urgencias = random.randint(30, 70)
            complejidad = "Alta"
        elif tipo == "Clinica":
            camas_general = random.randint(60, 180)
            camas_uci = random.randint(10, 50)
            camas_cirugia = random.randint(10, 30)
            camas_urgencias = random.randint(20, 50)
            complejidad = random.choice(["Media", "Alta"])
        elif tipo == "Centro Medico":
            camas_general = random.randint(10, 50)
            camas_uci = random.randint(0, 10)
            camas_cirugia = random.randint(0, 5)
            camas_urgencias = random.randint(5, 20)
            complejidad = random.choice(["Baja", "Media"])
        else:
            camas_general = random.randint(0, 10)
            camas_uci = 0
            camas_cirugia = 0
            camas_urgencias = random.randint(0, 5)
            complejidad = "Baja"

        sede = {
            "id_sede": i,
            "nom_sede": tipo + " HealthNet " + str(i),
            "tip_sede": tipo,
            "id_ciudad": ciudad[1],
            "id_pais": ciudad[2],
            "cap_camas_gen": camas_general,
            "cap_camas_uci": camas_uci,
            "cap_camas_cirugia": camas_cirugia,
            "cap_camas_urg": camas_urgencias,
            "nivel_complejidad": complejidad
        } 

        sedes.append(sede)

    df = pd.DataFrame(sedes)

    return df
              

               
