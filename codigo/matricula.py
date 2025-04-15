import re
import pandas as pd
from asignatura import Asignaturas

########################

class Matriculas():
    def __init__(self, archivoMatricula, archivoAsignaturas):
        df = pd.read_csv(archivoMatricula)

        self.carreras = df["CARRERA"].tolist()
        self.dnis = df["DNI"].tolist()
        self.codigos = df["CEA"].tolist()
        self.grupos = df["GRUPO"].tolist()

        self.asignaturas = Asignaturas(archivoAsignaturas)
        self.matriculaciones = self.getMatriculaciones()
    
    ####################

    # Dni, codigoCarrera, codigoAsignatura, grupo
    ## Necesario en: getMatriculaciones y str
    def __getitem__(self, index):
        return self.dnis[index], self.carreras[index], self.codigos[index], self.grupos[index]
    
    ####################
    
    # Alumno: dni, Asignatura: codigo, Grupo: grupo, Horario: dia - hora
    ## Necesario en:
    def __str__(self):
        matAlumno = []
        for i in range(len(self.dnis)):
            matAlumno.append((self[i]))

        res = ""
        datos = self.buscarAsignatura(matAlumno)

        for i in range(len(datos)):
            for valores in datos[i].values():
                res += f"Alumno: {valores[0]}, Asignatura: {valores[1]}, Grupo: {valores[2]}, Horario: {valores[3]}\n"
        
        return res
    
    ########################################
    ########################################
    
    # Clave: alumno
    # Valor: [(asignatura0, grupo0, horas0), (asignatura1, grupo1, horas1), ...]
    ## Necesario en: constructor
    def getMatriculaciones(self):
        matAlumno = []
        for i in range(len(self.dnis)):
            matAlumno.append((self[i]))

        datos = self.buscarAsignatura(matAlumno)

        actual = None
        anterior = None
        asignaturas = []
        matriculaciones = {}

        for i in range(len(datos)):
            for valores in datos[i].values():
                actual = valores[0]

                if i == 0: 
                    anterior = actual

                if actual != anterior:
                    matriculaciones[anterior] = asignaturas
                    asignaturas = []
                    anterior = actual

                asignaturas.append((valores[1], valores[2], valores[3]))

        return matriculaciones
    
    ####################
    
    # Clave: índice
    # Valor: (dni, codigoAsignatura, grupo, horario)
    ## Necesario en: getMatriculaciones
    def buscarAsignatura(self, matricula):
        asignaturas = []

        for i in range(len(matricula)):
            for j in range(self.asignaturas.getLongitud()):
                asignatura = f"{matricula[i][1]}..{matricula[i][2]}"

                if re.fullmatch(asignatura, self.asignaturas[j][0]) and matricula[i][3] == self.asignaturas[j][2]:
                    asignaturas.append({i: (matricula[i][0], self.asignaturas[j][0], self.asignaturas[j][2], self.asignaturas.getHorario(self.asignaturas[j][0], self.asignaturas[j][2]))})
                    break
                                
        return asignaturas
    
    ########################################
    ########################################
    
    # Clave: dni
    # Valor: [{indice0: (asignatura0, (sub)grupo0), (asignatura1, (sub)grupo1), ...}
    #        {indice1: (asignatura0, (sub)grupo0), (asignatura1, (sub)grupo1), ...}]
    ## Necesario en: Main
    def getCombinacionSubgrupos(self):
        combinaciones = {}
        subgruposAlumno = self.getPosiblesSubgrupos()

        for alumno in subgruposAlumno.keys():
            combinaciones[alumno] = []
            gpTeoria = self.getGpTeoriaAsignatura(alumno)
            self.combinarSubgrupos(subgruposAlumno[alumno], gpTeoria, combinaciones[alumno], len(gpTeoria)*2)

        return combinaciones
                
    ####################
    
    # Devuelve las combinaciones factibles entre grupos
    # y subgrupos de las asignaturas de un alumno
    ## Necesario en: getCombinacionSubgrupos
    def combinarSubgrupos(self, asignaturas, mixActual, resultado, tamFin):
        # Si se alcanza el tamaño final de la combinacion
        if len(mixActual) == tamFin:
            # Ordenar la combinacion de la copia para no alterar modificaciones futuras
            ordenado = sorted(mixActual.copy())

            # Evitar inclusiones del tipo (b,a) si ya hay (a,b)
            if ordenado not in resultado:
                # Añadir la combinacion a la lista de resultados
                resultado.append(ordenado)
            return

        else:
            # Por cada asignatura de todas las asignaturas de un alumno
            for dictAsignatura in asignaturas:

                # Código asignatura
                asignatura = list(dictAsignatura.keys())[0]

                # Subgrupos de una asignatura
                subgrupos = list(dictAsignatura.values())[0]

                # No introducir más de un subgrupo por grupo de asignatura
                count = 0 # Apariciones
                for pareja in mixActual:
                    if asignatura == pareja[0]:
                        count += 1 

                # Si es el primer subgrupo
                if count == 1:
                    # Por cada subgrupo del conjunto de subgrupos
                    for subgrupo in subgrupos:

                        # Comprobar si coinciden las horas de la combinacion actual con la nueva asignatura a introducir
                        if not self.solapamiento(asignatura, subgrupo, mixActual):
                            # Incluir el subgrupo en la combinacion
                            mixActual.append((asignatura, subgrupo))

                            # Seguir explorando adiciones en la combinacion
                            self.combinarSubgrupos(asignaturas, mixActual, resultado, tamFin)

                            # Explorar otras combinaciones
                            mixActual.pop()

    ####################

    # Compruba si hay solapamiento de una asignatura nueva a un grupo de ellas
    ## Necesario en: combinarSubgrupos
    def solapamiento(self, asigNueva, gpNuevo, combinacion):
        horasRellenas = []
        nuevaHora = self.asignaturas.getCodigoHoras(asigNueva, gpNuevo)

        for asig, grupo in combinacion:
            codigo = self.asignaturas.getCodigoHoras(asig, grupo)
            
            for i in codigo:
                horasRellenas.append(i)

        for hora in nuevaHora:
            if hora in horasRellenas:
                return True
            
        return False
    
    ########################################
    
    # Devuelve todos los grupos de teoría con su asignatura de un alumno
    ## Necesario en: getCombinacionSubgrupos
    def getGpTeoriaAsignatura(self, alumno):
        res = []
        for i in self.matriculaciones[alumno]:
                res.append((i[0], i[1]))

        return res
    
    ####################

    # Clave: dni
    # Valor: [{asignatura0: [subgrupo0, subgrupo1, subgrupo2]}, {asignatura1: [subgrupo0, subgrupo1, subgrupo2]}, ...]
    ## Necesario en: getCombinacionSubgrupos
    def getPosiblesSubgrupos(self):
        subgrupos = []
        resultado = {}

        for i in self.matriculaciones:
            asignaturas = self.getAsignaturasAlumno(i)

            for j in range(len(asignaturas)):
                asignaturaSubgrupos = self.buscarSubgrupos(asignaturas[j][0], asignaturas[j][1])
                subgrupos.append(asignaturaSubgrupos) 
                
            resultado[i] = subgrupos
            subgrupos = []
        
        return resultado
                                    
    ########################################

    # Devuelve las asignaturas, grupos y horas de la persona que coincide con el dni
    ## Necesario en: getPosiblesSubgrupos
    def getAsignaturasAlumno(self, alumno):
        return self.matriculaciones[int(alumno)]
    
    ####################
    
    # Clave: asignatura
    # Valor: [subgrupo0, subgrupo1, subgrupo2]
    ## Necesario en: getPosiblesSubgrupos
    def buscarSubgrupos(self, codigo, grupo):
        asignaturas = {}
        subgrupos = []

        subgrupo = f"{grupo}."
        for i in self.asignaturas:
            if (codigo == i[0]) and re.fullmatch(subgrupo, i[2]):
                subgrupos.append(i[2])

        asignaturas[codigo] = subgrupos
        return asignaturas

    ########################################
    ########################################