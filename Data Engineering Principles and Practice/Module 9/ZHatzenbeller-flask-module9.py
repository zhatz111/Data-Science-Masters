from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import psycopg2

app = Flask(__name__)

topics_data = {}

# Connect to the JHU postgre database
DB_NAME = "jhu"
DB_USER = "jhu"
DB_PASS = "jhu123"
DB_HOST = "localhost"
DB_PORT = "5432"

try:
    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    print("Database connected successfully")
except Exception as e:
    print("Database not connected successfully")

# Generate a cursor for executing SQL commands on the database
cur = conn.cursor()

# Execute SQL to create a new schema and table for the merged, cleaned file
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

# Commit the cursor execution SQL to the database
conn.commit()
print("Table Created successfully")


@app.route("/api/check_data", methods=["GET"])
def check_data():
    return jsonify(topics_data)


# Route to scrape a Wikipedia topic based on a POST request
@app.route("/api/scrape_wikipedia", methods=["POST"])
def scrape_wikipedia():
    # Get JSON data from the request
    data = request.get_json()

    # Extract the topic from the JSON object
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Topic not provided"}), 400

    # Prepare Wikipedia URL based on the topic
    url = f"https://en.wikipedia.org/wiki/{topic}"

    try:
        # Send a request to the Wikipedia page
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code != 200:
            return jsonify({"error": "Failed to retrieve the page"}), 400

        # Use BeautifulSoup to scrape the content
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract the first paragraph of the page as an example
        page_title = soup.find("title").text
        first_paragraph = soup.find("p").text.strip()[0:100]
        num_links = len(soup.find_all("a"))

        scraped_topic = {
            "title": page_title,
            "content": first_paragraph,
            "num_links": num_links,
        }

        topics_data[topic] = scraped_topic

        # Return the first paragraph and number of links in the response
        return jsonify(scraped_topic)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/delete_topic", methods=["DELETE"])
def delete_topic():
    # Get JSON data from the request
    data = request.get_json()

    # Extract the topic from the JSON object
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Topic not provided"}), 400

    # Check if the topic exists in the data
    if topic in topics_data:
        # Remove the topic
        del topics_data[topic]
        return jsonify({"message": f'Topic "{topic}" deleted successfully'}), 200
    else:
        # Return an error if the topic is not found
        return jsonify({"error": "Topic not found"}), 404


@app.route("/api/update_topic", methods=["PUT"])
def update_topic():
    # Get JSON data from the request
    data = request.get_json()

    # Extract the topic from the JSON object
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Topic not provided"}), 400

    # Check if the topic exists in the data
    if topic in topics_data:
        # Update the topic for each attribute
        for key, _ in data.items():
            if key != "topic":
                topics_data[topic][key] = data[key]

        return jsonify({"message": f'Topic "{topic}" updated successfully'}), 200
    else:
        # Return an error if the topic is not found
        return jsonify({"error": "Topic not found"}), 404


@app.route("/api/add_data", methods=["POST"])
def add_data():
    try:
        # Get the data from the request body
        for key, value in topics_data.items():
            cur.execute(
                "INSERT INTO wiki.topics (topic, title, content, num_links) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (key, value["title"], value["content"], value["num_links"]),
            )

        # Commit the data insertion to the database
        conn.commit()
        print("Data Loaded successfully")
        return jsonify({"message": "Data loaded successfully"}), 200

    except Exception as e:
        conn.rollback()
        print("Error inserting data:", e)
        return jsonify({"error": "Failed to insert data"}), 500


@app.route("/api/get_data", methods=["GET"])
def get_data():
    data = {}
    try:
        # Retrieve data from the database
        cur.execute("SELECT * FROM wiki.topics")
        rows = cur.fetchall()

        # Process each row and add it to the response dictionary
        for row in rows:
            data[row[0]] = {"title": row[1], "content": row[2], "num_links": row[3]}

        # Return a structured JSON response
        return jsonify({"status": "success", "data": data}), 200

    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({"status": "error", "message": "Failed to retrieve data"}), 500


if __name__ == "__main__":
    PORT = 8001
    app.run(debug=True, port=PORT)
