from auxiliar import translateHora, translateDia
import pandas as pd

########################

class Asignaturas:
    def __init__(self, archivo):
        df = pd.read_csv(archivo)
        self.codigos = df["CODIGO"].tolist()
        self.nombres = df["ASIGNATURA"].tolist()
        self.grupo = df["GRUPO"].tolist()

        hora1 = df["HORA1"].tolist()
        hora2 = df["HORA2"].tolist()
        hora3 = df["HORA3"].tolist()
        hora4 = df["HORA4"].tolist()
        hora5 = df["HORA5"].tolist()

        self.horas = [hora1, hora2, hora3, hora4, hora5]

    ####################

    # Codigo, abreviatura, (sub)grupo
    ## Necesario en: Matriculas.buscarAsignatura
    def __getitem__(self, index):
        return self.codigos[index], self.nombres[index], self.grupo[index]

    ####################
    
    # Código: abreviatura - (sub)grupo -> Dia(s): hora(s)
    ## Necesario en: 
    def __str__(self):
        res = ""

        for i in range(len(self.codigos)):
            res += f"{self.codigos[i]}: {self.nombres[i]} - {self.grupo[i]} -> {self.getHorario(i)}\n"

        return res
    
    ####################

    # Número de asignaturas en el archivo
    ## Necesario en: Matriculas.buscarAsignatura
    def getLongitud(self):
        return len(self.codigos)
    
    ####################
    
    # "Dia(s): hora(s)" de la asignatura "index"
    ## Necesario en:
    def getHorario(self, index):
        res = ""
        
        for i in range(len(self.horas)):
            elemento = str(self.horas[i][index])

            if elemento != "nan":
                res += f"{translateDia(elemento)}: {translateHora(elemento)} - "
            
        return res[:-3] # Eliminar último guión
    
    ####################

    # "Dia(s): hora(s)" de una asignatura con grupo
    ## Necesario en: Matriculas.buscarAsignatura
    def getHorario(self, asignatura, grupo):
        res = ""
        
        for i in range(len(self.codigos)):
            if self.codigos[i] == asignatura and self.grupo[i] == grupo:

                for j in range(len(self.horas)):
                    elemento = str(self.horas[j][i])

                    if elemento != "nan":
                        res += f"{translateDia(elemento)}: {translateHora(elemento)} - "
                
                return res[:-3]
            
    ####################

    # Lista de los códigos horarios para una asignatura y grupo
    ## Necesario en Matriculas.solapamiento
    def getCodigoHoras(self, asignatura, grupo):
        res = []
        
        for i in range(len(self.codigos)):
            if self.codigos[i] == asignatura and self.grupo[i] == grupo:
                res.append(self.horas[i])

        return res
    
    ####################