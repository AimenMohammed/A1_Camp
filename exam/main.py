from fastapi import FastAPI
import psycopg2

app = FastAPI()

conn = psycopg2.connect(
        host="localhost",
        database="weather_db",
        user="postgres",
        password="aimen",
        port=5432
    )
@app.get("/raw")
def raw():
    cur = conn.cursor()
    cur.execute("""
                SELECT * FROM raw_data
                ORDER BY timestamp DESC
                LIMIT 100
                """)
    return cur.fetchall()