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
        matAlumno = []
        for i in range(len(self.dnis)):
            matAlumno.append((self[i]))

        res = ""
        datos = self.buscarAsignatura(matAlumno)

        for i in range(len(datos)):
            for valores in datos[i].values():
                res += f"Alumno: {valores[0]}, Asignatura: {valores[1]}, Grupo: {valores[2]}, Horario: {valores[3]}\n"
        
        return res
    
    def buscarAsignatura(self, matricula):
        asignaturas = []

        for i in range(len(matricula)):
            for j in range(self.asignaturas.getLongitud()):
                asignatura = f"{matricula[i][1]}..{matricula[i][2]}"

                if re.fullmatch(asignatura, self.asignaturas[j][0]) and matricula[i][3] == self.asignaturas[j][2]:
                    asignaturas.append({i: (matricula[i][0], self.asignaturas[j][0], self.asignaturas[j][2], self.asignaturas.getHorario(j))})
                    break
                                
        return asignaturas
    
    def getMatriculaciones(self):
        # Clave: alumno
        # Valor: [(asignatura0, grupo0, horas0), (asignatura1, grupo1, horas1), ...]
        
        matAlumno = []
        for i in range(len(self.dnis)):
            matAlumno.append((self[i]))

        datos = self.buscarAsignatura(matAlumno)

        actual = None
        anterior = None
        asignaturas = []
        matriculaciones = {}

        for i in range(len(datos)):
            for valores in datos[i].values():
                actual = valores[0]
                asignaturas.append((valores[1], valores[2], valores[3]))

            if i == 0: 
                anterior = actual

            if actual != anterior:
                matriculaciones[anterior] = asignaturas

                asignaturas = []
                anterior = actual

        return matriculaciones