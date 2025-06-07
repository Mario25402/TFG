import sys
from matriculaHorario import *
from gruposAsignatura import *

##########

def main():
    sys.setrecursionlimit(10000)

    ###
    # Primer Cuatrimestre

    matHor = MatriculaHorario("./jesus/matricula.csv", "./jesus/horariosgiit1.csv")
    clases = gruposAsignatura("./jesus/horariosgiit1.csv")

    clases.getAulasRellenas(matHor.combinaciones)

    ###
    # Segundo Cuatrimestre

    #matHor = MatriculaHorario("./jesus/matricula.csv", "./jesus/horariosgiit2.csv")
    #clases = gruposAsignatura("./jesus/horariosgiit2.csv")

    #clases.getAulasRellenas(matHor.combinaciones)

##########

main()