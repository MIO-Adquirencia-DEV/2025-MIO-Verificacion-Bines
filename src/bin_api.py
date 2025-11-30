import time, requests

URL  = "https://bin-ip-checker.p.rapidapi.com/"
HOST = "bin-ip-checker.p.rapidapi.com"

def call(bin_value: str, api_key: str, retries=3, backoff=1.5):
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": HOST
    }
    payload = {"bin": bin_value}; params = {"bin": bin_value}
    last = None
    for i in range(1, retries+1):
        try:
            r = requests.post(URL, json=payload, headers=headers, params=params, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last = e; time.sleep(backoff**(i-1))
    raise RuntimeError(f"API sin éxito para BIN {bin_value}: {last}")

def normalize(item: str, data: dict) -> dict:
    if "BIN" not in data or not data["BIN"]:
        raise ValueError("Respuesta API inválida.")
    b = data["BIN"]
    typ = b.get("type")
    if isinstance(typ, list): typ = typ[0] if typ else None
    
    # Tomar la primera letra del tipo y ponerla en mayúscula
    tipo_producto = "C"  # Por defecto
    if typ:
        typ_str = str(typ).strip()
        if typ_str:
            tipo_producto = typ_str[0].upper()  # Primera letra en mayúscula
    
    # Normalizar marca: solo Mastercard en Title Case, los demás en mayúsculas
    marca = b.get("brand")
    if marca:
        marca_str = str(marca).upper()
        if marca_str == "MASTERCARD":
            marca = "Mastercard"
        else:
            marca = marca_str  # Los demás se quedan en mayúsculas
    
    country = (b.get("country") or {}).get("alpha2")
    # Si el país es DO o DOM, es Local, sino Internacional
    region = "Local" if country and country.upper() in ("DO", "DOM") else "Internacional"
    
    return {
        "Marca": marca,
        "BIN": int(item),
        "TipoProducto": tipo_producto,
        "Pais": country,
        "Region": region
    }
