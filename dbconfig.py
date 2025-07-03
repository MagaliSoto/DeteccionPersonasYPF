import mysql.connector
import os

def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),  # Variable de entorno DB_HOST, valor por defecto "localhost"
        port=int(os.getenv("DB_PORT", 3306)),    # Puerto por defecto 3306
        user="root",
        password=os.getenv("MYSQL_ROOT_PASSWORD", "Minigo.123"),
        database=os.getenv("MYSQL_DATABASE", "seguridad")
    )

if __name__ == "__main__":
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES;")
    for db in cursor.fetchall():
        print(db)
    conn.close()
