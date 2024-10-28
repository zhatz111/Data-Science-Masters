# Import necessary libraries
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import psycopg2

# Initialize a Flask application
app = Flask(__name__)

# In-memory dictionary to store scraped topic data
topics_data = {}

# Database connection parameters
DB_NAME = "jhu"
DB_USER = "jhu"
DB_PASS = "jhu123"
DB_HOST = "localhost"
DB_PORT = "5432"

# Attempt to connect to the PostgreSQL database
try:
    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    print("Database connected successfully")
except Exception as e:
    print("Database not connected successfully")

# Generate a cursor for executing SQL commands on the database
cur = conn.cursor()

# SQL command to create a schema and table for storing Wikipedia topic data
cur.execute(
    """
    CREATE SCHEMA IF NOT EXISTS wiki;

    CREATE TABLE IF NOT EXISTS wiki.topics (
        topic TEXT NOT NULL,
        title TEXT,
        content TEXT,
        num_links INTEGER
    );
"""
)

# Commit the schema and table creation to the database
conn.commit()
print("Table Created successfully")

# Route to check stored topic data in memory
@app.route("/api/check_data", methods=["GET"])
def check_data():
    return jsonify(topics_data)

# Route to scrape a Wikipedia topic based on a POST request
@app.route("/api/scrape_wikipedia", methods=["POST"])
def scrape_wikipedia():
    # Get JSON data from the request
    data = request.get_json()

    # Extract the topic name from the JSON object
    topic = data.get("topic")

    # Return an error if the topic is not provided
    if not topic:
        return jsonify({"error": "Topic not provided"}), 400

    # Build the Wikipedia URL for the given topic
    url = f"https://en.wikipedia.org/wiki/{topic}"

    try:
        # Send a GET request to the Wikipedia page
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code != 200:
            return jsonify({"error": "Failed to retrieve the page"}), 400

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract the page title, first paragraph, and link count
        page_title = soup.find("title").text
        first_paragraph = soup.find("p").text.strip()[0:100]
        num_links = len(soup.find_all("a"))

        # Store the scraped data in the dictionary
        scraped_topic = {
            "title": page_title,
            "content": first_paragraph,
            "num_links": num_links,
        }
        topics_data[topic] = scraped_topic

        # Return the scraped data as JSON
        return jsonify(scraped_topic)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to delete a topic from memory
@app.route("/api/delete_topic", methods=["DELETE"])
def delete_topic():
    # Get JSON data from the request
    data = request.get_json()

    # Extract the topic from the JSON object
    topic = data.get("topic")

    # Return an error if the topic is not provided
    if not topic:
        return jsonify({"error": "Topic not provided"}), 400

    # Check if the topic exists in memory, delete if found
    if topic in topics_data:
        del topics_data[topic]
        return jsonify({"message": f'Topic "{topic}" deleted successfully'}), 200
    else:
        return jsonify({"error": "Topic not found"}), 404

# Route to update topic data in memory
@app.route("/api/update_topic", methods=["PUT"])
def update_topic():
    # Get JSON data from the request
    data = request.get_json()

    # Extract the topic name from the JSON object
    topic = data.get("topic")

    # Return an error if the topic is not provided
    if not topic:
        return jsonify({"error": "Topic not provided"}), 400

    # Update topic data if it exists in memory
    if topic in topics_data:
        for key, _ in data.items():
            if key != "topic":
                topics_data[topic][key] = data[key]
        return jsonify({"message": f'Topic "{topic}" updated successfully'}), 200
    else:
        return jsonify({"error": "Topic not found"}), 404

# Route to insert in-memory topic data into the PostgreSQL database
@app.route("/api/add_data", methods=["POST"])
def add_data():
    try:
        # Loop through topics and insert them into the database
        for key, value in topics_data.items():
            cur.execute(
                """
                INSERT INTO wiki.topics (topic, title, content, num_links) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT DO NOTHING
                """,
                (key, value["title"], value["content"], value["num_links"]),
            )

        # Commit the insertion to the database
        conn.commit()
        print("Data Loaded successfully")
        return jsonify({"message": "Data loaded successfully"}), 200

    except Exception as e:
        # Rollback in case of an error and return an error message
        conn.rollback()
        print("Error inserting data:", e)
        return jsonify({"error": "Failed to insert data"}), 500

# Route to retrieve topic data from the PostgreSQL database
@app.route("/api/get_data", methods=["GET"])
def get_data():
    data = {}
    try:
        # Execute SQL command to retrieve all topics
        cur.execute("SELECT * FROM wiki.topics")
        rows = cur.fetchall()

        # Process each row and add it to the response dictionary
        for row in rows:
            data[row[0]] = {"title": row[1], "content": row[2], "num_links": row[3]}

        # Return data as JSON
        return jsonify({"status": "success", "data": data}), 200

    except Exception as e:
        # Print and return error message if retrieval fails
        print("Error fetching data:", e)
        return jsonify({"status": "error", "message": "Failed to retrieve data"}), 500

# Run the Flask application
if __name__ == "__main__":
    PORT = 8001
    app.run(debug=True, port=PORT)
