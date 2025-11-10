# Iniciar entorno virtual

```bash
python3 -m venv venv
```

# Activar entorno virtual

- Linux:

```bash
source venv/bin/activate
```
- Windows (Powershell)

```powershell
venv\Scripts\activate
```

## Excepciones (Windows)

- Si durante cualquier paso del proceso, en cuanto a la terminal, da error de dependencias, ejecutar **python.exe** en lugar de **python3**.

- Si powershell indica que no es posible la ejecución de código ya que no tenemos permisos, podemos ejecutar el siguiente comando para permitirlos temporalmente en la sesión que tenemos activa:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- Las rutas en Windows se indican con la barra invertida "\\", en lugar de la normal "/".

# Instalar dependencias

```bash
pip install -r requirements.txt
```

# Ejecutar
```bash
python3 src/main.py
```

## Consultar horario de un alumno
```bash
python3 src/consultaAlumno.py <dni>
```
- Este script puede recibirá un identificador de un alumno, en este caso el DNI, y devolverá un PDF con el horario. La entrada puede darse como un parámetro de ejecución o si no se especifica, se pedirá dentro del script una vez iniciada su ejecución.