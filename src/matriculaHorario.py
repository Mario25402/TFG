import re
import copy
import pandas as pd

class matriculaHorario():

    ###################################
    # Constructor
    # Órden 0, llamada desde Main
    # Inicializa todo lo necesario

    def __init__(self, fileMat, fileHor):
        # Cargar matrículas
        df = pd.read_csv(fileMat)

        carreras = df["CARRERA"].tolist()
        dnis = df["DNI"].tolist()
        codigos = df["CEA"].tolist()
        grupos = df["GRUPO"].tolist()

        ###
        # Cargar horarios

        df = pd.read_csv(fileHor)

        codigosCompletos = df["CODIGO"].tolist()
        nombres = df["ASIGNATURA"].tolist()
        gruposTP = df["GRUPO"].tolist()
        horas = [df[f"HORA{i}"].tolist() for i in range(1, 6)]

        ###
        # Inicializar variables

        self.datos = {}         # Datos trascritos de los archivos
        self.sinAsignar = {}    # Datos de subgrupos posibles
        self.combinaciones = {} # Combinaciones de subgrupos posibles

        for alumno in dnis:
            self.datos[alumno] = []
            self.sinAsignar[alumno] = []
            self.combinaciones[alumno] = []

        ###
        # Rellenar "datos" y "sinAsignar"

        # Recorrer matricula por cada alumno
        for i in range(len(dnis)):
            patronSgn = f"{carreras[i]}..{codigos[i]}"
            patronSgp = f"{grupos[i]}."

            # FIS(A1) solo ADE
            cambio = False
            if patronSgn == '216..3B':
                cambio = True
                patronSgn = '297..32'


            # Unificar grupos donde los dobles grados van juntos
            sustituciones = {
                '216..34': '297..3B', # SCD
                '216..35': '297..33', # FR
                '216..44': '297..45', # IG
                '216..45': '297..43', # DDSI
                                      # FIS
                '216..3C': '297..39', # ISE
                '216..3A': '297..3A'  # IA
            }
            patronSgn = sustituciones.get(patronSgn, patronSgn)

            # Buscar en horarios la asignatura
            for j in range(len(codigosCompletos)):
                if re.fullmatch(patronSgn, codigosCompletos[j]): # Teoría

                    if grupos[i] == gruposTP[j]:
                        codigoHoras = [int(x) for lista in horas for x in [lista[j]] if pd.notna(x)]

                        self.datos[dnis[i]].append({
                            "codigo": codigosCompletos[j],
                            "asignatura": nombres[j],
                            "grupo": grupos[i],
                            "horario": codigoHoras
                        })

                    elif re.fullmatch(patronSgp, gruposTP[j]): # Prácticas

                        # Solo asignar FIS(A1) a alumnos de ADE
                        if codigosCompletos[j] == '2971132' and gruposTP[j] == 'A1' and not cambio:
                            continue

                        if nombres[j] != "IES": # No añadir subgrupos de IES
                            codigoHoras = [int(x) for lista in horas for x in [lista[j]] if pd.notna(x)]

                            self.sinAsignar[dnis[i]].append({
                                "codigo": codigosCompletos[j],
                                "asignatura": nombres[j],
                                "grupo": gruposTP[j],
                                "horario": codigoHoras
                            })

                        # Ajustar horas de teoría y prácticas de ISE
                        else:
                            codigoHoras = [int(x) for lista in horas for x in [lista[j]] if pd.notna(x)]
                            self.datos[dnis[i]][len(self.datos[dnis[i]])-1]["horario"].extend(codigoHoras)
                            
                            sinRepetidos = list(set(self.datos[dnis[i]][len(self.datos[dnis[i]])-1]["horario"]))
                            self.datos[dnis[i]][len(self.datos[dnis[i]])-1]["horario"] = sinRepetidos

        ###
        # Rellenar "combinaciones"

        self.asignarCombinaciones()

    ###################################
    # Asignar Combinaciones
    # Órden 1, llamada desde órden 0
    # Asigna los subgrupos de alumnos con y sin combinaciones

    def asignarCombinaciones(self):
        for alumno in self.datos.keys():

            # No explorar subgrupos si ya hay solapamiento en teoría
            if not self.isSolapamientoTeoria(alumno):
                subgrupos = sorted(self.sinAsignar[alumno], key=lambda x: (x['codigo'], x['grupo']))

                if subgrupos != []:
                    self.calcCombinaciones(subgrupos, self.datos[alumno], self.combinaciones[alumno], False)

    ###################################
    # Solapamiento Teoría
    # Órden 2, llamada desde órden 1
    # Comprueba si hay horas de teoría que se solapan

    def isSolapamientoTeoria(self, alumno):
        horas = []

        for asignatura in self.datos[alumno]:
            for hora in asignatura['horario']:
                horas.append(hora)

        if len(horas) != len(set(horas)):
            return True

        return False
    
    ###################################
    # Calcular Combinaciones
    # Órden 3, llamada desde órden 1
    # Devuelve las combinaciones de subgrupos de cada alumno 

    def calcCombinaciones(self, subgruposAlumno, actual, combinaciones, solapar=False):
        codTeoria = {asignatura['codigo'] for asignatura in actual}

        # Eliminar IES
        if '2211115' in codTeoria:
            codTeoria.remove('2211115')

        if '2961119' in codTeoria:
            codTeoria.remove('2961119')

        ###################################
        # Backtrack
        # Órden 4, llamada desde órden 3
        # Explora las combinaciones de subgrupos de cada alumno

        def backtrack(index, combActual, usados, solapar=False):
            if usados == codTeoria:
                orden = sorted(copy.deepcopy(combActual), key=lambda x: (x['codigo'], x['grupo']))
                combinaciones.append(orden)
                return
            
            if index == len(subgruposAlumno):
                return
            
            subgrupo = subgruposAlumno[index]
            codigo = subgrupo['codigo']

            if codigo in codTeoria and codigo not in usados:
                if self.isFactible(subgrupo, actual + combActual, solapar):
                    combActual.append(subgrupo)
                    usados.add(codigo)

                    backtrack(index + 1, combActual, usados, solapar)
                    
                    combActual.pop()
                    usados.remove(codigo)
                
            backtrack(index + 1, combActual, usados, solapar)
    
        backtrack(0, [], set(), solapar)

    ###################################
    # Factible
    # Órden 5, llamada desde órden 4
    # Decide si un grupo es añadido a una combinación

    def isFactible(self, nueva, actual, solapar=False):
        nuevoCod = nueva['codigo']
        nuevaHora = set(nueva['horario'])

        apariciones = 0

        for asignatura in actual:
            # Contar asignaturas con el mismo código
            if asignatura['codigo'] == nuevoCod:
                apariciones += 1

                if apariciones >= 2:
                    return False  

            # Verificar solapamiento de horarios
            if (solapar == False):
                horarioActual = set(asignatura['horario'])
                if nuevaHora & horarioActual:
                    # Ignorar solapamiento entre AL y AM del mismo subgrupo
                    if (asignatura['codigo'] == "2211111" and nuevoCod == "2211112") or (
                        asignatura['codigo'] == "2211112" and nuevoCod == "2211111"):
                        if (asignatura["grupo"] == nueva["grupo"]):
                            return True
                    
                    return False  # Hay solapamiento

        return True

    ###################################
    # Get Sin Asignar
    # Órden 6, llamada desde Main
    # Devuelve los alumnos con solapamientos

    def getSinAsignar(self):
        res = {}
        for alumno in self.sinAsignar.keys():
            res[alumno] = []

            # Si no tiene combinaciones, coger subgrupos
            if self.combinaciones[alumno] == []:    
                subgrupos = sorted(self.sinAsignar[alumno], key=lambda x: (x['codigo'], x['grupo']))

                if subgrupos != []:
                    self.calcCombinaciones(subgrupos, self.datos[alumno], res[alumno], True)

        return res