import sys
import consultaAsignatura

from pathlib import Path
from matriculaHorario import *
from gruposAsignatura import *

##########

DIR_PATH = Path(__file__).parent.resolve()

def main():
    sys.setrecursionlimit(5000)

    ###
    # Primer Cuatrimestre

    matHor1 = matriculaHorario(DIR_PATH / ".." / "data" / "matricula.csv", DIR_PATH / ".." / "data" / "horarios1.csv")
    clases1 = gruposAsignatura(DIR_PATH / ".." / "data" / "horarios1.csv", matHor1.combinaciones, matHor1.datos, matHor1.getSinAsignar())

    clases1.asignarAsignaturas()
    clases1.getResultsAlumno()

    ###
    # Segundo Cuatrimestre

    matHor2 = matriculaHorario(DIR_PATH / ".." / "data" / "matricula.csv", DIR_PATH / ".." / "data" / "horarios2.csv")
    clases2 = gruposAsignatura(DIR_PATH / ".." / "data" / "horarios2.csv", matHor2.combinaciones, matHor2.datos, matHor2.getSinAsignar())

    clases2.asignarAsignaturas()
    clases2.getResultsAlumno()

    ###
    # PDF
    
    consultaAsignatura.execute()

##########

main()