import psycopg2

try:
    conn = psycopg2.connect(
        dbname='celucentro11',
        user='postgres',
        password='asbel123',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    print("Base de datos celucentro11 reseteada exitosamente.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error al resetear la base de datos: {e}")
