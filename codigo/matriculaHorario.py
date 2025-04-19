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
        self.combinaciones = {} # Combinaciones de subgrupos posibles

        for alumno in dnis:
            self.datos[alumno] = []
            self.sinAsignar[alumno] = []
            self.asignados[alumno] = []
            self.combinaciones[alumno] = []

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

        # Rellenar "combinaciones"
        self.getCombinacionSubgrupos()
        
    ####################

    def getCombinacionSubgrupos(self):
        for alumno in self.datos.keys():
            subgrupos = sorted(self.sinAsignar[alumno], key=lambda x: (x['codigo'], x['grupo']))

            self.combinarSubgrupos(subgrupos, self.datos[alumno], self.combinaciones[alumno], len(self.datos[alumno])*2)
                        
    ###

    def combinarSubgrupos(self, subgruposAlumno, actual, combinaciones, longitud, start=0):
        if len(actual) == longitud:
            ordenada = sorted(actual, key=lambda x: (x['codigo'], x['grupo']))
            combinaciones.append(ordenada)
            return

        for i in range(start, len(subgruposAlumno)):
            if self.factible(subgruposAlumno[i], actual):
                actual.append(subgruposAlumno[i])
                
                self.combinarSubgrupos(subgruposAlumno, actual, combinaciones, longitud, i+1)

                actual.pop()

    ###

    def factible(self, nuevo, actual):
        asignadas = []
        apariciones = 0

        for entrada in actual:
            if entrada['codigo'] == nuevo['codigo']:
                apariciones += 1

        # Solo un grupo de teoría y un subgrupo de prácticas
        if apariciones == 1:
            for entrada in actual:
                for hora in entrada['horario']:
                    asignadas.append(hora)
                    
            for hora in nuevo['horario']:
                if hora in asignadas:
                    return False
                    
            return True
        
        else:
            return False
    
    ####################