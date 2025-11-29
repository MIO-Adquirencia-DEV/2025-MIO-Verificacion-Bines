import os
from dotenv import load_dotenv
load_dotenv()

def env(name: str, required=True, default=""):
    v = os.getenv(name, default)
    if required and not v:
        raise RuntimeError(f"Falta variable de entorno: {name}")
    return v

class Settings:
    RAPIDAPI_KEY   = env("RAPIDAPI_KEY")
    SQL_SERVER     = env("SQLSERVER_SERVER")
    SQL_DB         = env("SQLSERVER_DB")
    SQL_USER       = env("SQLSERVER_USER")
    SQL_PWD        = env("SQLSERVER_PWD")
    GEOPAGOS_DB    = env("GEOPAGOS_DB")  # Base de datos de geopagos (diferente a SQL_DB)
    LOG_DIR        = env("APP_LOG_DIR", required=False, default="./logs")
    EXECUTOR       = env("APP_EXECUTOR", required=False, default="desconocido")
