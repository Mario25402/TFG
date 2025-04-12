from matricula import *

listaMat = Matriculas("/home/mario/Escritorio/TFG/jesus/matricula.csv", "/home/mario/Escritorio/TFG/jesus/horariosgiit.csv")
print(listaMat.getAsignaturasAlumno('96867605'))
print(listaMat.getIndex(442))