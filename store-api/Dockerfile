
FROM python:3.11

WORKDIR /app

COPY requirements.txt .

# RUN apt-get update && apt-get --assume-yes install libpq-dev && pip install psycopg2-binary


RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]