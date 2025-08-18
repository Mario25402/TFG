import re
import copy
import statistics
import pandas as pd

###############################################################################

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

###############################################################################

class gruposAsignatura:

    ###################################
    # Constructor
    # Órden 0, llamada desde Main
    # Inicializa todo lo necesario

    def __init__(self, fileHor, combinaciones, matricula, sinAsignar):
        self.combinaciones = combinaciones
        self.matricula = matricula
        self.sinAsignar = sinAsignar

        # Procesar archivo 
        df = pd.read_csv(fileHor)

        codigos = df["CODIGO"].tolist()
        nombres = df["ASIGNATURA"].tolist()
        grupos = df["GRUPO"].tolist()
        horas = [df[f"HORA{i}"].tolist() for i in range(1, 6)]

        ###
        # Rellenar "datos"
        
        self.datos = {}

        for i in range(len(codigos)):
            clave = (nombres[i], grupos[i])
            codigoHoras = [int(x) for lista in horas for x in [lista[i]] if pd.notna(x)]

            self.datos[clave] = {
                "codigo" : codigos[i],
                "capacidadTotal" : 26,
                "capacidadActual" : 0,
                "alumnos": [],
                "horario": codigoHoras,
                "subgrupos": None
            }
        
        ###
        # Ajustar capacidades a subgrupos y rellenar alumnos
        self.corregirSubgrupos(codigos, grupos)
        self.corregirIES()

    ###################################
    # Corregir Subgrupos
    # Órden 1, llamada desde órden 0
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

    ###################################
    # Corregir IES
    # Órden 2, llamada desde órden 0
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

    ###################################
    # Get Results Asignaturas
    # Órden 3, llamada desde Main
    # Rellena las asignaturas tanto de teoría como de prácticas

    def getResultsAsignaturas(self):
        solucionesEnteras = self.getAulasRellenas(self.combinaciones)
        solucionesSolapadas = self.setSolapados()

        self.solAsignaturas = {}
        self.solAsignaturas.update(solucionesEnteras[0])
        self.solAsignaturas.update(solucionesSolapadas[0])

        with open("./res/asignaturasAsignadas.txt", "w") as f:
            for asignatura, datos in self.solAsignaturas.items():
                f.write(f"Asignatura: {asignatura}:\n {datos}\n\n")

            f.write('\n\n\n\n\n')

            sumaEx = 0
            sumaSob = 0
            contador = 0

            for asignatura, datos in self.solAsignaturas.items():
                if datos["capacidadActual"] <= datos["capacidadTotal"]:
                    resta = datos["capacidadTotal"] - datos["capacidadActual"]

                    f.write(f"Sobrante {contador}: {asignatura} - {resta} alumnos\n")

                    contador += 1
                    sumaSob += resta

            f.write('\n\n\n\n\n')

            contador = 0

            for asignatura, datos in self.solAsignaturas.items():
                if datos["capacidadActual"] > datos["capacidadTotal"]:
                    resta = datos["capacidadActual"] - datos["capacidadTotal"]
                    f.write(f"Exceso {contador}: {asignatura} - {resta} alumnos\n")

                    contador += 1
                    sumaEx += resta

            f.write('\n\n\n\n\n')
            f.write(f"Suma sobrantes: {sumaSob}\n")
            f.write(f"Suma excesos: {sumaEx}\n")

            asignados = []
            matriculados = []
            
            for alumno in self.matricula.keys():
                if len(self.matricula[alumno]) > 0:
                    matriculados.append(alumno)

                nextAlumno = False
                for asignatura, datos in self.solAsignaturas.items():
                    if alumno in datos["alumnos"]:
                        asignados.append(alumno)
                        nextAlumno = True
                        break

                if nextAlumno:
                    continue

            f.write(f"Alumnos matriculados: {len(matriculados)}, Alumnos asignados: {len(asignados)}\n")
            f.write('\n\n')

    ###################################
    # Get Aulas Rellenas
    # Órden 4, llamada desde órden 3
    # Rellena los grupos de teoría y prácticas

    def getAulasRellenas(self, alumnos):

        # Rellenar grupos de teoría
        combMatriculados = self.__filtrarGruposTeoria(alumnos)
        self.rellenarGruposTeoria(combMatriculados)

        # Rellenar grupos de prácticas
        combMatriculados = self.__filtrarSubgrupos(alumnos)
        return self.explorarGruposPracticas(combMatriculados)
    
    ###################################
    # Filtrar Grupos Teoría
    # Órden 5, llamada desde órden 4
    # Aisla a los alumnos matriculados en una asignatura de teoría
    
    def __filtrarGruposTeoria(self, alumnos):
        resultado = {}
        for alumno, combinaciones in alumnos.items():
            resultado[alumno] = []

            if len(combinaciones) > 0:
                for asignatura in combinaciones[0]:
                    clave = (asignatura["asignatura"], asignatura["grupo"][0])
                    resultado[alumno].append(clave)

            self.__addIES(resultado[alumno], self.matricula[alumno])

        return resultado
    
    ###################################
    # Filtrar Grupos Teoría
    # Órden 6, llamada desde órden 5
    # Añade los grupos eliminados de IES

    def __addIES(self, matricula, resultado):
        for clave in matricula:
            if clave[0] == 'IES':
                resultado.append(("IES", clave["grupo"]))
                break

    ###################################
    # Rellenar Grupos Teoría
    # Órden 7, llamada desde órden 4
    # Añadir alumnos a todos sus grupos de teoría

    def rellenarGruposTeoria(self, combinaciones):
        for alumno, claves in combinaciones.items():
            if len(claves) > 0:
                for clave in claves:
                    if alumno not in self.datos[clave]["alumnos"]:
                        self.datos[clave]["alumnos"].append(alumno)
                        self.datos[clave]["capacidadActual"] += 1

    ###################################
    # Filtrar Subgrupos
    # Órden 8, llamada desde órden 4
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

    ###################################
    # Explorar Grupos Prácticas
    # Órden 9, llamada desde órden 4
    # Explora las combinaciones de subgrupos para asignar a los alumnos

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
        # Ordenar alumnos por el número de combinaciones (menos a más)
        alumnos_lista = self.sort(alumnos_lista)

        self.explorarCombinacionesSubgrupos(alumnos_lista, copy.deepcopy(self.datos), soluciones, 0, len(alumnos) - asignados)

        return soluciones
    
    ###################################
    # Rellenar Subgrupos
    # Órden 10, llamada desde órden 9
    # Añade un alumno a un subgrupo

    def rellenarSubgrupos(self, configuracion, alumno, combinacion):
        for asignatura in combinacion:
            clave = (asignatura["asignatura"], asignatura["grupo"])

            if alumno not in configuracion[clave]["alumnos"]:
                configuracion[clave]["alumnos"].append(alumno)
                configuracion[clave]["capacidadActual"] += 1

    ###################################
    # Sort
    # Órden 11, llamada desde órden 9
    # Ordena los grupos completos primero, luego por mas a menos combinaciones

    def sort(self, lista):
        cursosCompletos = self.cursoCompleto(lista)
        return sorted(lista, key=lambda x: (not cursosCompletos.get(x[0], False), len(x[1])), reverse=False)

    ###################################
    # Curso Completo
    # Órden 12, llamada desde órden 11
    # Comprueba las asignaturas de cada grado por curso

    def cursoCompleto(self, lista):
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

    ###################################
    # Explorar Combinaciones Subgrupos
    # Órden 13, llamada desde órden 9
    # Explora las combinaciones de subgrupos para el cómputo global
    
    def explorarCombinacionesSubgrupos(self, alumnos, actual, soluciones, indice, stop):
        if indice == stop:
            soluciones.append(copy.deepcopy(actual))
            return True
        
        diasBool = {}
        desviaciones = {}
        combEliminadas = []

        alumno, combinaciones = alumnos[indice]

        for i, combinacion in enumerate(combinaciones):
            diasBool[i] = {}
            desviaciones[i] = self.desviaciones(alumno, actual, combinacion)

        # Seleccionar el grupo con mejor equilibrio global de personas por aula
        mejor = [None, 1000] # indice, valor desviación
        for i, desv in desviaciones.items():
            desvTotal = sum(list(desv.values()))

            if desvTotal < mejor[1]:
                mejor[0] = i
                mejor[1] = desvTotal
                
        for i in range(len(combinaciones)):
            horas = set()
            asignaturas = combinaciones[i]
            
            for asignatura in asignaturas:
                horas.update(asignatura["horario"])

            # Eliminar combinaciones con horas muy separadas
            if self.separacionAltaHoras(horas, asignaturas, diasBool[i]):
                combEliminadas.append(combinaciones[i])
                break

            if i == mejor[0]:
                self.rellenarSubgrupos(actual, alumno, combinaciones[i])
                break

        # Si ninguna combinación es válida, añadir la combinación con mejor equilibrio
        if len(combEliminadas) == len(combinaciones):
            self.rellenarSubgrupos(actual, alumno, mejor[0])

        # Seguir explorando
        if self.explorarCombinacionesSubgrupos(alumnos, copy.deepcopy(actual), soluciones, indice + 1, stop):
            return True
        
        return False
    
    ###################################
    # Desviaciones
    # Órden 14, llamada desde órden 13
    # Calcula las desviaciones de los subgrupos de cada asignatura

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
    
   ###################################
    # Rellenar Subgrupos
    # Órden 15, llamada desde órden 14
    # Añade un alumno a un subgrupo

    ###################################
    # Separación Alta Horas
    # Órden 16, llamada desde órden 13
    # Comprueba si las horas de un alumno están muy separadas

    def separacionAltaHoras(self, horas, asignaturas, resultado):

        # Añadir horas de teoría
        for asignatura in asignaturas:
            clave = (asignatura["asignatura"], asignatura["grupo"][0])
            if clave in self.datos:
                horas.update(self.datos[clave]["horario"])

        ###

        separacion = {}
        resultados = {}

        for hora in horas:
            dia = str(hora)[0]
            separacion.setdefault(dia, set())
            separacion[dia].add(hora)

        for clave in separacion.keys():
            separacion[clave] = sorted(list(separacion[clave]))

        for dia, horas in separacion.items():
            resultados[dia] = False

            for i in range(len(horas) - 1):
                if horas[i + 1] - horas[i] > 2:
                    resultados[dia] = True
                    break

        # Comprobar que todos los días tienen el mismo resultado
        todoFalse = set(resultados.values()) == {False}

        if todoFalse:
            return False
        
        resultado = resultados
        return True
    
    ###################################
    # Rellenar Subgrupos
    # Órden 17, llamada desde órden 13
    # Añade un alumno a un subgrupo

    ###################################
    # Rellenar Subgrupos
    # Órden 18, llamada desde órden 13
    # Añade un alumno a un subgrupo
                            
    ###################################
    # Set Solapados
    # Órden 19, llamada desde órden 3
    # Rellena los alumnos con horas solapadas

    def setSolapados(self):
        teoria = {}
        horasTeoria = {}

        # Añadir alumnos a los grupos de teoría
        for alumno, posibilidades in self.sinAsignar.items():
            teoria[alumno] = []
            horasTeoria[alumno] = []

            for posibilidad in posibilidades:
                for asignatura in posibilidad:
                    clave = (asignatura['asignatura'], asignatura['grupo'][0])
                    teoria[alumno].append(clave)
                    horasTeoria[alumno].extend(self.datos[clave]["horario"])

        self.rellenarGruposTeoria(teoria)

        ###
        
        prFiltradas = self.filtrarSolapadas(self.sinAsignar, horasTeoria)
        practicas = self.explorarGruposPracticas(prFiltradas)

        return practicas
    
    ###################################
    # Get Aulas Rellenas
    # Órden 20, llamada desde órden 19
    # Rellena los grupos de teoría y prácticas

    ###################################
    # Filtrar Solapadas
    # Órden 21, llamada desde órden 19
    # Reduce el número de combinaciones solapadas

    def filtrarSolapadas(self, datos, horasTeoria):
        seleccionadas = {}
        copia = copy.deepcopy(datos)

        for alumno, combinaciones in datos.items():
            if len(combinaciones) > 0:
                horas = {}
                colisiones = {}
                seleccionadas[alumno] = []

                # Recopilar horas de cada combinacion y calcular cuantas se solapan
                for i, combinacion in enumerate(combinaciones):
                    horas[i] = horasTeoria[alumno]
                    
                    for asignatura in combinacion:
                        horas[i].extend(asignatura["horario"])

                    colisiones[i] = len(horas[i]) - len(set(horas[i]))

                # Calcular la media y seleccionar las que están por debajo
                mediaColisiones = statistics.mean(list(colisiones.values()))
                for i in range(len(colisiones)):
                    if colisiones[i] <= mediaColisiones:
                        seleccionadas[alumno].append(combinaciones[i])
                
                copia[alumno] = seleccionadas[alumno]

        combinacionesSelec = 0
        combinacionesOriginales = 0

        for alumno, combinaciones in seleccionadas.items():
            for combinacion in combinaciones:
                combinacionesSelec += 1

        for alumno, combinaciones in self.sinAsignar.items():
            for combinacion in combinaciones:
                combinacionesOriginales += 1

        print(f"Combinaciones seleccionadas: {combinacionesSelec} de {combinacionesOriginales}")

        return seleccionadas
    
     ###################################
    # Explorar Grupos Prácticas
    # Órden 22, llamada desde órden 19
    # Explora las combinaciones de subgrupos para asignar a los alumnos

    ###################################
    # Get Results Alumno
    # Órden 23, llamada desde Main
    # Rellena los resultados por alumno

    def getResultsAlumno(self):
        self.solAlumno = {}

        # Rellenar claves
        for alumno in self.matricula.keys():
            self.solAlumno[alumno] = set()

        # Rellenar asignaturas por alumno
        for asignatura, datos in self.solAsignaturas.items():
            for alumno in datos["alumnos"]:
                if asignatura not in self.solAlumno[alumno]:
                    self.solAlumno[alumno].add(asignatura)

        # Rellenar documento 
        with open("./res/alumnosAsignados.txt", "w") as f:
            vacios = 0

            for alumno, asignaturas in self.solAlumno.items():
                f.write(f"\n{alumno}:\n")

                for asignatura in sorted(asignaturas):
                    if (len(asignatura) == 0):
                        vacios += 1

                    abrv, grupo = asignatura
                    f.write(f"{abrv} - {grupo}\n")

            f.write(f"\nAlumnos sin asignaturas: {vacios}\n")
