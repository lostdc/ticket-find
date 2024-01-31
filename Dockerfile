# Utiliza una imagen oficial de Python como imagen padre.
FROM python:3.10.0

# Establece el directorio de trabajo en el contenedor.
WORKDIR /usr/src/app

# Instala las dependencias necesarias para Google Chrome y Chromedriver.
RUN apt-get update && apt-get install -y gnupg2 wget unzip cron && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y google-chrome-stable

# Instala ChromeDriver versión 121.
RUN wget -N https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chromedriver-linux64.zip -P ~/ && \
    unzip ~/chromedriver-linux64.zip -d ~/ && \
    rm ~/chromedriver-linux64.zip && \
    mv -f ~/chromedriver-linux64/chromedriver /usr/local/share/ && \
    chmod +x /usr/local/share/chromedriver && \
    ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver

# Copia los archivos requerimientos.txt en el contenedor en /usr/src/app.
COPY requerimientos.txt ./

# Instala las dependencias del proyecto.
RUN pip install --no-cache-dir -r requerimientos.txt

# Copia el resto del código fuente en el contenedor.
COPY . .

# Crea un archivo de servidor de health check básico llamado health_check.py.
RUN echo 'from http.server import BaseHTTPRequestHandler, HTTPServer\n\n\
class Handler(BaseHTTPRequestHandler):\n\
    def do_GET(self):\n\
        self.send_response(200)\n\
        self.end_headers()\n\
        self.wfile.write(b"OK")\n\n\
httpd = HTTPServer(("", 8080), Handler)\n\
httpd.serve_forever()' > health_check.py

# Expone el puerto 8080 para el health check.
EXPOSE 8080

# Crea un script de shell para ejecutar tu script Python.
RUN echo '#!/bin/sh\npython3 /usr/src/app/ticketplus_prod.py' > /usr/src/app/run_script.sh
RUN chmod +x /usr/src/app/run_script.sh

# Añade el trabajo cron
RUN echo "0 2 * * * /usr/src/app/run_script.sh >> /var/log/cron.log 2>&1" | crontab -

# Inicia cron y el servidor de health check.
CMD cron && python ./health_check.py
