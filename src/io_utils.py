import json, pandas as pd, re
from pathlib import Path
from datetime import date, timedelta


def read_bins_from_excel(path: str, column: str) -> list[str]:
    df = pd.read_excel(path, dtype={column: str})

    if column not in df.columns:
        raise ValueError(f"La columna '{column}' no existe.")

    bins = (df[column].astype(str)
            .apply(lambda s: re.sub(r"\D", "", s))  # sólo dígitos
            .str[:6])

    return sorted({b for b in bins if len(b) == 6 and b.isdigit()})


def read_bins_from_sql(conn, sql_file: str) -> list[str]:
    query = Path(sql_file).read_text(encoding="utf-8")
    today = date.today()
    start = today - timedelta(days=1)
    query = (query
             .replace("{{START_DATE}}", start.strftime("%Y-%m-%d"))
             .replace("{{END_DATE}}", today.strftime("%Y-%m-%d")))

    clean_bins: set[str] = set()
    with conn.cursor() as cur:
        cur.execute(query)
        for row in cur.fetchall():
            if not row or not row[0]:
                continue
            digits = re.sub(r"\D", "", str(row[0]))
            six = digits[:6]
            if len(six) == 6 and six.isdigit():
                clean_bins.add(six)

    return sorted(clean_bins)


def read_bins_from_geopagos(conn, sql_file: str, ftt_db_name: str) -> list[str]:
    """Lee BINs desde la tabla Transaction_Retention_Daily de la base de datos geopagos.
    
    Args:
        conn: Conexión a la base de datos de geopagos
        sql_file: Ruta al archivo SQL con el query
        ftt_db_name: Nombre de la base de datos donde está TempBIN (base de FTT)
    """
    query = Path(sql_file).read_text(encoding="utf-8")
    query = query.replace("{{FTT_DB}}", ftt_db_name)
    
    clean_bins: set[str] = set()
    with conn.cursor() as cur:
        cur.execute(query)
        for row in cur.fetchall():
            if not row or not row[0]:
                continue
            digits = re.sub(r"\D", "", str(row[0]))
            six = digits[:6]
            if len(six) == 6 and six.isdigit():
                clean_bins.add(six)
    
    return sorted(clean_bins)


def dump_json(path: str, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
