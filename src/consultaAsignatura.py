import ast
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph

########################################
# Rutas de los archivos

DIR_PATH = Path(__file__).parent.resolve()

PRIMERCUATRI = DIR_PATH / ".." / "output" / "raw" / "asignaturasAsignadas1.txt"
SEGUNDOCUATRI = DIR_PATH / ".." / "output" / "raw" / "asignaturasAsignadas2.txt"

###
# Convierte el texto en información estructurada

def procesarTexto(ruta):
    datos = {}
    clave_actual = None

    with open(ruta, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea: # Vacio
                continue

            # (Asignatura, grupo)
            if linea.startswith("Asignatura:"):
                clave_str = linea.replace("Asignatura:", "").strip()
                clave_str = clave_str.replace(":", "")
                clave_actual = ast.literal_eval(clave_str)
                datos[clave_actual] = {}

            # Información de cada entrada
            else:
                valores = ast.literal_eval(linea)  # convierte texto en valores
                datos[clave_actual] = valores

    return datos

###

def __buscarSubrupo(lista_grupos, alumno_teoria):
    for subgrupo, alumnos in enumerate(lista_grupos):
        if alumno_teoria in alumnos:
            return subgrupo + 1

###

def exportPDF(objeto, ruta):
    for asignatura, grupos in objeto.items():
        for grupo, lista_grupos in grupos.items():
            # Crear documento
            rutaFinal = ruta / f"{asignatura}_{grupo}.pdf"
            doc = SimpleDocTemplate(str(rutaFinal), pagesize=A4)
            contenido = []

            # Titulos y cabeceras de la tabla
            titulo = Paragraph(f"Asignatura: {asignatura} - Grupo: {grupo}", getSampleStyleSheet()["Title"])

            estilo = getSampleStyleSheet()["Heading2"]
            estilo.alignment = TA_CENTER
            subtitulo = Paragraph(f"Alumnos: {len(lista_grupos[0])}", estilo)

            cabecera = [["DNI", "Subgrupo"]]
            info = []

            contenido.append(titulo)
            contenido.append(subtitulo)
            contenido.append(Spacer(1, 12))

            ###

            # Contenido
            numSubgrupos = len(lista_grupos)

            # Con subgrupos
            if numSubgrupos > 1:
                for alumno_teoria in lista_grupos[0]:
                    subgrupo = __buscarSubrupo(lista_grupos[1:], alumno_teoria)
                    info.append([alumno_teoria, str(subgrupo)])
                    
            # Sin subgrupos
            elif len(lista_grupos) == 1:
                for alumno in lista_grupos[0]:
                    info.append([alumno, "1"])

            # Ordenar alumnos
            info.sort(key=lambda x: x[1])
            info = cabecera + info

            ###

            # Crear la tabla
            tabla = Table(info, colWidths=[100, 60])
            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#11645d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))

            contenido.append(tabla)
            doc.build(contenido)

########################################
# Inicialización

def execute():
    datos1 = procesarTexto(PRIMERCUATRI)
    datos2 = procesarTexto(SEGUNDOCUATRI)

    res = {}

    ###
    # Procesamiento
    # Primer Cuatrimestre

    for clave in datos1.keys():
        if clave[0] == 'TDRC':
            clave = ('TDRC(T)', clave[1])
        res[str(clave[0])] = {}

    for clave in datos1.keys():
        if clave[0] == 'TDRC':
            clave = ('TDRC(T)', clave[1])
        res[str(clave[0])][str(clave[1])[0]] = []

    for clave, valores in datos1.items():
        if clave[0] == 'TDRC':
            clave = ('TDRC(T)', clave[1])
        res[str(clave[0])][str(clave[1])[0]].append(valores["alumnos"])

    ###
    # Segundo Cuatrimestre

    for clave in datos2.keys():
        res[str(clave[0])] = {}

    for clave in datos2.keys():
        res[str(clave[0])][str(clave[1])[0]] = []

    for clave, valores in datos2.items():
        res[str(clave[0])][str(clave[1])[0]].append(valores["alumnos"])

    ###
    # Salida

    ruta = DIR_PATH / ".." / "output" / "asignaturas" 
    exportPDF(res, ruta)
