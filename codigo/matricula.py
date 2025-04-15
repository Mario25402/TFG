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

    ####################
    
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

    # Devuelve las asignaturas, grupos y horas de la persona que coincide con el dni
    ## Necesario en: getPosiblesSubgrupos
    def getAsignaturasAlumno(self, alumno):
        return self.matriculaciones[int(alumno)]
    
    ####################

    # Devuelve la información de la persona que coincide con el índice
    ## Necesario en: 
    def getIndex(self, index):
        lista = list(self.matriculaciones.keys())
        clave = lista[index]

        return {clave: self.getAsignaturasAlumno(clave)}
    
    ####################

    # Clave: dni
    # Valor: [{asignatura0: [subgrupo0, subgrupo1, subgrupo2]}, {asignatura1: [subgrupo0, subgrupo1, subgrupo2]}, ...]
    ## Necesario en: getCombinacionSubgrupos
    def getPosiblesSubgrupos(self):
        resultado = {}
        subgrupos = []

        for i in self.matriculaciones:
            asignaturas = self.getAsignaturasAlumno(i)

            for j in range(len(asignaturas)):
                asignaturaSubgrupos = self.buscarSubgrupos(asignaturas[j][0], asignaturas[j][1])
                subgrupos.append(asignaturaSubgrupos) 
                
            resultado[i] = subgrupos
            subgrupos = []
        
        return resultado
                                    
    ####################

    # Devuelve el grupo de teoría de la "asignatura" de un alumno
    ## Necesario en:
    def getGrupoTeoria(self, asignatura, alumno):
        for i in self.matriculaciones[alumno]:
            if i[0] == asignatura:
                return i[1]
            
    ####################

    # Devuelve todos los grupo de teoría de las asignaturaa de un alumno
    ## Necesario en: getCombinacionSubgrupos
    def getGruposTeoria(self, alumno):
        res = []

        for i in self.matriculaciones[alumno]:
                res.append((i[0], i[1]))

        return res
    
    ####################

    # Compruba si hay solapamiento de una asignatura nueva a un grupo de ellas
    ## Necesario en: combinarSubgrupos
    def solapamiento(self, asignaturaNueva, grupoNuevo, rellenados):
        codigosRellenados = []
        nuevo = self.asignaturas.getCodigoHoras(list(asignaturaNueva.keys())[0], grupoNuevo)

        for asig, grupo in rellenados:
            codigo = self.asignaturas.getCodigoHoras(asig, grupo)
            codigosRellenados.extend(codigo)

        if nuevo[0] in codigosRellenados:
            return True
        else:
            return False

    ####################

    # Devuelve las combinaciones factibles entre grupos
    # y subgrupos de las asignaturas de un alumno
    ## Necesario en: getCombinacionSubgrupos
    def combinarSubgrupos(self, alumno, asignaturas, actual, resultado, tamFin):
        if len(resultado) == tamFin:
            resultado.extend(actual)

        else:
            j = 0
            for dictAsignatura in asignaturas:
                for i in asignaturas[j].values():
                    for k in i:
                        if not self.solapamiento(dictAsignatura, k, actual):

                            count = 0
                            for k in actual:
                                if dictAsignatura == k[0]:
                                    count += 1 

                            if count == 1:
                                actual.append((dictAsignatura, i))
                                self.combinarSubgrupos(alumno, asignaturas, actual, resultado, tamFin-1)
                                actual.pop()
                j += 1

    ####################
    
    # Clave: dni
    # Valor: [{indice0: (asignatura0, (sub)grupo0), (asignatura1, (sub)grupo1), ...}
    #        {indice1: (asignatura0, (sub)grupo0), (asignatura1, (sub)grupo1), ...}]
    ## Necesario en: Main
    def getCombinacionSubgrupos(self):
        combinaciones = {}
        subgruposAlumno = self.getPosiblesSubgrupos()

        # Alumno
        for alumno in subgruposAlumno.keys():
            combinaciones[alumno] = []
            actual = []

            # Grupos Teoría
            actual = self.getGruposTeoria(alumno)

            # Subgrupos Prácticas
            self.combinarSubgrupos(alumno, subgruposAlumno[alumno], actual, combinaciones[alumno], len(actual)*2)

        return combinaciones
                
    ####################