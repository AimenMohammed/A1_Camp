import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="weather_db",
        user="postgres",
        password="aimen",
        port=5432
    )