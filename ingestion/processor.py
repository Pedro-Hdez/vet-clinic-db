"""Lo ejecuta cron cada minuto (ver ingestion/crontab): cuenta cuántos mensajes hay en el crudo
y lo anota en su log de monitoreo.

Lo que imprime un programa que ejecuta cron no aparece en ningún lado. Por eso todo, incluidos
los errores, se escribe en /app/logs/processor.log.

Es un ejemplo de cómo se conectan las piezas: no quita duplicados ni filtra, y no escribe en
la base de datos."""

import logging
import os
import sys
from pathlib import Path

# Log: solo a un archivo, porque cron no muestra lo que el programa imprime.
LOG_DIR = Path("/app/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    handlers=[logging.FileHandler(LOG_DIR / "processor.log")],
)
log = logging.getLogger("processor")

try:
    # cron no les pasa a sus trabajos las variables del contenedor. Esta llega porque el command
    # del servicio processor la copia a /etc/environment antes de iniciar cron.
    topic = os.environ["KAFKA_TOPIC"]
except KeyError as e:
    log.error(
        "Falta la variable de entorno %s: revisa que esté en environment: del servicio processor "
        "y que su command la copie a /etc/environment",
        e,
    )
    sys.exit(1)

raw_file = Path("/app/data/raw") / f"{topic}.log"

try:
    if not raw_file.exists():
        # Error conocido: el consumer todavía no ha guardado ningún mensaje.
        log.warning("El crudo %s todavía no existe", raw_file)
    else:
        with raw_file.open(encoding="utf-8") as f:
            total = sum(1 for _ in f)
        log.info("%s: %s mensajes en el crudo", raw_file.name, total)
except Exception:
    log.exception("Error inesperado en la corrida")
    sys.exit(1)
