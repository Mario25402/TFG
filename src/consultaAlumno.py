import sys
import argparse
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, PageBreak

########################################
# Rutas de los archivos

DIR_PATH = Path(__file__).parent.resolve()

PRIMERCUATRI = DIR_PATH / ".." / "output" / "alumnosAsignados1.txt"
SEGUNDOCUATRI = DIR_PATH / ".." / "output" / "alumnosAsignados2.txt"

###
# Convierte el texto en información estructurada

def procesarTexto(ruta):
    datos = {}
    dni_actual = None
    
    with open(ruta, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:  # Vacío
                continue
            
            # DNI
            if linea.endswith(":"):
                dni_actual = linea[:-1]  # quitar los dos puntos
                datos[dni_actual] = []

            # Resto
            else:
                # Dividir en partes
                partes = linea.split(" - ")
                abrv = partes[0]  # Asignatura
                grupo = partes[1] # Grupo

                if len(partes) > 2:
                    partes[2] = partes[2].replace("[", "").replace("]", "")
                    horas = partes[2].split(",")  # Convertir a lista
                    horas = [int(h.strip()) for h in horas]  # Pasar a int

                else:
                    horas = []

                # Guardar objeto
                datos[dni_actual].append({
                    "asignatura": abrv,
                    "grupo": grupo,
                    "horas": horas
                })
    
    return datos

###

def exportPDF(primerCuatri, segundoCuatri, alumno, ruta="salida.pdf"):
    # Crear documento
    doc = SimpleDocTemplate(ruta, pagesize=landscape(letter))
    contenido = []

    ###
    # Titulo principal
    
    titulo = Paragraph(f"Horario de {alumno}", getSampleStyleSheet()["Title"])
    contenido.append(titulo)
    contenido.append(Spacer(1, 20))

    ###
    # Función común para rellenar las tablas

    def crearTabla(asignaturas, tituloTabla):
        subtitulo = Paragraph(tituloTabla, getSampleStyleSheet()["Heading2"])
        contenido.append(subtitulo)
        contenido.append(Spacer(1, 12))

        ###
        # Filas y Columnas

        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        franjaHoras = [
            "08:30 - 09:30", "09:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
            "12:30 - 13:30", "13:30 - 14:30", "14:30 - 15:30", "15:30 - 16:30",
            "16:30 - 17:30", "17:30 - 18:30", "18:30 - 19:30", "19:30 - 20:30",
            "20:30 - 21:30"
        ]

        ###
        # Rellenar solo las franjas que tienen contenido

        horasOcupadas = []
        for asignatura in asignaturas:
            for h in asignatura["horas"]:
                horasOcupadas.append(h % 100) # últimos digitos

        if horasOcupadas:
            minHora = min(horasOcupadas)
            maxHora = max(horasOcupadas)

            if maxHora <= 6:  # Solo mañana
                rango = range(1, 7)
            elif minHora >= 8:  # Solo tarde
                rango = range(8, 14)
            else:  # Ambas
                rango = range(1, 14)
        else:
            rango = range(1, 14)  # Vacío

        ###
        # Crear tabla vacía
        
        horario = [["Hora"] + dias]
        for index in rango:
            horario.append([franjaHoras[index-1]] + [""] * 5)

        ###
        # Rellenar celdas
        for asignatura in asignaturas:
            nombre = asignatura["asignatura"]
            grupo = asignatura["grupo"]
            texto = f"{nombre} - {grupo}"

            # Separar día y hora
            for diaHora in asignatura["horas"]:
                dia = int(str(diaHora)[0]) - 1 # Desfase con celdas
                hora = (diaHora % 100)

                if hora in rango and 0 <= dia < 5:
                    fila = list(rango).index(hora) + 1 # Desfase con cabecera

                    # Solapadas
                    if horario[fila][dia+1]:
                        horario[fila][dia+1] += f"\n{texto}"

                    else:
                        horario[fila][dia+1] = texto

        ###
        # Estilo

        tabla = Table(horario, colWidths=[120, 120, 120, 120, 120, 120])
        estilo = [
            # Común
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            # Columna Horas
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#666666")),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.white),

            # Fila Días
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#11645d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ]

        # Hora de Comer
        if 7 in rango:
            filaComer = list(rango).index(7) + 1
            estilo.append(("BACKGROUND", (0, filaComer), (-1, filaComer), colors.lightgrey))

        tabla.setStyle(TableStyle(estilo))
        contenido.append(tabla)
        contenido.append(Spacer(1, 20))

    ###
    # Crear tablas para ambos cuatrimestres

    if primerCuatri:
        crearTabla(primerCuatri, "Primer Cuatrimestre")

    if primerCuatri and segundoCuatri:
        contenido.append(PageBreak())

    if segundoCuatri:
        crearTabla(segundoCuatri, "Segundo Cuatrimestre")

    ###
    # Generar PDF

    doc.build(contenido)

########################################
# Procesamiento

datos1 = procesarTexto(PRIMERCUATRI)
datos2 = procesarTexto(SEGUNDOCUATRI)

###
# Entrada

parser = argparse.ArgumentParser(description="Argumento con entrada manual si falta")
parser.add_argument("id", nargs="?", help="DNI del usuario")
args = parser.parse_args()

if not args.id:
	args.id = input("Por favor, ingresa tu nombre: ")

###
# Salida

ruta = DIR_PATH / ".." / "output" / "alumnos" / f"{args.id}.pdf"

if not args.id in datos1.keys() and not args.id in datos2.keys():
	print("\nClave erronea. Cancelando ejecución.")
	sys.exit(1)	
else:
	exportPDF(datos1[args.id], datos2[args.id], args.id, str(ruta))

