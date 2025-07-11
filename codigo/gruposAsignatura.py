import re
import copy
import statistics
import pandas as pd

###############

ADE = [
    ['2161116', '2161114', '2161115', '2161113'],
    ['216111B', '216111C', '216111D'],
    ['2161127', '2161125', '2161126'],
    ['216112B', '216112C', '216112D'],
    ['2161136', '2971133', '297113B'],
    ['216113D', '2971132', '2971139', '297113A'],
    ['2971145', '2971143', '2161146']
]

MATES = [
    ['2971114', '2971112', '297111C'],
    ['297111A', '2971113'],
    ['2971124', '2971123', '2971125'],
    ['2971116', '297112C', '2971129', '2971129'],
    ['2971135', '2971133', '297113B', '2971131'],
    ['2971132', '2971139', '297113A'],
    ['2971145', '2971143']
]

INFO = [
    ['2961112', '2961111', '2961114', '2961115', '2961113'],
    ['2961116', '296111A', '2961118', '2961117'], # SIN IES
    ['2961122', '2691125', '2961124', '2961123', '2961121'],
    ['2961126', '2961127', '2961129', '296112A', '2961128'],
    ['2961131', '2961134', '2961133', '2961135', '2961132'],
    ['296113L', '296113P', '296113M', '296113N', '296113K'],
    ['296113H', '296114E', '296113I', '296113F', '296113J'],
    ['296113C', '296113B', '296113D', '296113E', '296113A'],
    ['296113S', '296113R', '296113T', '296113Q', '296113U'],
    ['296113X', '296113Z', '296113Y', '296113V', '296113W'],
    ['29611CB', '29611CD', '296114I', '296114G', '296114H'],
    ['29611CC', '29611CF'],
    ['29611BA', '29611BB', '296114D', '296113G', '296114F', '29611BF'],
    ['29611BD', '29611BE', '29611BC'],
    ['29611AA', '29611AD', '29611AE', '296114A', '296114B', '296114C'],
    ['29611AB', '29611AF', '29611AC'],
    ['29611DC', '29611DE', '29611DA', '296114J', '296114L', '296114K'],
    ['29611DB', '29611DD'],
    ['29611FA', '29611FC', '296114M', '296114P', '296114N'],
    ['29611FB', '29611FE', '29611FD']
]

TELECO = [
    ['2211112', '2211111', '2211113', '2211114', '2211115'],
    ['2211116', '2211117', '2211119', '221111A', '2211118'],
    ['2211122', '2211124', '2211123', '2211121'],
    ['2211126', '221112A', '2211127', '2211128', '2211129'],
    ['2211134', '2211133', '2211132', '2211135', '2211131'],
    ['2211138', '2211136', '2211137', '2211139', '221113A'],
    ['221113B', '221113F', '221113D', '221113C', '221113E'],
    ['221113J', '221113K', '221113H', '221113I', '221113G'],
    ['2211143', '2211142', '2211141'],
    ['2211144', '2211145', '2211146'],
    ['2211147', '2211149', '2211148'],
    ['22111A3', '22111BB', '22111CB', '22111AB', '22111A2']
]

CURSOSCOMPLETOS = []
CURSOSCOMPLETOS.extend(TELECO)
CURSOSCOMPLETOS.extend(INFO)
CURSOSCOMPLETOS.extend(MATES)
CURSOSCOMPLETOS.extend(ADE)

###############

class gruposAsignatura:
    def __init__(self, fileHor, combinaciones, matricula):
        self.combinaciones = combinaciones
        self.matricula = matricula

        # Procesar archivo 
        df = pd.read_csv(fileHor)

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
                "capacidadTotal" : 26,
                "capacidadActual" : 0,
                "alumnos": [],
                "horario": codigoHoras,
                "subgrupos": None
            }

            """ if aulas[i] == "2.1" or aulas[i] == "3.1":
                self.datos[clave]["capacidadTotal"] = 30 """
        
        ###
        # Ajustar capacidades a subgrupos y rellenar alumnos
        self.corregirSubgrupos(codigos, grupos)
        self.corregirIES()

        # En primero de teleco hay una hora que se alterna entre AM y AL y tienen que coincidir si o si -> hacer bloques de asignaturas

        # Los grupos de los dobles grados son asignaturas comunes, aunque sean diferentes carreras

        # En los dobles grados hay unas asignaturas que se alternan una semana si y otra no (3INFOADE y 3INFOMATES),
        # en el subgrupo de FIS A1 solo pueden ir estudiantes de ADE

        # Priorizar las combinaciones que tienen las cinco asignaturas en el mismo subgrupo

        # Evitar combinaciones donde las horas esten muy separadas temporalmente

        # Hacer una lista ordenada de restricciones más o menos estrictas, si no dan buen resultado ir quitandolas.

    ####################

    # Ajusta la capacidad de los grupos a la unión de la de los subgrupos
    def corregirSubgrupos(self, codigos, grupos):
        for clave in self.datos.keys():
            if len(clave[1]) == 1:
                subgrupos = []
                patron = f"{clave[1]}."

                for i in range(len(codigos)):
                    if codigos[i] == self.datos[clave]["codigo"] and re.fullmatch(patron, grupos[i]):
                        subgrupos.append(grupos[i])

                self.datos[clave]["subgrupos"] = subgrupos
                self.datos[clave]["capacidadTotal"] *= len(self.datos[clave]["subgrupos"]) 

    ###

    # Eliminar subgrupos y corregir horas de IES
    def corregirIES(self):
        horas = {}
        claves = []

        # Inicializar horas
        for clave in self.datos.keys():
            if clave[0] == 'IES':
                horas[clave[1][0]] = []

        # Recopilar horarios de IES
        for clave, valor in self.datos.items():
            if clave[0] == 'IES':
                horas[clave[1][0]].extend(valor["horario"])

        # Asignar horas al grupo de teoría
        for clave, valor in horas.items():
            self.datos[('IES', clave)]["horario"] = set(valor)
            self.datos[('IES', clave)]["subgrupos"] = None

        # Eliminar subgrupos de IES
        for clave, valor in self.datos.items():
            if clave[0] == 'IES' and len(clave[1]) > 1:
                claves.append(clave)

        for clave in claves:
            del self.datos[clave]

        # Matricular alumnos en Teoría
        for alumno, asignaturas in self.matricula.items():
            if len(asignaturas) > 0:
                for asignatura in asignaturas:
                    if asignatura["asignatura"] == 'IES':
                        clave = (asignatura["asignatura"], asignatura["grupo"])
                        self.datos[clave]["alumnos"].append(alumno)
                        self.datos[clave]["capacidadActual"] += 1

    ####################

    def getAulasRellenas(self, alumnos):

        # Rellenar grupos de teoría
        combMatriculados = self.__filtrarAlumnos(alumnos)
        self.rellenarGruposTeoria(combMatriculados)

        # Rellenar grupos de prácticas
        combMatriculados = self.__filtrarSubgrupos(alumnos)
        return self.explorarGruposPracticas(combMatriculados)
        
    ###

    def getResults(self):
        soluciones = self.getAulasRellenas(self.combinaciones)

        for asignatura, datos in soluciones[0].items():
            print(f"Asignatura: {asignatura}:\n {datos}\n\n")

        print('\n\n\n\n\n')

        contador = 0
        anterior = ("", "W")

        for asignatura, datos in soluciones[0].items():
            if datos["capacidadActual"] <= datos["capacidadTotal"]:
                resta = datos["capacidadTotal"] - datos["capacidadActual"]

                if asignatura[1][0] != anterior[1][0]:
                    print('\n')

                print(f"Sobrante {contador}: {asignatura} - {resta} alumnos")

                anterior = asignatura
                contador += 1

        print('\n\n\n\n\n')

        contador = 0
        anterior = ("", "W")

        for asignatura, datos in soluciones[0].items():
            if datos["capacidadActual"] > datos["capacidadTotal"]:
                resta = datos["capacidadActual"] - datos["capacidadTotal"]
                print(f"Exceso {contador}: {asignatura} - {resta} alumnos")

                if asignatura[1][0] != anterior[1][0]:
                    print('\n')

                anterior = asignatura
                contador += 1

    # Añadir alumno a todos sus grupos de teoría
    def rellenarGruposTeoria(self, combinaciones):
        for alumno, claves in combinaciones.items():
            if len(claves) > 0:
                for clave in claves:
                    if alumno not in self.datos[clave]["alumnos"]:
                        self.datos[clave]["alumnos"].append(alumno)
                        self.datos[clave]["capacidadActual"] += 1
    ###

    def explorarGruposPracticas(self, alumnos):
        soluciones = []
        alumnos_lista = [] 
        asignados = 0

        for alumno, combinaciones in alumnos.items():
            if len(combinaciones) == 1:
                self.rellenarSubgrupos(self.datos, alumno, combinaciones[0])
                asignados += 1

            elif len(combinaciones) > 1:
                alumnos_lista.append((alumno, combinaciones))

        # Ordenar alumnos, antes los que tienen todas las asignaturas de un curso
        #alumnos_lista.sort()
        alumnos_lista = self.sort(alumnos_lista)
        # Ordenar alumnos por el número de combinaciones (menos a más)
        #alumnos_lista.sort(key = lambda x: len(x[1]), reverse=False)

        self.explorarCombinacionesSubgrupos(alumnos_lista, copy.deepcopy(self.datos), soluciones, 0, len(alumnos) - asignados)

        return soluciones
    
    ###

    def completo(self, lista):
        completo = {}

        for datos in lista:
            completo[datos[0]] = False
            codigos = []
            grupos = []

            for asignatura in datos[1][0]:
                codigos.append(asignatura["codigo"])
                grupos.append(asignatura["grupo"][0])

            repetidos = set(grupos)
            if len(repetidos) > 1:
                continue

            for curso in CURSOSCOMPLETOS:
                if sorted(codigos) == sorted(curso):
                    completo[datos[0]] = True
                    break

        return completo

    ###

    def sort(self, lista):
        cursosCompletos = self.completo(lista)
        return sorted(lista, key=lambda x: (not cursosCompletos.get(x[0], False), len(x[1])), reverse=False)

    ###
    
    def explorarCombinacionesSubgrupos(self, alumnos, actual, soluciones, indice, stop):
        if indice == stop:
            soluciones.append(copy.deepcopy(actual))
            return True
        
        alumno, combinaciones = alumnos[indice]
        desviaciones = {}

        for i, combinacion in enumerate(combinaciones):
            desviaciones[i] = self.desviaciones(alumno, copy.deepcopy(actual), combinacion)

        # Seleccionar el grupo con mejor equilibrio
        mejor = [None, 1000] # indice, valor desviación
        for i, desv in desviaciones.items():
            desvTotal = sum(list(desv.values()))

            if desvTotal < mejor[1]:
                mejor[0] = i
                mejor[1] = desvTotal
                
        for i in range(len(combinaciones)):
            if i == mejor[0]:
                self.rellenarSubgrupos(actual, alumno, combinaciones[i])
                break

        # Seguir explorando
        if self.explorarCombinacionesSubgrupos(alumnos, copy.deepcopy(actual), soluciones, indice + 1, stop):
            return True
        
        return False

    ###

    def desviaciones(self, alumno, configuracion, combinacion):
        self.rellenarSubgrupos(configuracion, alumno, combinacion)

        desviaciones = {}
        capacidades = {}

        asignaturasModificadas = [combinacion[i]["asignatura"] for i in range(len(combinacion))]
        gruposModificados = [combinacion[i]["grupo"] for i in range(len(combinacion))]

        for i in range(len(asignaturasModificadas)):

            patron = f"{gruposModificados[i][:-1]}."
            clavesSubgrupos = []

            # Buscar subgrupos de la asignatura modificada
            for clave in configuracion:
                if clave[0] == asignaturasModificadas[i] and re.fullmatch(patron, clave[1]):
                    clavesSubgrupos.append(clave)

            # Inicializar
            for clave in clavesSubgrupos:
                capacidades[clave[0]] = []
                desviaciones[clave[0]] = 0

            # Añadir capacidad actual de cada subgrupo
            for clave in clavesSubgrupos:
                capacidades[clave[0]].append(configuracion[clave]["capacidadActual"])

        # Calcular desviaciones estándar de los subgrupos de cada asignatura
        for clave in capacidades:
            if len(capacidades[clave]) > 1:
                desviaciones[clave] = statistics.stdev(capacidades[clave])

        return desviaciones

    ###

    def rellenarSubgrupos(self, configuracion, alumno, combinacion):
        for asignatura in combinacion:
            clave = (asignatura["asignatura"], asignatura["grupo"])

            if alumno not in configuracion[clave]["alumnos"]:
                configuracion[clave]["alumnos"].append(alumno)
                configuracion[clave]["capacidadActual"] += 1

    ####################

    def __addIES(self, matricula, resultado):
        for clave in matricula:
            if clave[0] == 'IES':
                resultado.append(("IES", clave["grupo"]))
                break

    # Aisla a los alumnos matriculados en una asignatura de teoría
    def __filtrarAlumnos(self, alumnos):
        resultado = {}
        for alumno, combinaciones in alumnos.items():
            resultado[alumno] = []

            if len(combinaciones) > 0:
                for asignatura in combinaciones[0]:
                    clave = (asignatura["asignatura"], asignatura["grupo"][0])
                    resultado[alumno].append(clave)

            self.__addIES(resultado[alumno], self.matricula[alumno])

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