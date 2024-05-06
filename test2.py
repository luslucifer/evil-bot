import json
import sqlite3
from dotenv import load_dotenv
import os 
from datetime import datetime

load_dotenv()

# Load your object from JSON file
# with open('st.json', 'r') as file:
#     obj_j = json.load(file)


# Define your Message class
class Message:
    def __init__(self, message_id, from_id, from_bot, from_first_name, from_username, chat_id, chat_title, chat_type, all_members_are_administrators, m3u8_link, files_list, imdb_id, ss, ep):
        self.message_id = message_id
        self.from_id = from_id
        self.from_bot = from_bot
        self.from_first_name = from_first_name
        self.from_username = from_username
        self.chat_id = chat_id
        self.chat_title = chat_title
        self.chat_type = chat_type
        self.all_members_are_administrators = all_members_are_administrators
        self.m3u8_link = m3u8_link
        self.files_list = files_list
        self.imdb_id = imdb_id
        self.ss = ss
        self.ep = ep


def main_db(obj_j):
# Establish connection to the SQLite database
    conn = sqlite3.connect('bot_db.sqlite')
    cursor = conn.cursor()

    # Create the Messages table if not exists
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS Bot_db (
            message_id INTEGER PRIMARY KEY,
            from_id INTEGER,
            from_bot BOOLEAN,
            from_first_name TEXT,
            from_username TEXT,
            chat_id INTEGER,
            chat_title TEXT,
            chat_type TEXT,
            all_members_are_administrators BOOLEAN,
            date TIMESTAMP,
            m3u8_link TEXT,
            files_list TEXT,
            imdb_id TEXT,
            ss TEXT,
            ep TEXT
        )
    '''
    cursor.execute(create_table_query)

    # Insert your object into the database
    message = Message(
        message_id=obj_j["message_id"],
        from_id=obj_j["from"]["id"],
        from_bot=obj_j["from"]["is_bot"],
        from_first_name=obj_j["from"]["first_name"],
        from_username=obj_j["from"]["username"],
        chat_id=obj_j["chat"]["id"],
        chat_title=obj_j["chat"]["title"],
        chat_type=obj_j["chat"]["type"],
        all_members_are_administrators=obj_j["chat"]["all_members_are_administrators"],
        m3u8_link=obj_j["m3u8_link"],
        files_list=json.dumps(obj_j["files_list"]),  # Convert list to JSON string
        imdb_id=obj_j["imdb_id"],
        ss=obj_j["ss"],
        ep=obj_j["ep"]
    )

    insert_query = '''
        INSERT INTO Bot_db (
            message_id, from_id, from_bot, from_first_name, from_username,
            chat_id, chat_title, chat_type, all_members_are_administrators,
            date, m3u8_link, files_list, imdb_id, ss, ep
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    cursor.execute(insert_query, (
        message.message_id,
        message.from_id,
        message.from_bot,
        message.from_first_name,
        message.from_username,
        message.chat_id,
        message.chat_title,
        message.chat_type,
        message.all_members_are_administrators,
        datetime.now(),  # Use current time
        message.m3u8_link,
        message.files_list,
        message.imdb_id,
        message.ss,
        message.ep
    ))

    # Commit changes and close connection
    conn.commit()
    conn.close()
