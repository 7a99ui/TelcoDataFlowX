#!/bin/bash
set -e

echo "🛑 Arrêt de tous les conteneurs actifs du projet..."
# Arrête tous les conteneurs actifs définis dans le docker-compose du projet
docker-compose stop

echo ""
echo "🚀 Démarrage de MinIO et Spark (Master, Workers, Notebook)..."
docker-compose up -d minio1 minio2 minio3 minio4 spark-master spark-worker1 spark-worker2 spark-notebook

echo ""
echo "⏳ Attente de 30 secondes pour l'initialisation de MinIO et Spark..."
sleep 30

echo ""
echo "📊 Statut des services MinIO et Spark :"
docker-compose ps minio1 minio2 minio3 minio4 spark-master spark-worker1 spark-worker2 spark-notebook

echo ""
echo "🎉 MinIO et Spark sont prêts !"
