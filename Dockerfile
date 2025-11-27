# Usar imagen base de Python
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para pyodbc y SQL Server
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Microsoft ODBC Driver for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/
COPY sql/ ./sql/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Crear directorios necesarios
RUN mkdir -p logs data/output

# Establecer variables de entorno por defecto
ENV APP_EXECUTOR=Docker_User
ENV APP_LOG_DIR=./logs

# Comando por defecto
CMD ["python", "src/process_bins.py", "--help"]
