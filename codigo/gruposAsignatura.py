import re
import copy
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

        # Rellenar grupos de teoría
        combMatriculados = self.__filtrarAlumnos(alumnos)
        self.rellenarGruposTeoria(combMatriculados)

        # Rellenar grupos de prácticas
        combMatriculados = self.__filtrarSubgrupos(alumnos)
        soluciones = self.explorarGruposPracticas(combMatriculados)

        
        for solucion in soluciones:
            self.repartirFallidos(solucion[0], solucion[1], combMatriculados)

    ###

    def repartirFallidos(self, configuracion, alumnos, combinaciones):
        for alumno in alumnos:
            #self.rellenarSubgrupos(configuracion, alumno, combinaciones[alumno][0])
            print(alumno)

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

    def explorarGruposPracticas(self, alumnos):
        fallidos = []
        soluciones = []
        alumnos_lista = [] 
        asignados = 0

        for alumno, combinaciones in alumnos.items():
            if len(combinaciones) == 1:
                self.rellenarSubgrupos(self.datos, alumno, combinaciones[0])
                asignados += 1

            elif len(combinaciones) > 1:
                alumnos_lista.append((alumno, combinaciones))

        # Ordenar alumnos por el número de combinaciones (menos a más)
        alumnos_lista.sort(key = lambda x: len(x[1]), reverse=False)

        self.explorarCombinacionesSubgrupos(alumnos_lista, 0, copy.deepcopy(self.datos), soluciones, len(alumnos) - asignados, fallidos)

        return soluciones

    ###

    def explorarCombinacionesSubgrupos(self, alumnos, indice, actual, soluciones, stop, fallidos):
        if len(soluciones) >= 1:
            return True
        
        if indice == stop:
            if self.factible(actual):
                soluciones.append((copy.deepcopy(actual), fallidos))
                
                #print(f"Nueva solución\n\n\n\n\n")
                return self.explorarCombinacionesSubgrupos(alumnos, 0, copy.deepcopy(self.datos), soluciones, stop, [])
            return False
         

        alumno, combinaciones = alumnos[indice]
        continua = False

        if alumno == 51231069:
            pass

        for i, combinacion in enumerate(combinaciones):
            if not self.combinacionPermitida(actual, alumno, combinacion):
                continue

            siguiente = copy.deepcopy(actual)
            self.rellenarSubgrupos(siguiente, alumno, combinacion)

            if self.factible(siguiente):
                #print(f"Alumno: {str(alumno)} - Combinacion nº: {i} - Índice: {indice}")
                solucion = self.explorarCombinacionesSubgrupos(alumnos, indice + 1, siguiente, soluciones, stop, fallidos)

                if solucion:
                    return True
                
                continua = True
                

        if not continua:
            #print (f"Alumno: {str(alumno)} - Fallido")
            if alumno not in fallidos:
                fallidos.append(alumno)

            if indice + 1 < stop:
                return self.explorarCombinacionesSubgrupos(alumnos, indice + 1, actual, soluciones, stop, fallidos)
                
        return False

    ###

    def combinacionPermitida(self, configuracion, alumno, combinacion):
        for asignatura in combinacion:
            clave = (asignatura["asignatura"], asignatura["grupo"])

            if alumno in configuracion[clave]["alumnos"]:
                return False

            if configuracion[clave]["capacidadActual"] >= configuracion[clave]["capacidadTotal"]:
                return False
            
            return True

    ###

    def factible(self, configuracion):
        for clave, datos in configuracion.items():
            if (datos['subgrupos'] == None) and (datos["capacidadActual"] > datos["capacidadTotal"]):
                return False
            elif (datos['subgrupos'] == None) and (datos["capacidadActual"] <= datos["capacidadTotal"]):
                nuevaClave = (clave[0], clave[1][0])

                if self.datos[nuevaClave]["capacidadActual"] - 5 > self.datos[nuevaClave]["capacidadTotal"]:
                    return True
        return True

    ###

    def rellenarSubgrupos(self, configuracion, alumno, combinacion):
        for asignatura in combinacion:
            clave = (asignatura["asignatura"], asignatura["grupo"])

            if alumno not in configuracion[clave]["alumnos"]:
                configuracion[clave]["alumnos"].append(alumno)
                configuracion[clave]["capacidadActual"] += 1

    ###

    """ def rellenarAlumnos(self, asignatura, alumnos, actual, mejorRelleno, mejorPuntuacion):
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
        pass """

    ####################

    # Aisla a los alumnos matriculados en una asignatura
    def __filtrarAlumnos(self, alumnos):
        resultado = {}
        alumnoCombinacion = {}

        for alumno, datos in alumnos.items():
            alumnoCombinacion[alumno] = []

            for combinacion in datos:
                for asignatura in combinacion:

                    if len(asignatura["grupo"]) == 1:
                        alumnoCombinacion[alumno].append(combinacion)

            if len(alumnoCombinacion[alumno]) > 0:
                resultado[alumno] = alumnoCombinacion[alumno]

        return resultado   

    ###

    # Reduce las combinaciones de asignaturas solo a los subgrupos 
    def __filtrarSubgrupos(self, alumnos):
        resultado = {}
        alumnoCombinacion = {}

        for alumno, datos in alumnos.items():
            alumnoCombinacion[alumno] = []

            for combinacion in datos:
                comb = []

                for asignatura in combinacion:
                    if len(asignatura["grupo"]) > 1:
                        comb.append(asignatura)

                if len(comb) > 0:
                    alumnoCombinacion[alumno].append(comb)

            if len(alumnoCombinacion[alumno]) > 0:
                resultado[alumno] = alumnoCombinacion[alumno]

        return resultado
                            
    ####################