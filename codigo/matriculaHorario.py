import pandas as pd
import re

class MatriculasHorarios():
    def __init__(self, fileMat, fileHor):
        df = pd.read_csv(fileMat)

        carreras = df["CARRERA"].tolist()
        dnis = df["DNI"].tolist()
        codigos = df["CEA"].tolist()
        grupos = df["GRUPO"].tolist()

        ###

        df = pd.read_csv(fileHor)

        codigosCompletos = df["CODIGO"].tolist()
        nombres = df["ASIGNATURA"].tolist()
        gruposTP = df["GRUPO"].tolist()
        hora1 = df["HORA1"].tolist()
        hora2 = df["HORA2"].tolist()
        hora3 = df["HORA3"].tolist()
        hora4 = df["HORA4"].tolist()
        hora5 = df["HORA5"].tolist()

        horas = [df[f"HORA{i}"].tolist() for i in range(1, 6)]

        ###

        self.datos = {}         # Datos trascritos de los archivos
        self.sinAsignar = {}    # Datos de subgrupos posibles
        self.asignados = {}     # Datos de subgrupos asignados

        for i in range(len(dnis)):
            self.datos[dnis[i]] = []
            self.sinAsignar[dnis[i]] = []
            self.asignados[dnis[i]] = []

        ###

        for i in range(len(dnis)):
            patronSgn = f"{carreras[i]}..{codigos[i]}"
            patronSgp = f"{grupos[i]}."

            for j in range(len(codigosCompletos)):
                if re.fullmatch(patronSgn, codigosCompletos[j]):
                    if grupos[i] == gruposTP[j]:
                        codigoHoras = [int(x) for lista in horas for x in [lista[j]] if pd.notna(x)]

                        self.datos[dnis[i]].append({
                            "codigo": codigosCompletos[j],
                            "asignatura": nombres[j],
                            "grupo": grupos[i],
                            "horario": codigoHoras
                        })

                    elif re.fullmatch(patronSgp, gruposTP[j]):
                        codigoHoras = [int(x) for lista in horas for x in [lista[j]] if pd.notna(x)]

                        self.sinAsignar[dnis[i]].append({
                            "codigo": codigosCompletos[j],
                            "asignatura": nombres[j],
                            "grupo": gruposTP[j],
                            "horario": codigoHoras
                        })

        ###