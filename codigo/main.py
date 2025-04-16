from matricula import *
from auxiliar import *
from matriculaHorario import *

####################

"""listaMat = Matriculas("./jesus/matricula.csv", "./jesus/horariosgiit.csv")

combAlumnos = listaMat.getCombinacionSubgrupos()
combinacionSubgruposToString(combAlumnos)"""

##########

def main():
    matHor = MatriculasHorarios("./jesus/matricula.csv", "./jesus/horariosgiit.csv")

##########

main()    