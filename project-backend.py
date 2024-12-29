from flask import Flask, jsonify
import pyodbc
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database configuration (Windows Authentication)
DB_CONFIG = {
    'server': 'localhost\SQLEXPRESS01',  # Replace with your SQL Server name
    'database': 'project_database',  # Replace with your database name
}
CONNECTION_STRING = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"    
    f"SERVER={DB_CONFIG['server']};"
    f"DATABASE={DB_CONFIG['database']};"
    f"Trusted_Connection=yes;"
)
# CONNECTION_STRING="Server=localhost\SQLEXPRESS01;Database=;Trusted_Connection=True;"

def get_db_connection():
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        print("Successfully connected to the database.")
        return conn
    except pyodbc.Error as e:
        print(f"Database connection failed: {e}")
        return None

@app.route('/')
def home():
    # Attempt to connect to the database
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({"message": "Welcome to the Flask App!", "db_status": "Connected to the database."})
    else:
        return jsonify({"message": "Welcome to the Flask App!", "db_status": "Failed to connect to the database."})

@app.route('/employees')
def get_employees():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to the database."}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM EMPLOYEE")  # Adjust table name as needed
        rows = cursor.fetchall()
        employees = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        return jsonify(employees)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({"error": "Failed to fetch data."}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
