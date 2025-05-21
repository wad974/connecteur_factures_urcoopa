# Utiliser Ubuntu 22.04 comme base
FROM ubuntu:22.04

# Définition des variables d'environnement
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TZ=Indian/Reunion

# Mise à jour et installation des dépendances nécessaires
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        curl \
        tzdata \
        python3 \
        python3-pip \
        nano \
        gcc \
        cron \
        build-essential \
        supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Définition du fuseau horaire
RUN ln -fs /usr/share/zoneinfo/Indian/Reunion /etc/localtime

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers dans le conteneur
ADD . /app/

# Copier les fichiers applicatifs
COPY main.py requirements.txt server.crt server.key ./

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Localtime
RUN rm /etc/localtime

# Localtime Runtime Reunion
RUN ln -s /usr/share/zoneinfo/Indian/Reunion /etc/localtime

# Copie du fichier Supervisord.conf
#COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Configuration CRON
COPY moncrontab /etc/cron.d/moncrontab
RUN chmod 0644 /etc/cron.d/moncrontab && \
    crontab /etc/cron.d/moncrontab && \
    touch /var/log/cron.log

# Exposition des ports
EXPOSE 9898

# Démarrer Supervisord pour gérer plusieurs processus
#CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
# Lancer Uvicorn avec SSL
# Lancement de Uvicorn + Cron via supervisord
CMD service cron start && \
    uvicorn main:app --host 0.0.0.0 --port 9898
    #uvicorn main:app --host 0.0.0.0 --port 9898 --ssl-keyfile=server.key --ssl-certfile=server.crt

# Commande de lancement (le script Python lance Uvicorn avec SSL)
#CMD ["python3", "main.py"]
