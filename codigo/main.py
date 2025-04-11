from asignatura import *
from matricula import *

"""
# Horario
horario = Horarios()
horario.append("2961101", ["101", "202", "303", "104"])
horario.append("2961102", ["102", "203", "304", "105"])
horario.append("2961103", ["103", "204", "305", "106"])

#####
# Asignatura
alem = Asignatura("2961101", "A")
calculo = Asignatura("2961102", "A")

#####
# Estudiante
asignaturas = [alem, calculo]

estudiante = Estudiante("12345678A", asignaturas)
#print(estudiante)

#####
# EXCELL

asignatura = translateAsignatura("2961154", "../externos/asignaturasII.ods")
print(asignatura) 
"""

listaAsig = Asignaturas("../jesus/horariosgiit.csv")
#print(listaAsig[0])

listaMat = Matriculas("../jesus/matricula.csv", "../jesus/horariosgiit.csv")
print(listaMat)

