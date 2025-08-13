import sys
from matriculaHorario import *
from gruposAsignatura import *

##########

def main():
    sys.setrecursionlimit(10000)

    ###
    # Primer Cuatrimestre

    matHor = MatriculaHorario("./jesus/matricula.csv", "./jesus/horariosgiit1.csv")
    clases = gruposAsignatura("./jesus/horariosgiit1.csv", matHor.combinaciones, matHor.datos, matHor.getSinAsignar())

    clases.getResults()

    ###
    # Segundo Cuatrimestre

    matHor = MatriculaHorario("./jesus/matricula.csv", "./jesus/horariosgiit2.csv")
    clases = gruposAsignatura("./jesus/horariosgiit2.csv", matHor.combinaciones, matHor.datos, matHor.getSinAsignar())

    clases.getResults()

##########

main()

# 296: Info
# 297: InfoMates
# 216: InfoAde
# 221: Teleco 