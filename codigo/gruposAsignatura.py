import re
import pandas as pd

class gruposAsignatura:
    def __init__(self, fileHorario):
        # Procesar archivo 
        df = pd.read_csv(fileHorario)

        codigos = df["CODIGO"].tolist()
        nombres = df["ASIGNATURA"].tolist()
        grupos = df["GRUPO"].tolist()
        #aulas = df["AULA"].tolist()
        horas = [df[f"HORA{i}"].tolist() for i in range(1, 6)]

        ###
        # Rellenar "datos"
        
        self.datos = {}

        for i in range(len(codigos)):
            clave = (nombres[i], grupos[i])
            codigoHoras = [int(x) for lista in horas for x in [lista[i]] if pd.notna(x)]

            self.datos[clave] = {
                "codigo" : codigos[i],
                "aula": None, #aulas[i],
                "capacidadTotal" : 30,
                "capacidadActual" : 0,
                "alumnos": [],
                "horario": codigoHoras,
                "subgrupos": None
            }
        
        ###
        # Ajustar capacidades a subgrupos y rellenar alumnos
        
        self.corregirSubgrupos(codigos, grupos)

    ####################

    # Ajusta la capacidad de los grupos a la unión de la de los subgrupos
    def corregirSubgrupos(self, codigos, grupos):
        for clave, datos in self.datos.items():
            if len(clave[1]) == 1:
                subgrupos = []
                patron = f"{clave[1]}."

                for i in range(len(codigos)):
                    if codigos[i] == self.datos[clave]["codigo"] and re.fullmatch(patron, grupos[i]):
                        subgrupos.append(grupos[i])

                self.datos[clave]["subgrupos"] = subgrupos
                self.datos[clave]["capacidadTotal"] *= len(self.datos[clave]["subgrupos"]) 

    ####################

    def getAulasRellenas(self, alumnos):
        for clave, datos in self.datos.items():

            # Rellenar grupos de teoria
            if len(clave[1]) == 1:
                combMatriculados = self.__filtrarAlumnos(alumnos, clave)
                self.rellenarGruposTeoria(combMatriculados)

            """ while datos["capacidadActual"] < datos["capacidadTotal"]:
                for alumnos in combMatriculados:
                    self.rellenarAlumnos(datos, alumnos, [], [], 0) """

    ###

    # Añadir alumno a todos sus grupos de teoría
    def rellenarGruposTeoria(self, alumnos):
        for alumno, combinaciones in alumnos.items():
            for asignatura in combinaciones[0]:
                if len(asignatura["grupo"]) == 1:
                    clave = (asignatura["asignatura"], asignatura["grupo"])

                    if alumno not in self.datos[clave]["alumnos"]:
                        self.datos[clave]["alumnos"].append(alumno)
                        self.datos[clave]["capacidadActual"] += 1
                        
    ###

    def rellenarAlumnos(self, asignatura, alumnos, actual, mejorRelleno, mejorPuntuacion):
        if asignatura["capacidadActual"] == asignatura["capacidadTotal"]:
            puntuacionActual = self.getPuntuacion(alumnos)

            # Actualizar mejor combinacion
            if puntuacionActual > mejorPuntuacion:
                mejorRelleno = actual.copy()                
                mejorPuntuacion = puntuacionActual.copy()

            return
        
        ###

        for alumno, combinaciones in alumnos.items():
            for combinacion in combinaciones:
                if self.factible(alumno, combinacion.copy(), actual):
                    actual.append(alumno)
                    asignatura["capacidadActual"] += 1

                    alumnos[alumno].remove(combinacion)
                    self.rellenarAlumnos(asignatura, alumnos, actual, mejorRelleno, mejorPuntuacion)
                    alumnos[alumno].append(combinacion)

                    
                    actual.pop()
                    asignatura["capacidadActual"] -= 1

    ###

    # Obtener el numero de alumnos cuyas combinaciones en total ya no son factibles y por tanto no pueden ser asignados
    def getPuntuacion(self, alumnos):
        restantes = 0

        for alumno in alumnos.keys():
            for combinacion in alumnos[alumno]:
                for clave, datos in combinacion.items():
                    if datos["asignatura"] == clave[0] and datos["grupo"] == clave[1]:
                        restantes += 1
        
        return restantes

    ###

    def factible(self, nuevo, combinacion, asignaturaClase):
        if nuevo in asignaturaClase or asignaturaClase["capacidadActual"] >= asignaturaClase["capacidadTotal"]:
            return False
        
        else:
            for asignatura in combinacion:
                clave = (asignatura["asignatura"], asignatura["grupo"])
                combinacion.remove(asignatura)

                if self.factible(nuevo, combinacion, self.datos[clave]):
                    return True

    ###

    def asignarAlumno(self, alumno, asignatura):
        pass

    ###

    # Aisla a los alumnos matriculados en una asignatura
    def __filtrarAlumnos(self, alumnos, claveAsignatura):
        resultado = {}
        alumnoCombinacion = {}

        for alumno, datos in alumnos.items():
            alumnoCombinacion[alumno] = []

            for combinacion in datos:
                for asignatura in combinacion:

                    if asignatura["asignatura"] == claveAsignatura[0] \
                    and asignatura["grupo"] == claveAsignatura[1]:
                        alumnoCombinacion[alumno].append(combinacion)

            if len(alumnoCombinacion[alumno]) > 0:
                resultado[alumno] = alumnoCombinacion[alumno]

        return resultado       
                            
    ####################