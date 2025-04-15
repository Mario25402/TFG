from auxiliar import translateHora, translateDia
import pandas as pd

########################

class Asignaturas:
    def __init__(self, archivo):
        df = pd.read_csv(archivo)

        self.codigos = df["CODIGO"].tolist()
        self.nombres = df["ASIGNATURA"].tolist()
        self.grupo = df["GRUPO"].tolist()
        self.horas = [df[f"HORA{i}"].tolist() for i in range(1, 6)]

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

        for i in range(self.getLongitud()):
            res += f"{self.codigos[i]}: {self.nombres[i]} - {self.grupo[i]} -> {self.getHorario(i)}\n"

        return res
    
    ########################################
    ########################################

    # Número de asignaturas en el archivo
    ## Necesario en: Matriculas.buscarAsignatura
    def getLongitud(self):
        return len(self.codigos)
    
    ####################

    # "Dia(s): hora(s)" de una asignatura con grupo
    ## Necesario en: Matriculas.buscarAsignatura
    def getHorario(self, asignatura, grupo):
        res = ""
        
        for i in range(self.getLongitud()):
            if self.codigos[i] == asignatura and self.grupo[i] == grupo:

                for j in range(len(self.horas)):
                    elemento = str(self.horas[j][i])

                    if elemento != "nan":
                        res += f"{translateDia(elemento)}: {translateHora(elemento)} - "
                
                return res[:-3]
            
    ########################################

    # Lista de los códigos horarios para una asignatura y grupo
    ## Necesario en Matriculas.solapamiento
    def getCodigoHoras(self, asignatura, grupo):
        res = []

        for i in range(self.getLongitud()):
            if self.codigos[i] == asignatura and self.grupo[i] == grupo:
    
                for j in range(len(self.horas)):
                    if not pd.isna(self.horas[j][i]):
                        res.append(int(float(self.horas[j][i])))

        return res
    
    ########################################
    ########################################