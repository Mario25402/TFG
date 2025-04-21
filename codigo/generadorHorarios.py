import os
import re
import pandas as pd

class ProcesadorHorarios:
    def __init__(self, archivo):
        ###
        # Procesar archivo según extensión
        extension = os.path.splitext(archivo)[1].lower()

        if extension == ".ods":
            horarios = pd.read_excel(archivo, sheet_name=None, header=None, engine="odf")
        elif extension == ".xlsx":
            horarios = pd.read_excel(archivo, sheet_name=None, header=None, engine="openpyxl")
        else:
            raise ValueError("Formato soportados .ods o .xlsx")
        
        ###
        # Inicializar variables

        self.datos = {}

        aula = None
        subgrupo = None
        asignatura = None

        ###
        # Recorrer las páginas y extraer la información
        
        for pagina, df in horarios.items():
            for numCol in range(df.shape[1]):
                for numFila in range(df.shape[0]):
                    celda = df.iat[numFila, numCol]

                    if pd.notna(celda):
                        # Extraer curso
                        if (numFila == 1 or numFila == 33) and numCol == 0:
                            curso = celda.strip()[0]
                            grupo = celda.strip()[3]

                        # Extraer cuatrimestre
                        elif (numFila == 2 or numFila == 34) and numCol == 0:
                            cuatrimestre = celda.strip()[0]

                        # Extraer asignatura y aula
                        elif ((numFila > 3 and numFila <= 28) or (numFila > 35 and numFila <= 60)) and (numCol >= 1 and numCol <= 16):
                            if numFila % 2 == 0:
                                asignatura = celda

                                patron = rf"\({grupo}(\d+)\)"
                                match = re.search(patron, asignatura)
                                if match:
                                    subgrupo = f"{grupo}{match.group(1)}"
                                    asignatura = re.sub(patron, "", asignatura).strip()

                            else:
                                aula = celda

                            ###
                            # Guardar datos en el diccionario

                            if asignatura and aula:
                                codigo = self.traducirCodigo(numFila-1, numCol)

                                s_gp = grupo
                                if subgrupo:
                                    s_gp = subgrupo

                                self.datos[codigo] = {
                                    "asignatura": asignatura,
                                    "aula": aula,
                                    "curso": curso,
                                    "grupo": s_gp,
                                    "cuatrimestre": cuatrimestre
                                }

                                aula = None
                                subgrupo = None
                                asignatura = None

    ####################

    def traducirCodigo(self, fila, columna):
        dia = None
        if columna >= 1 and columna <= 3:
            dia = "1" # Lunes
        elif columna >= 4 and columna <= 6:
            dia = "2" # Martes
        elif columna >= 7 and columna <= 9:
            dia = "3" # Miércoles
        elif columna >= 10 and columna <= 12:
            dia = "4" # Jueves
        elif columna >= 13 and columna <= 15:
            dia = "5" # Viernes

        ###
        
        hora = None
        if fila == 4 or fila == 36:
            hora = "01"
        elif fila == 6 or fila == 38:
            hora = "02"
        elif fila == 8 or fila == 40:
            hora = "03"
        elif fila == 10 or fila == 42:
            hora = "04"
        elif fila == 12 or fila == 44:
            hora = "05"
        elif fila == 14 or fila == 46:
            hora = "06"
        elif fila == 17 or fila == 49:
            hora = "07"
        elif fila == 19 or fila == 51:
            hora = "08"
        elif fila == 21 or fila == 53:
            hora = "09"
        elif fila == 23 or fila == 55:
            hora = "10"
        elif fila == 25 or fila == 57:
            hora = "11"
        elif fila == 27 or fila == 59:
            hora = "12"
        
        ###

        return f"{dia}{hora}"
                
    ####################

horarios = ProcesadorHorarios("./jesus/HorariosGII(24-25).xlsx")