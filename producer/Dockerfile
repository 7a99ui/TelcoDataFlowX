FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip setuptools wheel
RUN pip install --default-timeout=100 -i https://pypi.org/simple kafka-python pandas

CMD ["python", "app.py"]
