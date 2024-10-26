from flask import Flask, request, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)

# Create a SQLite database connection
conn = sqlite3.connect('mod09_data.db', check_same_thread=False)
c = conn.cursor()

# Create a table to store the data if not exists
c.execute('''CREATE TABLE IF NOT EXISTS userdata
             (Name TEXT, Age INTEGER, City TEXT)''')
conn.commit()

# Define a POST endpoint to add data to the database
@app.route('/api/add_data', methods=['POST'])
def add_data():
    # Get the data from the request body
    data = request.json
    
    # Insert the data into the database
    c.execute("INSERT INTO userdata (Name, Age, City) VALUES (?, ?, ?)", (data['Name'], data['Age'], data['City']))
    conn.commit()

    # Return a success message
    response = {
        'message': 'Data added successfully'
    }
    return jsonify(response)

# Define a GET endpoint to retrieve all data from the database
@app.route('/api/get_data', methods=['GET'])
def get_data():
    # Retrieve data from the database
    c.execute("SELECT * FROM userdata")
    rows = c.fetchall()
    data = [{'Name': row[0], 'Age': row[1], 'City': row[2]} for row in rows]
    return jsonify(data)

if __name__ == '__main__':
    port = 8001
    app.run(debug=True, port=port)



