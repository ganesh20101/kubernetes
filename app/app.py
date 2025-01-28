from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# MySQL connection configuration
db_config = {
    'host': 'mysql',
    'user': 'root',
    'password': 'admin123',
    'database': 'user_db'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')

    # Insert into MySQL
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
    except Exception as e:
        return f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

    return f"User {name} with email {email} added successfully!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

