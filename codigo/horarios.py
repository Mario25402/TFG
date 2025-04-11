from auxiliar import *

class Horarios:
    def __init__(self):
        self.asignatura = []
        self.horario = []

    def __str__(self):
        res = ""

        for i in range(0, len(self.asignatura)):
            res += f"Asignatura: {self.asignatura[i]}\n\n"
            res += "Horario:\n"
        
            for j in range(len(self.horario[i])):
                res += f"Grupo: {j}, Día: {translateDia(self.horario[i][j])}, Hora: {translateHora(self.horario[i][j])}\n"

            res += "\n/////\n\n"

        return res
    
    def append(self, asignatura, horario):
        self.asignatura.append(asignatura)
        self.horario.append(horario)