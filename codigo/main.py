from matriculaHorario import *
from gruposAsignatura import *

##########

def main():
    matHor = MatriculaHorario("./jesus/matricula.csv", "./jesus/horariosgiit.csv")

    clases = gruposAsignatura("./jesus/horariosgiit.csv")

##########

main()