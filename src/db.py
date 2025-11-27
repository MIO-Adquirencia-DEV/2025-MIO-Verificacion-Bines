import pyodbc
from typing import Iterable, Set


def connect(server, db, user, pwd):
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={db};UID={user};PWD={pwd};TrustServerCertificate=yes"
    )


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
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO TempBIN (Marca, BIN, TipoProducto, Pais, Region)
                    VALUES (?, ?, ?, ?, ?)
                    """, row["Marca"], row["BIN"], row["TipoProducto"], row["Pais"], row["Region"])
    conn.commit()
