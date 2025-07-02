import os
import re
import pandas as pd

class ProcesadorHorarios:
    
    # Variables de la clase
    COL_CURSO = 0
    FIL_CURSO = 1
    DESCANSO1 = 16
    DESCANSO2 = 48
    CONTENIDO1_INI = 4
    CONTENIDO1_FIN = 28
    CONTENIDO2_INI = 36
    CONTENIDO2_FIN = 60
    COL_CONTENIDO_INI = 1
    COL_CONTENIDO_FIN = 16
    
    ###

    codigosAsignaturas = {
        "CA(A)": "2161113",
        "TOC(A)": "2161114",
        "FP(A)": "2161115",
        "FFT(A)": "2161116",
        "MP(A)": "216111B",
        "FS(A)": "216111C",
        "ALEM(A)": "216111D",
        "ED(A)": "2161125",
        "EC(A)": "2161126",
        "SO(A)": "2161127",
        "LMD(A)": "216112B",
        "ALG(A)": "216112C",
        "AC(A)": "216112D",
        "PDOO(A)": "2161136",
        "FBD(A)": "216113D",
        "MC(A)": "2161146",
        "AM": "2211111",
        "AL": "2211112",
        "AC": ["2211113", "296112A"],
        "FI": "2211114",
        "IES": ["2211115", "2961119"],
        "EDCN": "2211116",
        "EO": "2211117",
        "CCE": "2211118",
        "SL": "2211119",
        "FFI": "221111A",
        "TC": "2211121",
        "TO": "2211122",
        "ST": "2211123",
        "FPR": "2211124",
        "C1": "2211126",
        "SD": "2211127",
        "EA": "2211129",
        "IRC": "221112A",
        "C2": "2211131",
        "EP": "2211132",
        "SED": "2211133",
        "TDRC": ["2211134", "296113Z"],
        "SCM": "2211135",
        "TDS": "2211136",
        "SCA": "2211137",
        "MCO": "2211138",
        "AP": "2211139",
        "SR": "221113A",
        "DAR": "221113B",
        "SRC": "221113C",
        "CP": "221113D",
        "RIM": "221113E",
        "GR": "221113F",
        "CERF": "221113G",
        "EM": "221113H",
        "IE": "221113I",
        "DCSE": "221113J",
        "SAL": "221113K",
        "CO": "2211141",
        "CI": "2211142",
        "TRD": "2211143",
        "RAC": "2211144",
        "RM": "2211145",
        "DDR": "2211146",
        "CIC": "2211147",
        "SC": "2211148",
        "EE": "2211149",
        "FF": "22111A1",
        "FAT": "22111A2",
        "CAM": "22111A3",
        "TH": "22111AA",
        "PVD": "22111AB",
        "LT": "22111BA",
        "PSETR": "22111BB",
        "TCI": "22111CA",
        "AET": "22111CB",
        "ALEM": "2961111",
        "CA": "2961112",
        "FFT": "2961113",
        "FS": "2961114",
        "FP": "2961115",
        "LMD": "2961116",
        "TOC": "2961117",
        "MP": "2961118",
        "ES": "296111A",
        "PDOO": "2961121",
        "ED": ["2961122", "2211128"],
        "SO": "2961123",
        "SCD": "2961124",
        "EC": "2961125",
        "ALG": "2961126",
        "FIS": "2961127",
        "FBD": "2961128",
        "IA": "2961129",
        "MC": "2961131",
        "DDSI": "2961132",
        "IG": "2961133",
        "FR": "2961134",
        "ISE": "2961135",
        "IC": "296113A",
        "TSI": "296113B",
        "AA": "296113C",
        "MAC": "296113D",
        "MH": "296113E",
        "DS": "296113F",
        "DGP": "296113G",
        "SG": "296113H",
        "DSD": "296113I",
        "SIBW": "296113J",
        "AS": "296113K",
        "ACAP": "296113L",
        "DSE": "296113M",
        "DHD": "296113N",
        "SMP": "296113P",
        "PW": "296113Q",
        "SIE": "296113R",
        "ISI": "296113S",
        "ABD": "296113T",
        "SMD": "296113U",
        "SMM": "296113V",
        "CUIA": "296113W",
        "TW": "296113X",
        "SWAP": "296113Y",
        "PL": "296114A",
        "VC": "296114B",
        "NPI": "296114C",
        "MDA": "296114D",
        "DIU": "296114E",
        "DBA": "296114F",
        "TR": "296114G",
        "CPD": "296114H",
        "SE": "296114I",
        "RI": ["296114J", "29611AC"],
        "IN": "296114K",
        "BDD": "296114L",
        "DAI": "296114M",
        "IV": "296114N",
        "SPSI": "296114P",
        "EISI": "29611A2",
        "CEGE": "29611A5",
        "DI": "29611A6",
        "TIC": "29611AA",
        "PLD": "29611AB",
        "PTC": "29611AD",
        "SS": "29611AE",
        "CRIP": "29611AF",
        "LP": "29611BA",
        "PGV": "29611BB",
        "PPR": "29611BC",
        "NTP": "29611BD",
        "AO": "29611BE",
        "SSO": "29611BF",
        "II": "29611CB",
        "CII": "29611CC",
        "TE": "29611CD",
        "MEI": "29611CF",
        "SIG": "29611DA",
        "PDIH": "29611DB",
        "GRD": "29611DC",
        "SCGC": "29611DD",
        "RSC": "29611DE",
        "TID": "29611FA",
        "PDS": "29611FB",
        "CRIM": "29611FC",
        "PDM": "29611FD",
        "RMS": "29611FE",
        "FP(M)": "2971112",
        "FS(M)": "2971113",
        "FFT(M)": "2971114",
        "LMD(M)": "2971116",
        "MP(M)": "297111A",
        "TOC(M)": "297111C",
        "EC(M)": "2971123",
        "ED(M)": "2971124",
        "SO(M)": "2971125",
        "ALG(M)": "2971127",
        "AC(M)": "2971129",
        "PDOO(M)": "297112C",
        "FBD(M)": "2971131",
        "FIS(MA)": "2971132",
        "FR(MA)": "2971133",
        "MC(M)": "2971135",
        "ISE(MA)": "2971139",
        "IA(MA)": "297113A",
        "SCD(MA)": "297113B",
        "DDSI(MA)": "2971143",
        "IG(MA)": "2971145",
        "IES(M)": "2971151"
    }

    ###

    filasHora = {
        4: "01", 36: "01",  # 8:30
        6: "02", 38: "02",  # 9:30
        8: "03", 40: "03",  # 10:30
        10: "04", 42: "04", # 11:30
        12: "05", 44: "05", # 12:30
        14: "06", 46: "06", # 13:30
        16: "07", 48: "07", # 14:30
        17: "08", 49: "08", # 15:30
        19: "09", 51: "09", # 16:30
        21: "10", 53: "10", # 17:30
        23: "11", 55: "11", # 18:30
        25: "12", 57: "12", # 19:30
        27: "13", 59: "13"  # 20:30
    }

    ###

    columnasDia = {}

    ####################

    def __init__(self, archivo):
        
        # Procesar archivo según extensión
        extension = os.path.splitext(archivo)[1].lower()

        if extension == ".ods":
            horarios = pd.read_excel(archivo, sheet_name=None, header=None, engine="odf")
        elif extension == ".xlsx":
            horarios = pd.read_excel(archivo, sheet_name=None, header=None, engine="openpyxl")
        else:
            raise ValueError("Formato soportados .ods o .xlsx")
        
        ###
        # Inicializar variables

        self.datos = {}
        self.aula = None
        self.subgrupo = None
        self.asignatura = None

        ###
        # Recorrer las páginas y extraer la información
        
        for pagina, df in horarios.items():
            print(f"Procesando {pagina}...")
            iniDias = []

            # Registrar donde empieza cada día
            for numCol in range(df.shape[1]):
                celda = df.iat[3, numCol]

                if pd.notna(celda):
                    iniDias.append(numCol);
            
            self.rellenarAnchoDias(iniDias, df.shape[1])

            ###
            
            for numCol in range(df.shape[1]):

                # Guardar curso y grupo
                if numCol == self.COL_CURSO:
                    for numFila in range(0, self.CONTENIDO1_INI - 1):
                        if numFila == self.FIL_CURSO:
                            texto = df.iat[numFila, numCol].replace(" ", "")

                            if "(" not in texto:
                                self.grupo = texto[2]
                            else:
                                self.grupo = "A"

                            self.curso = texto[0]
                            break

                elif numCol >= self.COL_CONTENIDO_INI and numCol < df.shape[1] -2:

                    # Primer Cuatrimestre
                    for numFila in range(self.CONTENIDO1_INI, self.CONTENIDO1_FIN):
                        celda = df.iat[numFila, numCol]

                        if pd.notna(celda):
                            self.procesarCelda(celda, numFila, numCol, 1)

                    # Segundo Cuatrimestre
                    for numFila in range(self.CONTENIDO2_INI, df.shape[0]):
                        celda = df.iat[numFila, numCol]

                        if pd.notna(celda):
                            self.procesarCelda(celda, numFila, numCol, 2)

        self.datos = dict(sorted(self.datos.items()))

    #####

    def procesarCelda(self, celda, numFila, numCol, cuatrimestre):

        # Antes de mediodía
        if numFila < self.DESCANSO1 or (numFila > self.CONTENIDO2_INI and numFila < self.DESCANSO2):
            if numFila % 2 == 0:
                self.asignatura = celda
                patron = rf"\({self.grupo}(\d+)\)"
                match = re.search(patron, self.asignatura)

                if match:
                    self.subgrupo = f"{self.grupo}{match.group(1)}"
                    self.asignatura = re.sub(patron, "", self.asignatura).strip()
            else:
                self.aula = celda

        # Después de mediodía
        else:
            if numFila % 2 != 0:
                self.asignatura = celda
                patron = rf"\({self.grupo}(\d+)\)"
                match = re.search(patron, self.asignatura)

                if match:
                    self.subgrupo = f"{self.grupo}{match.group(1)}"
                    self.asignatura = re.sub(patron, "", self.asignatura).strip()

            else:
                self.aula = celda
                

        ###

        # Guardar datos en el diccionario
        if self.asignatura and self.aula:
            codigo = self.traducirCodigo(numFila-1, numCol)
            clave = (self.asignatura, self.subgrupo or self.grupo) # Establecer subgrupo si lo hay

            if 'SG' in clave[0]:
                pass

            # Si ya existe la clave, añadir la hora nueva
            if self.datos.get(clave):
                self.datos[clave]["horario"].append(codigo)

            else:
                self.datos[clave] = {
                    "codigo": self.codigosAsignaturas[self.asignatura],
                    "asignatura": self.asignatura,
                    "horario": [codigo],
                    "aula": self.aula,
                    "curso": self.curso,
                    "grupo": self.subgrupo or self.grupo,
                    "cuatrimestre": cuatrimestre
                }

            self.aula = None
            self.subgrupo = None
            self.asignatura = None

    #####

    def traducirCodigo(self, fila, columna):
        return f"{self.columnasDia[columna]}{self.filasHora[fila]}"

    ####################

    def rellenarAnchoDias(self, posDias, anchoMax):
        dia = 0
        colDias = {}

        for col in range(anchoMax):
            for start in posDias:
                if col == start:
                    dia += 1

                colDias[col] = dia

        self.columnasDia = colDias

    ####################

    def generarCSV(self):
        registros = []

        for (asignatura, grupo), info in self.datos.items():
            codigo = info["codigo"]

            if isinstance(info["codigo"], list):
                codigo = info["codigo"][1]

            fila = {
                "CODIGO": codigo,
                "ASIGNATURA": asignatura,
                "GRUPO": grupo,
                "AULA": info["aula"],
                "CURSO": info["curso"],
                "CUATRIMESTRE": info["cuatrimestre"],
            }

            # Desglosar las horas en columnas separadas
            for i, hora in enumerate(info.get("horario", [])):
                fila[f"HORA{i+1}"] = hora

            registros.append(fila)

        # Ordenar registros
        registros = sorted(registros, key=lambda x: (x["CODIGO"]))

        # Crear el DataFrame
        df = pd.DataFrame(registros)

        # Guardar como CSV
        df.to_csv("horarios.csv", index=False, sep=',', encoding='utf-8-sig')


    ####################

horarios = ProcesadorHorarios("./jesus/HorariosGII(24-25).xlsx")
horarios.generarCSV()