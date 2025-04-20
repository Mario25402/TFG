import re
import pandas as pd

class gruposAsignatura:
    def __init__(self, fileHorario):
        # Procesar archivo 
        df = pd.read_csv(fileHorario)

        codigos = df["CODIGO"].tolist()
        nombres = df["ASIGNATURA"].tolist()
        grupos = df["GRUPO"].tolist()
        hora1 = df["HORA1"].tolist()
        hora2 = df["HORA2"].tolist()
        hora3 = df["HORA3"].tolist()
        hora4 = df["HORA4"].tolist()
        hora5 = df["HORA5"].tolist()

        horas = [df[f"HORA{i}"].tolist() for i in range(1, 6)]

        ###
        # Rellenar "datos"
        
        self.datos = {}

        for i in range(len(codigos)):
            clave = (nombres[i], grupos[i])
            codigoHoras = [int(x) for lista in horas for x in [lista[i]] if pd.notna(x)]

            self.datos[clave] = {
                "codigo" : codigos[i],
                "aula": None,
                "capacidadTotal" : 30,
                "capacidadActual" : 0,
                "alumnos": [],
                "horario": codigoHoras,
                "subgrupos": None
            }
        
        ###
        # Ajustar capacidades a subgrupos y rellenar alumnos
        
        self.corregirSubgrupos(codigos, grupos)
        self.rellenarAlumnos()

    ####################

    def corregirSubgrupos(self, codigos, grupos):
        for clave, datos in self.datos.items():
            if len(clave[1]) == 1:
                subgrupos = []
                patron = f"{clave[1]}."

                for i in range(len(codigos)):
                    if codigos[i] == self.datos[clave]["codigo"] and re.fullmatch(patron, grupos[i]):
                        subgrupos.append(grupos[i])

                self.datos[clave]["subgrupos"] = subgrupos
                self.datos[clave]["capacidadTotal"] *= len(self.datos[clave]["subgrupos"]) 

    ####################

    def rellenarAlumnos(self):
        pass