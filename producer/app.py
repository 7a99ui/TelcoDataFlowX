from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import pandas as pd
import json
import time
import sys

# Configuration
KAFKA_BROKERS = ['kafka1:9092', 'kafka2:9092', 'kafka3:9092']
TOPIC = "demo_topic"
MAX_RETRIES = 10
RETRY_DELAY = 5

def create_producer_with_retry():
    """Crée un producteur Kafka avec retry automatique"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"🔄 Tentative de connexion à Kafka ({attempt}/{MAX_RETRIES})...")
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks='all',
                retries=5,
                linger_ms=10,
                batch_size=32768,
                request_timeout_ms=30000,
                api_version_auto_timeout_ms=10000
            )
            print("✅ Connexion à Kafka établie avec succès!")
            return producer
        except NoBrokersAvailable:
            print(f"⚠️  Kafka non disponible, nouvelle tentative dans {RETRY_DELAY}s...")
            if attempt == MAX_RETRIES:
                print("❌ Impossible de se connecter à Kafka après plusieurs tentatives")
                sys.exit(1)
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            sys.exit(1)

# Créer le producteur avec retry
producer = create_producer_with_retry()

# Chargement du dataset
print("📂 Chargement du dataset...")
df = pd.read_csv("data/dataset.csv")
print(f"📊 {len(df)} lignes à envoyer")

# Envoi des messages
print(f"📤 Envoi des messages vers le topic '{TOPIC}'...")
sent_count = 0

for idx, row in df.iterrows():
    msg = row.to_dict()
    try:
        producer.send(TOPIC, msg)
        sent_count += 1
        if sent_count % 100 == 0:
            print(f"   ✓ {sent_count}/{len(df)} messages envoyés")
        time.sleep(0.1)
    except Exception as e:
        print(f"⚠️  Erreur lors de l'envoi du message {idx}: {e}")

producer.flush()
print(f"✅ {sent_count} messages envoyés avec succès!")
print("🏁 Producer terminé")
