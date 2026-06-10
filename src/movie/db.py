import os

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    connection = psycopg2.connect(
        dbname=os.getenv("DATABASE_DBNAME"),
        host=os.getenv("DATABASE_LOCALHOST"),
        port=os.getenv("DATABASE_PORT"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        cursor_factory=RealDictCursor,
    )

    with connection.cursor() as cursor:
        cursor.execute(f'SET search_path TO {os.getenv("DATABASE_SCHEMA")}')

    return connection