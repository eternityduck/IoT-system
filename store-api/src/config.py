import os


def try_parse(type, value: str):
    try:
        return type(value)
    except Exception:
        return None


POSTGRES_HOST = os.environ.get("POSTGRES_HOST") or "localhost"
POSTGRES_PORT = try_parse(int, os.environ.get("POSTGRES_PORT")) or 5432
POSTGRES_USER = os.environ.get("POSTGRES_USER") or "admin"
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD") or "admin"
POSTGRES_DB = os.environ.get("POSTGRES_DB") or "stora_db"
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
