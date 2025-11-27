import json, pandas as pd, re
from pathlib import Path


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

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        bins = [str(r[0]) for r in rows if r and r[0]]

    bins = [b for b in bins if len(b) == 6 and b.isdigit()]
    return sorted(set(bins))


def dump_json(path: str, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
