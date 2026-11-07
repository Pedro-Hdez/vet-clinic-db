"""Lee el tópico de Kafka y agrega cada mensaje, tal cual, como una línea del crudo.

Cada acción y cada error se anotan en /app/logs/consumer.log."""

import logging
import os
import sys
from pathlib import Path

from confluent_kafka import Consumer, KafkaError

# Log: se escribe en un archivo y también en la consola, para verlo con docker compose logs.
LOG_DIR = Path("/app/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    handlers=[logging.FileHandler(LOG_DIR / "consumer.log"), logging.StreamHandler()],
)
log = logging.getLogger("consumer")

try:
    topic = os.environ["KAFKA_TOPIC"]
    bootstrap_servers = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
except KeyError as e:
    log.error("Falta la variable de entorno %s: revisa tu .env y environment: en docker-compose.yml", e)
    sys.exit(1)

# /app/data es el volumen crudo, que el processor también ve.
raw_file = Path("/app/data/raw") / f"{topic}.log"
raw_file.parent.mkdir(parents=True, exist_ok=True)

consumer = Consumer({
    "bootstrap.servers": bootstrap_servers,
    "group.id": "ingestion",
    "auto.offset.reset": "earliest",
    "allow.auto.create.topics": True,
})
consumer.subscribe([topic])
log.info("Suscrito al tópico %s; el crudo se escribe en %s", topic, raw_file)

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                # Error conocido al iniciar: el consumer se suscribió antes de que existiera el tópico.
                # Con allow.auto.create.topics, Kafka lo crea y el consumer sigue esperando mensajes.
                log.warning("El tópico %s todavía no existe; se crea automáticamente: %s", topic, msg.error())
            else:
                log.error("Kafka reportó un error: %s", msg.error())
            continue
        line = msg.value().decode("utf-8")
        # Modo "a" (append): cada mensaje se agrega al final del archivo, sin borrar lo anterior.
        # Al salir del with se cierra el archivo y la línea queda escrita para el processor.
        with raw_file.open("a", encoding="utf-8") as raw:
            raw.write(line + "\n")
        log.info("Guardado en el crudo (offset %s): %s", msg.offset(), line)
except OSError:
    # Error conocido: no se pudo escribir en el crudo (por ejemplo, el disco está lleno).
    log.exception("No se pudo escribir en el crudo %s; el consumer termina", raw_file)
    sys.exit(1)
except Exception:
    log.exception("Error inesperado; el consumer termina y Docker lo volverá a iniciar")
    sys.exit(1)
