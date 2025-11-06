import ast
import statistics
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
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

def exportPDF(objeto, nombrePDF="salida.pdf"):
    # Crear documento
    doc = SimpleDocTemplate(nombrePDF, pagesize=A4)
    contenido = []

    ###

    # Titulo
    titulo = Paragraph("Reparto de Alumnos por Asignatura y Grupo", getSampleStyleSheet()["Title"])
    contenido.append(titulo)
    contenido.append(Spacer(1, 20))

    ###

    # Cabeceras de la tabla
    info = [["Asignatura", "Grupo", "Teoría", "Subgrupos (S1, S2, S3, S4)", "Desviación"]]

    # Convertir el objeto a filas
    for asignatura, grupos in objeto.items():
        for grupo, recuento in grupos.items():

            # Separa teoría y subgrupos
            if recuento:
                teoria = recuento[0]
                resto = recuento[1:]

            # Vacío
            else:
                teoria = ""
                resto = []

            # Desviación entre subgrupos
            if len(resto) > 1:
                desviacion = round(statistics.stdev([int(x) for x in resto]), 2)
            else:
                desviacion = 0

            # Rellenar
            info.append([asignatura, grupo, str(teoria), ", ".join(map(str, resto)), str(desviacion)])

    ###

    # Crear la tabla
    tabla = Table(info, colWidths=[80, 50, 75, 160, 70])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#11645d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
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
        res[str(clave[0])][str(clave[1])[0]].append(valores["capacidad"])

    ###
    # Segundo Cuatrimestre

    for clave in datos2.keys():
        res[str(clave[0])] = {}

    for clave in datos2.keys():
        res[str(clave[0])][str(clave[1])[0]] = []

    for clave, valores in datos2.items():
        res[str(clave[0])][str(clave[1])[0]].append(valores["capacidad"])

    ###
    # Salida

    ruta = DIR_PATH / ".." / "output" / "repartoAsignaturas.pdf"
    exportPDF(res, str(ruta))
