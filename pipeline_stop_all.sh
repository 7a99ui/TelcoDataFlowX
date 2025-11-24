#!/bin/bash
set -e

echo "🛑 Arrêt de tous les services du pipeline TelcoDataFlow..."

# Arrêter tous les conteneurs définis dans le docker-compose
docker-compose down

echo ""
echo "🧹 Suppression de tous les conteneurs arrêtés liés au projet..."
# Supprimer tous les conteneurs arrêtés (stop + exited)
docker ps -a -q | xargs -r docker rm

echo ""
echo "🧹 Nettoyage des volumes anonymes inutilisés..."
docker volume prune -f

echo ""
echo "📋 Vérification des conteneurs restants..."
docker ps -a

echo ""
echo "✅ Tous les services du pipeline ont été arrêtés et les volumes inutilisés supprimés."
