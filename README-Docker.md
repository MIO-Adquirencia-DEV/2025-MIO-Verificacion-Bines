# Procesar Bines - Docker

## Configuración Rápida

### 1. Crear archivo .env
```bash
# RapidAPI
RAPIDAPI_KEY=tu_rapidapi_key_aqui

# SQL Server (usando el contenedor Docker)
SQLSERVER_SERVER=sqlserver
SQLSERVER_DB=master
SQLSERVER_USER=sa
SQLSERVER_PWD=YourStrong@Passw0rd

# Configuración de ejecución
APP_EXECUTOR=Tu_Nombre
APP_LOG_DIR=./logs
```

### 2. Ejecutar

**Linux/macOS:**
```bash
bash scripts/run-docker.sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-docker.ps1
```

## Configuración Manual

### Solo construir la imagen:
```bash
docker-compose build
```

### Solo iniciar SQL Server:
```bash
docker-compose up -d sqlserver
```

### Ejecutar el procesamiento:
```bash
docker-compose run --rm process-bins
```

## Base de Datos

El contenedor incluye SQL Server Express. Para crear la tabla `TempBIN`, ejecuta:

```sql
CREATE TABLE dbo.TempBIN
(
    Id           INT IDENTITY(1,1) PRIMARY KEY,
    Marca        VARCHAR(50) NULL,
    BIN          INT       NOT NULL UNIQUE,
    TipoProducto VARCHAR(50) NULL,
    Pais         CHAR(2) NULL,
    Region       VARCHAR(30) NULL,
    FechaCreado  DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
```

## Conectar a SQL Server desde el host

- **Servidor:** localhost:1433
- **Usuario:** sa
- **Contraseña:** YourStrong@Passw0rd

## Logs

Los logs se guardan en `./logs/` y se montan como volumen para persistir entre ejecuciones.
