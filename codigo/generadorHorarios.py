import os
import pandas as pd

########################

class ProcesadorHorarios:
    def __init__(self, archivo):
        self.dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}
        self.filasHoras = {
            5: "01",
            7: "02",
            9: "03",
            11: "04",
            13: "05",
            15: "06",
            17: "07",
            18: "08",
            20: "09",
            22: "10",
            24: "11",
            26: "12",
            28: "13",
            37: "01",
            39: "02",
            41: "03",
            43: "04",
            45: "05",
            47: "06",
            49: "07",
            50: "08",
            52: "09",
            54: "10",
            56: "11",
            58: "12",
            60: "13"
        }

        extension = os.path.splitext(archivo)[1].lower()
        if extension == ".ods":
            df = pd.read_excel(archivo, header=None, engine="odf")
        elif extension == ".xlsx":
            df = pd.read_excel(archivo, header=None, engine="openpyxl")
        else:
            raise ValueError("Formato soportados .ods o .xlsx")
        
        info = {1: 2, 2: 5, 3: 8, 4: 11, 5: 14}
        

horarios = ProcesadorHorarios("../jesus/HorariosGII(24-25).xlsx")