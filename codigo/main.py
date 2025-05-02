from matriculaHorario import *
from gruposAsignatura import *

##########

def main():
    matHor = MatriculaHorario("./jesus/matricula.csv", "./jesus/horariosgiit2.csv")

    clases = gruposAsignatura("./jesus/horariosgiit2.csv")

##########

main()