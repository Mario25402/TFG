import re
import copy
import pandas as pd

class MatriculaHorario():
    def __init__(self, fileMat, fileHor):
        # Cargar matrículas
        df = pd.read_csv(fileMat)

        carreras = df["CARRERA"].tolist()
        dnis = df["DNI"].tolist()
        codigos = df["CEA"].tolist()
        grupos = df["GRUPO"].tolist()
        #denominaciones = df["DENOMINACIÓN"].tolist()

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
        self.asignados = {}     # Datos de subgrupos asignados
        self.combinaciones = {} # Combinaciones de subgrupos posibles

        for alumno in dnis:
            self.datos[alumno] = []
            self.sinAsignar[alumno] = []
            self.asignados[alumno] = []
            self.combinaciones[alumno] = []

        ###
        # Rellenar "datos" y "sinAsignar"

        for i in range(len(dnis)):
            patronSgn = f"{carreras[i]}..{codigos[i]}"
            patronSgp = f"{grupos[i]}."

            cambio = False
            if patronSgn == '216..3B':
                cambio = True
                patronSgn = '297..32'

            for j in range(len(codigosCompletos)):
                if re.fullmatch(patronSgn, codigosCompletos[j]):

                    if grupos[i] == gruposTP[j]:
                        codigoHoras = [int(x) for lista in horas for x in [lista[j]] if pd.notna(x)]

                        self.datos[dnis[i]].append({
                            "codigo": codigosCompletos[j],
                            "asignatura": nombres[j],
                            "grupo": grupos[i],
                            "horario": codigoHoras
                        })

                    elif re.fullmatch(patronSgp, gruposTP[j]):

                        if codigosCompletos[j] == '2971132' and gruposTP[j] == 'A1' and not cambio:
                            continue

                        if nombres[j] != "IES":
                            codigoHoras = [int(x) for lista in horas for x in [lista[j]] if pd.notna(x)]

                            self.sinAsignar[dnis[i]].append({
                                "codigo": codigosCompletos[j],
                                "asignatura": nombres[j],
                                "grupo": gruposTP[j],
                                "horario": codigoHoras
                            })

                        else:
                            codigoHoras = [int(x) for lista in horas for x in [lista[j]] if pd.notna(x)]
                            self.datos[dnis[i]][len(self.datos[dnis[i]])-1]["horario"].extend(codigoHoras)
                            
                            sinRepetidos = list(set(self.datos[dnis[i]][len(self.datos[dnis[i]])-1]["horario"]))
                            self.datos[dnis[i]][len(self.datos[dnis[i]])-1]["horario"] = sinRepetidos

        ###
        # Rellenar "combinaciones"

        self.getCombinacionSubgrupos()
        self.sinCombinaciones()

    ####################

    def solapamientoTeoria(self, alumno):
        horas = []

        for asignatura in self.datos[alumno]:
            for hora in asignatura['horario']:
                horas.append(hora)

        if len(horas) != len(set(horas)):
            return True

        return False


    def getCombinacionSubgrupos(self):
        for alumno in self.datos.keys():

            # No explorar subgrupos si ya hay solapamiento en teoría
            if not self.solapamientoTeoria(alumno):
                subgrupos = sorted(self.sinAsignar[alumno], key=lambda x: (x['codigo'], x['grupo']))

                if subgrupos != []:
                    self.combinarSubgrupos(subgrupos, self.datos[alumno], self.combinaciones[alumno], True)
                        
    ###

    def combinarSubgrupos(self, subgruposAlumno, actual, combinaciones, solapar=False):
        codTeoria = {asignatura['codigo'] for asignatura in actual}

        # Eliminar IES
        if '2211115' in codTeoria:
            codTeoria.remove('2211115')

        if '2961119' in codTeoria:
            codTeoria.remove('2961119')

        ###

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
                if self.factible(subgrupo, actual + combActual, solapar):
                    combActual.append(subgrupo)
                    usados.add(codigo)

                    backtrack(index + 1, combActual, usados, solapar)
                    
                    combActual.pop()
                    usados.remove(codigo)
                
            backtrack(index + 1, combActual, usados, solapar)
    
        backtrack(0, [], set(), solapar)

    ###

    def factible(self, nueva, actual, solapar=False):
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

    
    ####################

    def sinCombinaciones(self):
        alumnos = []

        for alumno, matriculas in self.datos.items():
            if matriculas != [] and self.combinaciones[alumno] == []:
                alumnos.append(alumno)

        # Fichero de alumnos sin combinaciones
        with open("./res/sinComb.txt", "w") as f:            
            for i, alumno in enumerate(alumnos):
                f.write(f"\n\nAlumno Nº {i}: {alumno}\n")

                f.write(f"\nTeoría: {self.datos[alumno]}\n")
                f.write(f"\nHoras Teoría: {[hora for asignatura in self.datos[alumno] for hora in asignatura['horario']]}\n")

                f.write(f"\nSubgrupos:\n")
                for i, combinacion in enumerate(self.sinAsignar[alumno]):
                    f.write(f"Posibilidad {i}:\t{combinacion}\n")


    def getSinAsignar(self):
        res = {}
        for alumno in self.sinAsignar.keys():
            res[alumno] = []

            if self.combinaciones[alumno] == []:    
                subgrupos = sorted(self.sinAsignar[alumno], key=lambda x: (x['codigo'], x['grupo']))

                if subgrupos != []:
                    self.combinarSubgrupos(subgrupos, self.datos[alumno], res[alumno], True)

        return res

    ####################

    def combinacionesToString(self):
        for alumno in self.combinaciones.keys():
            print(f"Alumno: {alumno}")
            for i, combinacion in enumerate(self.combinaciones[alumno]):
                print(f"Combinación {i+1}:")
                for subgrupo in combinacion:
                    print(f"  - {subgrupo['asignatura']} ({subgrupo['grupo']})")
            print()