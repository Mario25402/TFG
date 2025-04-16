from matricula import *
from auxiliar import *

listaMat = Matriculas("./jesus/matricula.csv", "./jesus/horariosgiit.csv")

combAlumnos = listaMat.getCombinacionSubgrupos()
combinacionSubgruposToString(combAlumnos)
    