FROM python:3.10
WORKDIR /app
COPY . .

# Installer kafka-python, pandas et boto3 pour MinIO
RUN pip install --upgrade pip
RUN pip install kafka-python pandas boto3

CMD ["python", "app.py"]
