# TelcoDataFlow
Distributed Telco data architecture with streaming ingestion (Kafka), data lakehouse storage (Delta Lake on MinIO), ML processing (Spark ML), SQL query engine (Presto/Trino), and interactive dashboards (Superset).

---

## Prérequis
Pour faire fonctionner le projet, certains fichiers JAR volumineux sont nécessaires pour Hadoop et AWS. Ils **ne sont pas inclus dans le dépôt** en raison de leur taille (>100 Mo).

Téléchargez les fichiers suivants et placez-les dans le dossier `jars/` :

- `aws-java-sdk-bundle-1.12.406.jar` depuis [AWS SDK](https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.406/aws-java-sdk-bundle-1.12.406.jar)
- `aws-java-sdk-bundle-1.12.301.jar` depuis [AWS SDK](https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.301/aws-java-sdk-bundle-1.12.301.jar)
- `hadoop-aws-3.3.6.jar` depuis [Maven Repository](https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-aws/3.3.6)
- `hadoop-common-3.3.6.jar` depuis [Maven Repository](https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-common/3.3.6)

> **Note** : Assurez-vous que le dossier `jars/` existe à la racine du projet avant de placer ces fichiers.

---

## Installation et exécution

### 1. Préparer le Docker / Spark
Si vous utilisez Docker, le Dockerfile est déjà configuré pour utiliser les JAR présents dans `jars/`.

### 2. Notebooks
Les notebooks Spark (ex. `MinIo_deltaLake.ipynb`) s’attendent à trouver ces JAR dans le dossier `jars/`.

---

## Structure du projet
