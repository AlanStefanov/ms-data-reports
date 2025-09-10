# Usa una imagen base de Python oficial
FROM python:3.9-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Actualiza las listas de paquetes e instala las dependencias en un solo comando para evitar problemas de caché
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de requerimientos e instálalos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos del proyecto
COPY . .

# Expone el puerto por defecto de Flask
EXPOSE 5000

# Define el comando para ejecutar la aplicación
CMD ["python", "app.py"]
