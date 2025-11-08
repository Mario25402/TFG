import re
import copy
import statistics
import pandas as pd
from pathlib import Path

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
    ['29611CD', '296114I', '296114G', '296114H'],
    ['296114D', '296113G', '296114F'],
    ['296114A', '296114B', '296114C'],
    ['296114J', '296114L', '296114K'],
    ['296114M', '296114P', '296114N'],
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
]

CURSOSCOMPLETOS = []
CURSOSCOMPLETOS.extend(TELECO)
CURSOSCOMPLETOS.extend(INFO)
CURSOSCOMPLETOS.extend(MATES)
CURSOSCOMPLETOS.extend(ADE)

DIR_PATH = Path(__file__).parent.resolve()

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
        self.cuatrimestre = str(fileHor)[-5]
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
                "ocupacion" : 0,
                "alumnos": [],
                "horario": codigoHoras
            }

        # Unificar Teoria y Subgrupos
        self.__corregirIES()

    ###################################
    # Corregir IES
    # Órden 2, llamada desde órden 0
    # Eliminar subgrupos y corregir horas de teoría

    def __corregirIES(self):
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
                        self.datos[clave]["ocupacion"] += 1

    ###################################
    # Asignar Asignaturas
    # Órden 3, llamada desde Main
    # Rellena las asignaturas tanto de teoría como de prácticas

    def asignarAsignaturas(self):
        solucionesEnteras = self.rellenarAulas(self.combinaciones)
        solucionesSolapadas = self.asignarSolapados()

        self.solAsignaturas = self.fusionarSoluciones(solucionesEnteras[0], solucionesSolapadas[0])
        self.solAsignaturasFinal = self.repaso(self.solAsignaturas)

        ###
        # Rellenar documento

        ruta = DIR_PATH / ".." / "output" / "raw" / f"asignaturasAsignadas{self.cuatrimestre}.txt"
        with open(str(ruta), "w") as f:
            for asignatura, datos in self.solAsignaturasFinal.items():
                f.write(f"Asignatura: {asignatura}:\n {datos}\n\n")

    ###################################
    # Rellenar Aulas
    # Órden 4, llamada desde órden 3
    # Rellena los grupos de teoría y prácticas

    def rellenarAulas(self, alumnos):
        self.asignaciones = {} # Guarda la combinación elegida por alumno

        # Rellenar grupos de teoría
        combMatriculados = self.__filtrarGruposTeoria(alumnos)
        self.rellenarGruposTeoria(combMatriculados)

        # Rellenar grupos de prácticas
        combMatriculados = self.__filtrarSubgrupos(alumnos)
        return self.rellenarGruposPracticas(combMatriculados)
    
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
    # Añade los grupos de teoría de IES que no estan en 'alumnos'

    def __addIES(self, matricula, resultado):
        for clave in matricula:
            if clave[0] == 'IES':
                resultado.append(("IES", clave[1]))
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
                        self.datos[clave]["ocupacion"] += 1

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
    # Rellenar Grupos Prácticas
    # Órden 9, llamada desde órden 4
    # Explora las combinaciones de subgrupos para asignar a los alumnos

    def rellenarGruposPracticas(self, alumnos):
        soluciones = []
        alumnos_lista = [] 
        asignados = 0

        for alumno, combinaciones in alumnos.items():
            if len(combinaciones) == 1:
                self.aniadirAlumnoCombinacion(self.datos, alumno, combinaciones[0])
                asignados += 1

            elif len(combinaciones) > 1:
                alumnos_lista.append((alumno, combinaciones))

        # Ordenar alumnos, antes los que tienen todas las asignaturas de un curso
        # Ordenar alumnos por el número de combinaciones (menos a más)
        alumnos_lista = self.__sort(alumnos_lista)

        self.explorarCombinacionesSubgrupos(alumnos_lista, copy.deepcopy(self.datos), soluciones, 0, len(alumnos) - asignados)

        return soluciones
    
    ###################################
    # Añadir Alumno a Combinación
    # Órden 10, llamada desde órden 9
    # Añade un alumno a los subgrupos de la combinación

    def aniadirAlumnoCombinacion(self, configuracion, alumno, combinacion):
        for asignatura in combinacion:
            clave = (asignatura["asignatura"], asignatura["grupo"])

            if alumno not in configuracion[clave]["alumnos"]:
                configuracion[clave]["alumnos"].append(alumno)
                configuracion[clave]["ocupacion"] += 1

    ###################################
    # Sort
    # Órden 11, llamada desde órden 9
    # Ordena los grupos completos primero, luego por mas a menos combinaciones

    def __sort(self, lista):
        cursosCompletos = self.isCursoCompleto(lista)
    
        ###
        
        completos = []
        resto = []

        for alumno, resultado in cursosCompletos.items():
            if resultado:
                completos.append(alumno)
            else:
                resto.append(alumno)

        ###

        resCompletos = []
        resResto = []
        
        for alumno, combinaciones in lista:
            if alumno in completos:
                resCompletos.append((alumno, combinaciones))
            else:
                resResto.append((alumno, combinaciones))

        ###

        resCompletos = sorted(resCompletos, key=lambda x: len(x[1]), reverse=False)
        resResto = sorted(resResto, key=lambda x: len(x[1]), reverse=False)
    
        return resCompletos + resResto

    ###################################
    # Curso Completo
    # Órden 12, llamada desde órden 11
    # Comprueba las asignaturas de cada grado por curso

    def isCursoCompleto(self, lista):
        completo = {}

        for datos in lista:
            completo[datos[0]] = False
            codigos = []
            grupos = []

            # Reunir asignaturas del alumno
            for asignatura in datos[1][0]:
                codigos.append(asignatura["codigo"])
                grupos.append(asignatura["grupo"][0])

            # Comprobar que solo hay un grupo
            repetidos = set(grupos)
            if len(repetidos) > 1:
                continue

            # Comprobar que las asignaturas pertenecen a un mismo curso
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

        if alumno == 37947823:
            pass

        for i, combinacion in enumerate(combinaciones):
            diasBool[i] = {}
            desviaciones[i] = self.calcDesviaciones(alumno, copy.deepcopy(actual), combinacion)

        # Calcular desviaciones de cada asignatura por grupo perteneciente
        mejor = [None, 1000] # indice, valor desviación
        desviaciones = dict(sorted(desviaciones.items(), key=lambda item: sum(item[1].values()) / len(item[1])))

        for i, desv in desviaciones.items():
            desvTotal = sum(list(desv.values()))

            if desvTotal < mejor[1]:
                mejor[0] = i
                mejor[1] = desvTotal

            mejorCopia = mejor
                
        # Seleccionar o descartar las combinaciones y elegir la resultante de menor desviación
        for i in range(len(combinaciones)):
            horas = set()
            asignaturas = combinaciones[i]
            
            for asignatura in asignaturas:
                horas.update(asignatura["horario"])

            # Eliminar combinaciones con horas muy separadas
            if self.isSeparacionHoras(horas, asignaturas, diasBool[i]):
                combEliminadas.append((i, combinaciones[i]))
                continue

        # Si ninguna es válida, volver a añadir la primera mejor
        asignada = False
        if len(combEliminadas) == len(combinaciones):
            self.aniadirAlumnoCombinacion(actual, alumno, combinaciones[mejor[0]])
            asignada = True

        else:
            for index, eliminada in combEliminadas:
                if eliminada == combinaciones[mejor[0]]:
                    if len(desviaciones) > 0:
                        desviaciones.pop(index)

        # Añadir la combinación con mejor equilibrio
        if not asignada:
            if len(desviaciones) == 0:
                mejor = mejorCopia

            self.aniadirAlumnoCombinacion(actual, alumno, combinaciones[mejor[0]])

        self.asignaciones[alumno] = mejor[0]

        # Seguir explorando
        if self.explorarCombinacionesSubgrupos(alumnos, copy.deepcopy(actual), soluciones, indice + 1, stop):
            return True
        
        return False
    
    ###################################
    # Calcular Desviaciones
    # Órden 14, llamada desde órden 13
    # Calcula las desviaciones de los subgrupos de cada asignatura

    def calcDesviaciones(self, alumno, configuracion, combinacion):
        self.aniadirAlumnoCombinacion(configuracion, alumno, combinacion)

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
                capacidades[clave[0]].append(configuracion[clave]["ocupacion"])

        # Calcular desviaciones estándar de los subgrupos de cada asignatura
        for clave in capacidades.keys():
            if len(capacidades[clave]) > 1:
                desviaciones[clave] = statistics.stdev(capacidades[clave])
            else:
                desviaciones[clave] = 0

        return desviaciones
    
   ###################################
    # Añadir Alumno a Subgrupo
    # Órden 15, llamada desde órden 14
    # Añade un alumno a un subgrupo

    ###################################
    # Separación Limite Horas
    # Órden 16, llamada desde órden 13
    # Comprueba si las horas de un alumno están muy separadas

    def isSeparacionHoras(self, horas, asignaturas, resultado):

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
                diff = self.__calcDiferenciaHoras(horas[i+1], horas[i])

                if diff > 1:
                    resultados[dia] = True
                    break

        # Comprobar que todos los días tienen el mismo resultado
        todoFalse = set(resultados.values()) == {False}

        # Eliminar hora de comer

        if todoFalse:
            return False
        
        resultado = resultados
        return True
    
    ###################################
    # Calcular Diferencia Horas
    # Órden 17, llamada desde órden 16
    # Calcula la diferencia de horas sin contar la hora de comer

    def __calcDiferenciaHoras(self, horaMayor, horaMenor):
        resta = horaMayor - horaMenor
        horaComer = int(f"{str(horaMenor)[0]}07")

        if horaMenor < horaComer <= horaMayor:
            resta -= 1

        return resta

    ###################################
    # Añadir Alumno a Subgrupo
    # Órden 18, llamada desde órden 13
    # Añade un alumno a un subgrupo

    ###################################
    # Añadir Alumno a Subgrupo
    # Órden 19, llamada desde órden 13
    # Añade un alumno a un subgrupo
                            
    ###################################
    # Asignar Solapados
    # Órden 20, llamada desde órden 3
    # Rellena los alumnos con horas solapadas

    def asignarSolapados(self):
        teoria = {}
        horasTeoria = {}

        # Añadir alumnos a los grupos de teoría
        for alumno, posibilidades in self.sinAsignar.items():
            teoria[alumno] = set()
            horasTeoria[alumno] = set()

            for posibilidad in posibilidades:
                for asignatura in posibilidad:
                    clave = (asignatura['asignatura'], asignatura['grupo'][0])
                    teoria[alumno].add(clave)
                    horasTeoria[alumno].update(self.datos[clave]["horario"])

        self.rellenarGruposTeoria(teoria)

        ###
        
        prFiltradas = self.__filtrarSolapados(self.sinAsignar, horasTeoria)
        practicas = self.rellenarGruposPracticas(prFiltradas)

        return practicas
    
    ###################################
    # Rellenar Grupos Teoria
    # Órden 21, llamada desde órden 20
    # Rellena los grupos de teoría de los alumnos

    ###################################
    # Filtrar Solapados
    # Órden 22, llamada desde órden 20
    # Reduce el número de combinaciones solapadas

    def __filtrarSolapados(self, datos, horasTeoria):
        seleccionadas = {}
        copia = copy.deepcopy(datos)

        for alumno, combinaciones in datos.items():
            if len(combinaciones) > 0:
                horas = {}
                colisiones = {}
                seleccionadas[alumno] = []

                # Recopilar horas de cada combinacion y calcular cuantas se solapan
                for i, combinacion in enumerate(combinaciones):
                    horas[i] = list(horasTeoria[alumno])
                    
                    for asignatura in combinacion:
                        horas[i].extend(asignatura["horario"])

                    colisiones[i] = len(horas[i]) - len(set(horas[i]))

                # Agrupar las combinaciones por número de colisiones
                agrupColisiones = {}
                for indexComb, colisiones in colisiones.items():
                    agrupColisiones.setdefault(colisiones, []).append(indexComb)

                # Seleccionar el grupo de menores colisiones
                menoresColisiones = sorted(agrupColisiones.items(), key=lambda x: x[0])[:1]
                for _, indices in menoresColisiones:
                    for index in indices:
                        seleccionadas[alumno].append(combinaciones[index])

                copia[alumno] = seleccionadas[alumno]

        return seleccionadas
    
     ###################################
    # Explorar Grupos Prácticas
    # Órden 23, llamada desde órden 20
    # Explora las combinaciones de subgrupos para asignar a los alumnos

    ###################################
    # Fusionar Soluciones
    # Órden 24, llamada desde órden 3
    # Unifica los datos de las soluciones completas y las solapadas

    def fusionarSoluciones(self, primeraParte, segundaParte):
        parteCompleta = primeraParte

        for asignatura, datos in segundaParte.items():

            # Si no existe, añadirla completamente
            if asignatura not in parteCompleta:
                parteCompleta[asignatura] = datos

            # Si ya existe, añadir los alumnos
            else:
                parteCompleta[asignatura]["alumnos"].extend(datos["alumnos"])
                parteCompleta[asignatura]["alumnos"] = list(set(parteCompleta[asignatura]["alumnos"]))
                parteCompleta[asignatura]["ocupacion"] = len(parteCompleta[asignatura]["alumnos"])

        return parteCompleta
    
    ###################################
    # Repaso
    # Órden 25, llamada desde orden 3
    # Elimina a cada alumno para explorar una posible combinación mejor

    def repaso(self, reparto):
        explorados = set() # Estudiantes cambiados
        sol = []
        estudiante = 1

        for par, contenido in reparto.items():
            if len(par[1]) == 1: # Buscar en grupos de teoría
                for alumno in contenido["alumnos"]: # Recorrer cada alumno
                    if alumno not in explorados and len(self.combinaciones[alumno]) > 1:
                        # Marcar alumno como cambiado
                        explorados.add(alumno)
                        estudiante += 1

                        # Eliminar alumno de sus subgrupos
                        self.__desmatricular(alumno, reparto)

                        # Explorar de nuevo la mejor combinación
                        self.explorarCombinacionesSubgrupos([(alumno, self.combinaciones[alumno])], reparto, sol, 0, 1)
                        
        return sol[-1]

    ###################################
    # Desmatricular
    # Órden 26, llamada desde 25
    # Elimina a un alumno del reparto (prácticas)

    def __desmatricular(self, alumno, reparto):
        combinacion = self.asignaciones[alumno]
        asignaturas = self.combinaciones[alumno][combinacion]

        for asignatura in asignaturas:
            clave = (asignatura["asignatura"], asignatura["grupo"])

            reparto[clave]["alumnos"].remove(alumno)
            reparto[clave]["ocupacion"] -= 1

    ###################################
    # Get Results Alumno
    # Órden 27, llamada desde Main
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
        ruta = DIR_PATH / ".." / "output" / "raw" / f"alumnosAsignados{self.cuatrimestre}.txt"
        with open(str(ruta), "w") as f:
            for alumno, asignaturas in self.solAlumno.items():
                f.write(f"\n{alumno}:\n")

                if (len(asignaturas) > 0):
                    for asignatura in sorted(asignaturas):
                        abrv, grupo = asignatura
                        horas = self.datos[asignatura]["horario"]

                        f.write(f"{abrv} - {grupo} - [{', '.join(map(str, horas))}]\n")
