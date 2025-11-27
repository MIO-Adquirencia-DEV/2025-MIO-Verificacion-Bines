# Proyecto BINES

## Descripción
Este proyecto procesa transacciones de distintos orígenes (**Adquirencia** y **FTT**) para **extraer BINs (primeros 6 dígitos de tarjetas)**, verificar cuáles ya existen en la base de datos SQL Server y completar los faltantes consultando la **API de BIN Lookup (RapidAPI)**.  
La información obtenida se inserta en la tabla `TempBIN`.

---

## Estructura del proyecto

```
BINES/
├─ src/
│  ├─ process_bins.py          # Punto de entrada: orquesta todo el flujo
│  ├─ bin_api.py               # Cliente de la API (RapidAPI)
│  ├─ db.py                    # Conexión y operaciones a SQL Server
│  ├─ io_utils.py              # Lectura de SQL y utilidades
│  └─ config.py                # Configuración y variables de entorno
│
├─ data/
│  └─ output/                  # Artefactos generados
│     ├─ valores_unicos.json
│     └─ elementos_faltantes.json
│
├─ logs/                       # Un archivo de log por día
│
├─ scripts/
│  ├─ run.sh                   # Script de ejecución en Linux/macOS
│  └─ run.ps1                  # Script de ejecución en Windows
│
├─ .env.example                # Variables de entorno de ejemplo
├─ requirements.txt            # Dependencias del proyecto
├─ README.md                   # Este archivo
└─ sql/
   └─ ftt.sql                   # Consulta para BINs de ftt
```

---

## Requisitos

- Python 3.10+
- SQL Server accesible
- Cuenta en RapidAPI con acceso al endpoint `bin-ip-checker`

---

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto a partir de `.env.example`:

```env
# RapidAPI
RAPIDAPI_KEY=coloca_tu_key

# SQL Server
SQLSERVER_SERVER=
SQLSERVER_DB=
SQLSERVER_USER=
SQLSERVER_PWD=

# Configuración de ejecución
APP_EXECUTOR=Nombre_Apellido
APP_LOG_DIR=./logs
```

---

## Instalación

```bash
# Clonar repositorio
git clone <url-del-repo>
cd BINES

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# .venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

---

## Ejecución

### En Linux/macOS
```bash
bash scripts/run.sh
```

### En Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1
```

---

---

## Logs

- Todos los procesos registran sus acciones en `./logs/app-YYYY-MM-DD.log`.
- El nombre del ejecutor se toma de la variable de entorno `APP_EXECUTOR`.
- Se registran:
    - Cantidad de BINs procesados
    - BINs insertados, omitidos y con error
    - Errores de conexión o de API

---

## Flujo resumido

1. Ejecuta las consultas SQL (`adquirencia.sql` y `ftt.sql`).
2. Extrae los BINs (primeros 6 dígitos de la tarjeta).
3. Guarda los BINs únicos en `valores_unicos.json`.
4. Verifica cuáles BINs ya existen en SQL Server.
5. Guarda los faltantes en `elementos_faltantes.json`.
6. Consulta la API de RapidAPI por cada BIN faltante.
7. Inserta la información en la tabla `TempBIN`.
8. Genera logs diarios con el detalle del proceso.

---
