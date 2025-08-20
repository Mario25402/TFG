import sys
from matriculaHorario import *
from gruposAsignatura import *

##########

def main():
    sys.setrecursionlimit(10000)

    ###
    # Primer Cuatrimestre

    matHor1 = MatriculaHorario("./jesus/matricula.csv", "./jesus/horariosgiit1.csv")
    clases1 = gruposAsignatura("./jesus/horariosgiit1.csv", matHor1.combinaciones, matHor1.datos, matHor1.getSinAsignar())

    clases1.getResultsAsignaturas()
    clases1.getResultsAlumno()

    ###
    # Segundo Cuatrimestre

    matHor2 = MatriculaHorario("./jesus/matricula.csv", "./jesus/horariosgiit2.csv")
    clases2 = gruposAsignatura("./jesus/horariosgiit2.csv", matHor2.combinaciones, matHor2.datos, matHor2.getSinAsignar())

    clases2.getResultsAsignaturas()
    clases2.getResultsAlumno()

##########

main()