from kafka import KafkaConsumer
import pandas as pd
import json
import boto3
from io import BytesIO
import time
import os  # pour récupérer la variable d'environnement

# --- Paramètres Kafka ---
TOPIC = "demo_topic"
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 100))  # récupère la valeur depuis l'environnement, défaut 100

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=['kafka1:9092', 'kafka2:9092', 'kafka3:9092'],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="telco_consumer_group",  
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)


# --- Paramètres MinIO ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio1:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "telco-churn")


# Créer le client S3/MinIO
s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY
)

# Créer le bucket si inexistant
try:
    s3.head_bucket(Bucket=MINIO_BUCKET)
except:
    s3.create_bucket(Bucket=MINIO_BUCKET)

batch = []
batch_num = 0

print(f"Consumer prêt, en attente de messages... Batch size = {BATCH_SIZE}")

for msg in consumer:
    batch.append(msg.value)

    if len(batch) >= BATCH_SIZE:
        df_batch = pd.DataFrame(batch)
        batch_num += 1
        # Convertir en CSV dans un buffer mémoire
        csv_buffer = BytesIO()
        df_batch.to_csv(csv_buffer, index=False)
        # Upload vers MinIO
        s3.put_object(
            Bucket=MINIO_BUCKET,
            Key=f"raw/batch_{batch_num}_{int(time.time())}.csv",
            Body=csv_buffer.getvalue()
        )
        print(f"Batch {batch_num} envoyé vers MinIO ({len(batch)} messages)")

        batch = []

# Traiter le reste
if batch:
    df_batch = pd.DataFrame(batch)
    batch_num += 1
    csv_buffer = BytesIO()
    df_batch.to_csv(csv_buffer, index=False)
    s3.put_object(
        Bucket=MINIO_BUCKET,
        Key=f"raw/batch_{batch_num}_{int(time.time())}.csv",
        Body=csv_buffer.getvalue()
    )
    time.sleep(0.1)  # Laisser un petit temps pour MinIO
    print(f"Dernier batch {batch_num} envoyé vers MinIO ({len(batch)} messages)")
