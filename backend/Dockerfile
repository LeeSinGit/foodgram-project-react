FROM python:3.9-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libpq-dev gcc netcat-traditional
WORKDIR /app
COPY requirements.txt ./
RUN pip install -U pip && \
    pip install -r requirements.txt --no-cache-dir
COPY . .

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]


CMD ["gunicorn", "foodgram_final.wsgi:application", "--bind", "0.0.0.0:8888"]
