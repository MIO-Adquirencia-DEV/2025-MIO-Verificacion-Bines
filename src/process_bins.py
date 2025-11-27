import argparse, json, logging, os, time
from datetime import datetime
from config import Settings
from io_utils import dump_json, read_bins_from_sql, read_bins_from_excel
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
    p = argparse.ArgumentParser(description="Flujo integral de BINes")
    p.add_argument("--excel", default="./data/1_TransactionsReport.xlsx", help="Ruta al archivo Excel de transacciones")
    p.add_argument("--col", default="Número tarjeta", help="Nombre de la columna con números de tarjeta")
    p.add_argument("--ftt-sql", default="./sql/ftt.sql", help="Ruta al SQL de ftt")
    p.add_argument("--dump_unicos", default="./data/output/valores_unicos.json")
    p.add_argument("--dump_faltantes", default="./data/output/elementos_faltantes.json")
    p.add_argument("--batch_db", type=int, default=1000)
    p.add_argument("--sleep_api", type=float, default=0.0)
    args = p.parse_args()

    setup_logger(Settings.LOG_DIR, Settings.EXECUTOR)
    conn = connect(Settings.SQL_SERVER, Settings.SQL_DB, Settings.SQL_USER, Settings.SQL_PWD)

    try:
        # 1) Obtener BINes desde ambas fuentes
        bins_geopagos = read_bins_from_excel(args.excel, args.col)  # lista de str
        bins_ftt = read_bins_from_sql(conn, args.ftt_sql)  # lista de str

        # 2) Unificar, deduplicar y ordenar
        bins = sorted(set(bins_geopagos) | set(bins_ftt))
        dump_json(args.dump_unicos, [{"primeros_6_caracteres": b} for b in bins])
        logging.info(f"BINs únicos (excel + ftt): {len(bins)}")

        # 3) Verificar existentes y calcular faltantes
        existentes = existing_bins(conn, bins, args.batch_db)  # set de int
        faltantes = [b for b in bins if int(b) not in existentes]
        dump_json(args.dump_faltantes, faltantes)
        logging.info(f"BINs faltantes: {len(faltantes)}")

        # 4) Consultar API e insertar
        ok = sk = err = 0
        for i, b in enumerate(faltantes, 1):
            if bin_exists(conn, b):
                sk += 1
                logging.info(f"[{i}/{len(faltantes)}] BIN {b} ya existe (omitido).")
                continue
            try:
                # Temporarily commented to avoid consuming RapidAPI credits while validando el flujo.
                # data = call(b, Settings.RAPIDAPI_KEY)
                # row = normalize(b, data)
                # insert_bin(conn, row)
                logging.info(f"[{i}/{len(faltantes)}] BIN {b} API omitida (validación).")
            except Exception as e:
                err += 1
                logging.error(f"[{i}/{len(faltantes)}] BIN {b} error: {e}")
            if args.sleep_api > 0:
                time.sleep(args.sleep_api)

        logging.info(f"RESUMEN | Insertados: {ok} | Omitidos: {sk} | Errores: {err}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
