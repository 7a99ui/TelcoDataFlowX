#!/bin/bash
set -e

export CLUSTER_ID=f1a2b3c4-5678-90ab-cdef-1234567890ab
echo "CLUSTER_ID défini : $CLUSTER_ID"

echo "🚀 Démarrage de Kafka et MinIO..."
docker-compose up -d kafka1 kafka2 kafka3 minio1 minio2 minio3 minio4

echo ""
echo "⏳ Attente de 60 secondes pour les health checks..."
sleep 60

echo ""
echo "📋 Création du topic 'demo_topic'..."
docker exec kafka1 kafka-topics \
    --bootstrap-server kafka1:9092 \
    --create \
    --topic demo_topic \
    --partitions 3 \
    --replication-factor 3 2>/dev/null || echo "   Topic existe déjà."

echo ""
echo "🚀 Démarrage du producer et du consumer..."
docker-compose up -d producer consumer

echo ""
echo "📊 Statut de tous les services :"
docker-compose ps kafka1 kafka2 kafka3 minio1 minio2 minio3 minio4 producer consumer

echo ""
echo "🎉 Kafka, MinIO, producer et consumer sont prêts !"
