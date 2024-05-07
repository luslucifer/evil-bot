import json
from dotenv import load_dotenv
import os
from datetime import datetime
import psycopg2

load_dotenv()

# Define your Message class
class Message:
    def __init__(self, m3u8_link, files_list, imdb_id, ss, ep, mp4_arr):
        self.m3u8_link = m3u8_link
        self.files_list = files_list
        self.imdb_id = imdb_id
        self.ss = ss
        self.ep = ep
        self.mp4_arr = mp4_arr

def main_db(obj_j):
    # Establish connection to the PostgreSQL database
    DATABASE_URL = os.getenv('DB_URL')
    conn = psycopg2.connect('postgresql://movies%20and%20tv%20file%20ids_owner:dA2BlmHuZc0p@ep-polished-waterfall-a55cmupj.us-east-2.aws.neon.tech/movies%20and%20tv%20file%20ids?sslmode=require')
    cursor = conn.cursor()

    # Create the Messages table if not exists
    create_table_query = '''
CREATE TABLE IF NOT EXISTS final_table (
    id SERIAL PRIMARY KEY,
    m3u8_link TEXT,
    files_list JSONB,
    imdb_id TEXT,
    ss TEXT,
    ep TEXT,
    mp4_arr JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);'''
    cursor.execute(create_table_query)

    # Insert your object into the database
    message = Message(
        m3u8_link=obj_j["m3u8_link"],
        files_list=json.dumps(obj_j["files_list"]),  # Convert list to JSON string
        imdb_id=obj_j["imdb_id"],
        ss=obj_j["ss"],
        ep=obj_j["ep"],
        mp4_arr=obj_j['mp4_arr']
    )

    # Use parameterized query to avoid SQL injection
    insert_query = '''
INSERT INTO final_table (
    m3u8_link, files_list, imdb_id, ss, ep, mp4_arr
) VALUES (
    %s, %s, %s, %s, %s, %s
);
'''
    cursor.execute(insert_query, (
        message.m3u8_link,
        message.files_list,
        message.imdb_id,
        message.ss,
        message.ep,
        json.dumps(message.mp4_arr)  # Convert list to JSON string
    ))

    # Commit changes and close connection
    conn.commit()
    conn.close()

# Example usage
# Load data from JSON file


# Call the function to insert data into the PostgreSQL database
