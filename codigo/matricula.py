import re
import pandas as pd
from asignatura import Asignaturas

class Matriculas():
    def __init__(self, archivoMatricula, archivoAsignaturas):
        df = pd.read_csv(archivoMatricula)
        self.carreras = df["CARRERA"].tolist()
        self.dnis = df["DNI"].tolist()
        self.codigos = df["CEA"].tolist()
        self.grupos = df["GRUPO"].tolist()

        self.asignaturas = Asignaturas(archivoAsignaturas)

    def __getitem__(self, index):
        return self.dnis[index], self.carreras[index], self.codigos[index], self.grupos[index]
    
    def __str__(self):
        res = ""
        usados = []
        grupos = []

        for i in range(len(self.dnis)):
            if usados.count(self.dnis[i]) == 0:
                usados.append(self.dnis[i])
                
                for j in range(len(self.dnis)):
                    if self.dnis[j] == self.dnis[i]:
                        grupos.append(self.grupos[j])

            print(f"Grupo: {grupos}")
            res += f"Alumno: {self.dnis[i]} - Asignaturas: {self.buscarAsignatura(self.dnis[i], grupos)}\n"

        return res
    
    def buscarAsignatura(self, alumno, grupos):
        asignaturas = []
        usados = []

        for i in range(len(self.dnis)):
            if self.dnis[i] == alumno:
                codigo = f"{self.carreras[i]}..{self.codigos[i]}"

                for j in range(self.asignaturas.getLongitud()):
                    if re.fullmatch(codigo, self.asignaturas[j][0]):
                        for k in range(len(grupos)):
                            if grupos[k] == self.asignaturas[j][2]:
                                asignaturas.append(self.asignaturas[j])
                                usados.append(grupos[k])
                                grupos.pop(k)

                                if len(grupos) == 0:
                                    grupos = usados
                                    usados.clear()
                                break
                                
        
        return asignaturas
    






""" import re
import pandas as pd
from asignatura import Asignaturas

class Matriculas():
    def __init__(self, archivoMatricula, archivoAsignaturas):
        df = pd.read_csv(archivoMatricula)
        self.carreras = df["CARRERA"].tolist()
        self.dnis = df["DNI"].tolist()
        self.codigos = df["CEA"].tolist()
        self.grupos = df["GRUPO"].tolist()

        self.asignaturas = Asignaturas(archivoAsignaturas)

    def __str__(self):
        res = ""
        usados = []

        for i in range(len(self.dnis)):
            if usados.count(self.dnis[i]) == 0:
                usados.append(self.dnis[i])
                
            res += f"Alumno: {self.dnis[i]} - Asignaturas: {self.buscarAsignatura(self.dnis[i])}\n"

        return res
    
    def buscarAsignatura(self, alumno):
        asignaturas = []

        for i in range(len(self.dnis)):
            if self.dnis[i] == alumno:
                codigo = f"{self.carreras[i]}..{self.codigos[i]}"

                for j in range(self.asignaturas.getLongitud()):
                    if re.fullmatch(codigo, self.asignaturas[j][0]):
                            asignaturas.append(self.asignaturas[j])
        
        return asignaturas """