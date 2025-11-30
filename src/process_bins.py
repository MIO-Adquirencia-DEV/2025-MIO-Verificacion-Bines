import json, logging, os, time
from datetime import datetime
from pathlib import Path
from config import Settings
from io_utils import dump_json, read_bins_from_sql, read_bins_from_geopagos
from db import connect, existing_bins, bin_exists, insert_bin
from bin_api import call, normalize


def setup_logger(log_dir: str, executor: str):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"app-{datetime.now():%Y-%m-%d}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"),
                  logging.StreamHandler()]
    )
    logging.info(f"Executor: {executor}")


def main():
    # Obtener el directorio base del proyecto (dos niveles arriba de src/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Configuración fija del proceso (rutas relativas al proyecto)
    ftt_sql = project_root / "sql" / "ftt.sql"
    geopagos_sql = project_root / "sql" / "geopagos.sql"
    dump_unicos = project_root / "data" / "output" / "valores_unicos.json"
    dump_faltantes = project_root / "data" / "output" / "elementos_faltantes.json"
    batch_db = 1000
    sleep_api = 0.0
    
    # Crear directorio de output si no existe
    dump_unicos.parent.mkdir(parents=True, exist_ok=True)

    # Asegurar que LOG_DIR sea relativo al proyecto si es relativo
    log_dir = Settings.LOG_DIR
    if not os.path.isabs(log_dir):
        log_dir = str(project_root / log_dir)
    
    setup_logger(log_dir, Settings.EXECUTOR)
    
    # Conexión principal (para ftt y TempBIN)
    conn = connect(Settings.SQL_SERVER, Settings.SQL_DB, Settings.SQL_USER, Settings.SQL_PWD)
    
    # Conexión a geopagos (base de datos diferente)
    conn_geopagos = connect(Settings.SQL_SERVER, Settings.GEOPAGOS_DB, Settings.SQL_USER, Settings.SQL_PWD)

    try:
        # 1) Obtener BINes desde ambas fuentes
        bins_geopagos = read_bins_from_geopagos(conn_geopagos, str(geopagos_sql), Settings.SQL_DB)  # lista de str
        bins_ftt = read_bins_from_sql(conn, str(ftt_sql))  # lista de str

        # 2) Unificar, deduplicar y ordenar
        bins = sorted(set(bins_geopagos) | set(bins_ftt))
        dump_json(str(dump_unicos), [{"primeros_6_caracteres": b} for b in bins])
        logging.info(f"BINs únicos (geopagos + ftt): {len(bins)}")

        # 3) Verificar existentes y calcular faltantes
        existentes = existing_bins(conn, bins, batch_db)  # set de int
        faltantes = [b for b in bins if int(b) not in existentes]
        dump_json(str(dump_faltantes), faltantes)
        logging.info(f"BINs faltantes: {len(faltantes)}")

        # 4) Consultar API e insertar
        ok = sk = err = 0
        for i, b in enumerate(faltantes, 1):
            if bin_exists(conn, b):
                sk += 1
                logging.info(f"[{i}/{len(faltantes)}] BIN {b} ya existe (omitido).")
                continue
            try:
                data = call(b, Settings.RAPIDAPI_KEY)
                row = normalize(b, data)
                insert_bin(conn_geopagos, row)
                ok += 1
                logging.info(f"[{i}/{len(faltantes)}] BIN {b} insertado.")
            except Exception as e:
                err += 1
                logging.error(f"[{i}/{len(faltantes)}] BIN {b} error: {e}")
            if sleep_api > 0:
                time.sleep(sleep_api)

        logging.info(f"RESUMEN | Insertados: {ok} | Omitidos: {sk} | Errores: {err}")

    finally:
        conn.close()
        conn_geopagos.close()


if __name__ == "__main__":
    main()
