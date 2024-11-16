import pymongo

# Configure MongoDB connection
# TODO
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    if client:
        print("Connected to MongoDB server")
        client.server_info() # ping the server to verify the connection
except pymongo.errors.ConnectionFailure as e:
    print(f"Failed to connect to MongoDB server: {e}")

db = client['kafka']

if __name__ == "__main__":
    # Define a query to retrieve documents (messages)
    query = {}

    # Retrieve documents from the MongoDB collection based on the query
    messages = db.test_mongo.find(query)

    # Iterate through the retrieved documents (messages)
    for message in messages:
        print("Message from MongoDB:", message)

    # Calculate and print the message count using count_documents()
    message_count = db.test_mongo.count_documents(query)
    print(f"Total Messages Retrieved: {message_count}")
