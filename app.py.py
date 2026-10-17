import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector as mysql

app = Flask(__name__)
app.secret_key = "cleaning_system_secret_key"

# Cloud Database Connection configuration helper
def get_db_connection():
    return mysql.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        passwd=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
        port=int(os.environ.get("DB_PORT", 3306))
    )

# Automatically builds the required tables if they do not exist
def init_db():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS customers (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), phone VARCHAR(20), address VARCHAR(255)) AUTO_INCREMENT = 1000")
        cursor.execute("CREATE TABLE IF NOT EXISTS services (id INT AUTO_INCREMENT PRIMARY KEY, cid INT, service_name VARCHAR(255), price FLOAT, date DATE, time VARCHAR(20), FOREIGN KEY (cid) REFERENCES customers(id) ON DELETE CASCADE) AUTO_INCREMENT = 2000")
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print(f"Database setup holding... Check environment configurations: {e}")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = None
    search_type = None
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        query = request.form.get('query')
        
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        if search_type == "name":
            cursor.execute("SELECT * FROM customers WHERE name LIKE %s", (f"%{query}%",))
        elif search_type == "phone":
            cursor.execute("SELECT * FROM customers WHERE phone LIKE %s", (f"%{query}%",))
        else:
            cursor.execute("SELECT * FROM customers WHERE id = %s", (query,))
            
        results = cursor.fetchall()
        cursor.close()
        db.close()
    return render_template('search.html', results=results, search_type=search_type)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == "add_customer":
            name = request.form.get('name')
            phone = request.form.get('phone')
            address = request.form.get('address')
            cursor.execute("INSERT INTO customers (name, phone, address) VALUES (%s, %s, %s)", (name, phone, address))
            db.commit()
            flash("Customer added successfully!")
            
    cursor.execute("SELECT * FROM customers")
    all_customers = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('admin.html', customers=all_customers)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
