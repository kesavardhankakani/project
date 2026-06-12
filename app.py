from flask import Flask
import psycopg2

app =Flask(__name__)

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "kesava"

def get_db_connection():
    return psycopg2.connect(
        host = DB_HOST,
        database = DB_NAME,
        user = DB_USER,
        password = DB_PASSWORD
    )

def create_stu_table():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
                create table  IF NOT EXISTS stu_table(
                stu_id SERIAL PRIMARY KEY,
                stu_name TEXT NOT NULL,
                stu_roll TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE
                );
""")
    connection.commit()
    cur.close()
    connection.close()

create_stu_table()

if __name__ == "__main__":
        app.run(debug=True)