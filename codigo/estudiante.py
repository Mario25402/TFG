class Estudiante:
    def __init__(self, dni, asignaturas):
        self.dni = dni
        self.asignaturas = asignaturas

    def __str__(self):
        res = f"Estudiante: {self.dni}\n"

        for asignatura in self.asignaturas:
            res += f"\n/////\n\n {asignatura}\n"

        return res
