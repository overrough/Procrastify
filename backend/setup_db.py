import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DATABASE', 'procrastify')
    port = int(os.environ.get('MYSQL_PORT', 3306))
    print(f"Connecting to {host}...")
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        cursor.close()
        conn.close()
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        cursor = conn.cursor()
        print(f"Connected to database '{database}'. Reading schema.sql...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(base_dir, 'database', 'schema.sql')
        with open(schema_path, 'r') as f:
            sql_script = f.read()
        print("Executing schema script...")
        results = cursor.execute(sql_script, multi=True)
        for result in results:
            if result.with_rows:
                result.fetchall()
        conn.commit()
        print("✅ Success! All database tables are created.")
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_database()
