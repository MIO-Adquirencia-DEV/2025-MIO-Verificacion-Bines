import pyodbc
from typing import Iterable, Set, Optional


def get_available_driver() -> Optional[str]:
    """Detecta qué driver ODBC de SQL Server está disponible en el sistema."""
    drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    
    # Orden de preferencia: versiones más recientes primero
    preferred_drivers = [
        'ODBC Driver 18 for SQL Server',
        'ODBC Driver 17 for SQL Server',
        'ODBC Driver 13 for SQL Server',
        'SQL Server Native Client 11.0',
        'SQL Server',
    ]
    
    # Buscar el primer driver preferido que esté disponible
    for preferred in preferred_drivers:
        if preferred in drivers:
            return preferred
    
    # Si no hay ninguno preferido, usar el primero disponible
    if drivers:
        return drivers[0]
    
    return None


def connect(server, db, user, pwd):
    """Conecta a SQL Server. Maneja errores comunes de autenticación y detecta drivers disponibles."""
    driver = get_available_driver()
    
    if not driver:
        available = ', '.join(pyodbc.drivers()) if pyodbc.drivers() else 'ninguno'
        raise RuntimeError(
            f"No se encontró ningún driver ODBC de SQL Server instalado.\n\n"
            f"Drivers disponibles en el sistema: {available}\n\n"
            f"SOLUCIÓN:\n"
            f"1. Descarga e instala 'ODBC Driver for SQL Server' desde:\n"
            f"   https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server\n\n"
            f"2. O instala 'SQL Server Native Client' si usas una versión antigua de SQL Server.\n\n"
            f"3. Reinicia el script después de instalar el driver."
        )
    
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={db};"
        f"UID={user};"
        f"PWD={pwd};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=yes"
    )
    
    try:
        return pyodbc.connect(connection_string)
    except pyodbc.InterfaceError as e:
        error_msg = str(e)
        if "IM002" in error_msg or "No se encuentra el nombre del origen de datos" in error_msg:
            available = ', '.join(pyodbc.drivers()) if pyodbc.drivers() else 'ninguno'
            raise RuntimeError(
                f"Error: No se puede usar el driver '{driver}'.\n\n"
                f"Drivers disponibles: {available}\n\n"
                f"SOLUCIÓN: Instala 'ODBC Driver for SQL Server' desde:\n"
                f"https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server"
            ) from e
        if "Login failed" in error_msg:
            raise RuntimeError(
                f"Error de autenticación con SQL Server.\n"
                f"Servidor: {server}\n"
                f"Base de datos: {db}\n"
                f"Usuario: {user}\n"
                f"Verifica:\n"
                f"  1. Usuario y contraseña correctos en .env\n"
                f"  2. El usuario '{user}' existe en SQL Server\n"
                f"  3. El usuario tiene permisos en la base de datos '{db}'\n"
                f"  4. SQL Server está configurado para autenticación SQL (no solo Windows)\n"
                f"  5. El usuario no está bloqueado o deshabilitado\n"
                f"Error original: {error_msg}"
            ) from e
        raise
    except Exception as e:
        raise RuntimeError(
            f"Error al conectar a SQL Server.\n"
            f"Servidor: {server}\n"
            f"Base de datos: {db}\n"
            f"Usuario: {user}\n"
            f"Driver usado: {driver}\n"
            f"Error: {e}"
        ) from e


def existing_bins(conn, bins: list[str], batch: int = 1000) -> Set[int]:
    sql_base = "SELECT BIN FROM TempBIN WHERE BIN IN ({})"
    s: Set[int] = set()
    with conn.cursor() as cur:
        for i in range(0, len(bins), batch):
            lot = bins[i:i + batch]
            cur.execute(sql_base.format(",".join("?" * len(lot))), lot)
            for r in cur.fetchall():
                try:
                    s.add(int(r[0]))
                except:
                    pass
    return s


def bin_exists(conn, bin_value: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM TempBIN WHERE BIN = ?", bin_value)
        return cur.fetchone()[0] > 0


def insert_bin(conn, row: dict):
    """Inserta un BIN en TempBIN usando la conexión proporcionada."""
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO TempBIN (Marca, BIN, TipoProducto, Pais, Region)
                    VALUES (?, ?, ?, ?, ?)
                    """, row["Marca"], row["BIN"], row["TipoProducto"], row["Pais"], row["Region"])
    conn.commit()
