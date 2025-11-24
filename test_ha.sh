#!/bin/bash
set -e

# -----------------------
# Configuration
# -----------------------
KAFKA_BROKERS="kafka1:9092,kafka2:9092,kafka3:9092"
TOPIC="demo_topic"
MINIO_NODE="minio1"
MINIO_BUCKET="telco-churn"
NUM_MESSAGES=10

# -----------------------
# 1️⃣ Publier des messages test via le conteneur producer
# -----------------------
echo "📤 Publication de ${NUM_MESSAGES} messages test via producer..."
docker exec producer bash -c "
for i in \$(seq 0 $((NUM_MESSAGES-1))); do
    python3 producer.py --topic $TOPIC --message '{\"test\": \$i}'
    echo 'Message envoyé:' \$i
done
"
echo "✅ Messages publiés via producer."

# -----------------------
# 2️⃣ Consommer les messages via le conteneur consumer
# -----------------------
echo "📥 Consommation des messages via consumer..."
docker exec consumer bash -c "
python3 consumer.py --topic $TOPIC --from-start --max $NUM_MESSAGES
"

# -----------------------
# 3️⃣ Simuler panne d'un broker Kafka
# -----------------------
BROKER_TO_STOP="kafka2"
echo "⚠️ Arrêt temporaire de $BROKER_TO_STOP..."
docker stop $BROKER_TO_STOP
sleep 3

# Publier des messages supplémentaires pendant la panne
echo "📤 Publication de messages supplémentaires pendant la panne..."
docker exec producer bash -c "
for i in \$(seq $NUM_MESSAGES $((NUM_MESSAGES+4))); do
    python3 producer.py --topic $TOPIC --message '{\"test\": \$i}'
    echo 'Message envoyé:' \$i
done
"
echo "✅ Messages publiés pendant la panne."

# Redémarrer le broker
echo "🔄 Redémarrage de $BROKER_TO_STOP..."
docker start $BROKER_TO_STOP
sleep 5

# Consommer tous les messages
echo "📥 Consommation complète après la panne Kafka..."
docker exec consumer bash -c "
python3 consumer.py --topic $TOPIC --from-start --max $((NUM_MESSAGES+5))
"

# -----------------------
# 4️⃣ Simuler panne MinIO
# -----------------------
MINIO_TO_STOP="minio3"
echo "⚠️ Arrêt temporaire de $MINIO_TO_STOP..."
docker stop $MINIO_TO_STOP
sleep 3

# Écrire un fichier test via le conteneur consumer ou producer si upload prévu
echo "📤 Écriture d'un fichier test dans MinIO via $MINIO_NODE..."
docker exec $MINIO_NODE mc alias set local http://minio1:9000 minio minio123
docker exec $MINIO_NODE sh -c "echo 'test file' > /tmp/test_file.txt"
docker exec $MINIO_NODE mc cp /tmp/test_file.txt local/$MINIO_BUCKET/test_file.txt

# Redémarrer le nœud MinIO
echo "🔄 Redémarrage de $MINIO_TO_STOP..."
docker start $MINIO_TO_STOP
sleep 3

# Vérifier la présence du fichier sur MinIO
echo "📂 Vérification du fichier sur MinIO..."
docker exec $MINIO_NODE mc ls local/$MINIO_BUCKET/ | grep "test_file.txt" && echo "✅ Fichier présent."

echo "🎉 Test HA avec conteneurs Dockerisés terminé avec succès !"
