from matriculaHorario import *
from gruposAsignatura import *
import sys

##########

def main():
    sys.setrecursionlimit(10000)
    matHor = MatriculaHorario("./jesus/matricula.csv", "./jesus/horariosgiit2.csv")

    clases = gruposAsignatura("./jesus/horariosgiit2.csv")
    clases.getAulasRellenas(matHor.combinaciones)

##########

main()