####################
# Funciones auxiliares

# Traduce el código a día de la semana
def translateDia(num):
    num = num[0]

    if num == "1":
        return "Lunes"
    elif num == "2":
        return "Martes"
    elif num == "3":
        return "Miércoles"
    elif num == "4":
        return "Jueves"
    elif num == "5":
        return "Viernes"
    
##########
    
# Traduce el código a hora
def translateHora(num):
    num = num[1:3]

    if num == "01":
        return "08:30"
    elif num == "02":
        return "09:30"
    elif num == "03":
        return "10:30"
    elif num == "04":
        return "11:30"
    elif num == "05":
        return "12:30"
    elif num == "06":
        return "13:30"
    elif num == "08":
        return "15:30"
    elif num == "09":
        return "16:30"
    elif num == "10":
        return "17:30"
    elif num == "11":
        return "18:30"
    elif num == "12":
        return "19:30"
    elif num == "13":
        return "20:30"
    
##########

# Traduce el código a grado
def translateGrado(codigo): # Useless I think
    codigo = codigo[0:3]

    if codigo == "296":
        return "II", "../externos/asignaturasII.ods"
    elif codigo == "221":
        return "IT", "../externos/asignaturasIT.ods"
    elif codigo == "297":
        return "IIM", "../externos/asignaturasIIM.ods"
    elif codigo == "216":
        return "IIADE", "../externos/asignaturasIIADE.ods"
    
    # 270 es de mates
    # 999 es reconocimiento de creditos
    # 230 es caminos
    # en la columna de CEA me puedo encontrar de todo con los erasmus