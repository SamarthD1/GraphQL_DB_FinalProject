import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

class Neo4jDB:
    def __init__(self):
        print(f"Connecting to {URI} with user {USERNAME}...")
        self.driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
        try:
            self.driver.verify_connectivity()
            print("Connection successful!")
        except Exception as e:
            print(f"Connection failed: {e}")
            raise e

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session(database=DATABASE) as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

db = Neo4jDB()

def get_db():
    return db
