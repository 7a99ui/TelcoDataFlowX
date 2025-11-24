FROM apache/spark:3.5.7-scala2.12-java17-python3-ubuntu

USER root
RUN apt-get update && \
    apt-get install -y python3-pip wget curl unzip && \
    python3 -m pip install --upgrade pip

# Installer PySpark et Delta Lake Python
RUN pip install --no-cache-dir \
    pyspark==3.5.7 \
    delta-spark==3.2.1 \
    jupyter==1.1.1 \
    notebook==7.5.0 \
    boto3==1.26.0 \
    pandas==2.1.1 \
    pyarrow==12.0.1

# Télécharger les jars Hadoop AWS pour S3A + Delta Lake 3.2.1 (compatible Spark 3.5.x)
RUN mkdir -p /opt/spark/jars && \
    # Hadoop AWS pour MinIO/S3
    wget -O /opt/spark/jars/hadoop-aws-3.3.4.jar \
      https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    wget -O /opt/spark/jars/aws-java-sdk-bundle-1.12.526.jar \
      https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.526/aws-java-sdk-bundle-1.12.526.jar && \
    # Delta Lake 3.2.1 pour Spark 3.5.x
    wget -O /opt/spark/jars/delta-spark_2.12-3.2.1.jar \
      https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.2.1/delta-spark_2.12-3.2.1.jar && \
    wget -O /opt/spark/jars/delta-storage-3.2.1.jar \
      https://repo1.maven.org/maven2/io/delta/delta-storage/3.2.1/delta-storage-3.2.1.jar

# Ajouter les JARs au classpath Spark
ENV SPARK_CLASSPATH="/opt/spark/jars/*"

WORKDIR /opt/workspace
EXPOSE 8888 4040

CMD ["bash", "-c", "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='spark123' --NotebookApp.notebook_dir=/opt/workspace"]