"""Simula la recepción de la clínica: cada INTERVAL_SECONDS segundos llega una mascota,
y se publica en Kafka un mensaje con su llegada.

Cada acción y cada error se anotan en /app/logs/producer.log."""

import json
import logging
import os
import random
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from confluent_kafka import Producer

# Log: se escribe en un archivo y también en la consola, para verlo con docker compose logs.
LOG_DIR = Path("/app/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    handlers=[logging.FileHandler(LOG_DIR / "producer.log"), logging.StreamHandler()],
)
log = logging.getLogger("producer")


def read_pet_ids():
    """Lee de PostgreSQL los IDs de las mascotas que existen."""
    with psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    ) as conn:
        return [row[0] for row in conn.execute("SELECT pet_id FROM pets ORDER BY pet_id").fetchall()]


def report(err, msg):
    """Kafka llama a esta función cuando confirma, o no, que guardó un mensaje."""
    value = msg.value().decode("utf-8")
    if err is not None:
        log.error("Kafka no guardó el mensaje %s: %s", value, err)
    else:
        log.info("Enviado: %s", value)


# Al iniciar: configuración y mascotas.
try:
    topic = os.environ["KAFKA_TOPIC"]
    interval = float(os.environ["INTERVAL_SECONDS"])
    producer = Producer({"bootstrap.servers": os.environ["KAFKA_BOOTSTRAP_SERVERS"]})
    pet_ids = read_pet_ids()
except KeyError as e:
    log.error("Falta la variable de entorno %s: revisa tu .env y environment: en docker-compose.yml", e)
    sys.exit(1)
except psycopg.OperationalError as e:
    # Error conocido al iniciar: PostgreSQL todavía no acepta conexiones.
    # El programa termina con error y Docker lo vuelve a iniciar (restart: on-failure).
    log.error("No se pudo conectar a PostgreSQL; Docker volverá a iniciar el producer: %s", e)
    sys.exit(1)
except Exception:
    log.exception("Error inesperado al iniciar")
    sys.exit(1)

if not pet_ids:
    log.error("La tabla pets está vacía: no hay mascotas para simular llegadas")
    sys.exit(1)
log.info("Mascotas registradas: %s", pet_ids)

# Una llegada cada INTERVAL_SECONDS segundos.
try:
    while True:
        message = {
            "event_id": str(uuid.uuid4()),
            "pet_id": random.choice(pet_ids),
            "arrived_at": datetime.now(timezone.utc).isoformat(),
        }
        producer.produce(topic, value=json.dumps(message), on_delivery=report)
        producer.flush()
        time.sleep(interval)
except Exception:
    log.exception("Error inesperado; el producer termina y Docker lo volverá a iniciar")
    sys.exit(1)
