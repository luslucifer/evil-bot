import sqlite3
def create_table():
    conn = sqlite3.connect('data.sqlite3')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS db (
    tmdb INTEGER,
    message_id INTEGER,
    from_id INTEGER,
    from_is_bot INTEGER,
    from_first_name TEXT,
    from_username TEXT,
    chat_id INTEGER,
    chat_title TEXT,
    chat_type TEXT,
    chat_all_members_are_administrators INTEGER,
    message_date INTEGER,
    m3u8 TEXT,
    files_list TEXT
    
);
''')
    conn.commit()
    conn.close()

# Define a function to insert data into the database
def insert_data_into_db( file_data,db='db'):
    chat_id =file_data['chat']['id']
    conn = sqlite3.connect(f'{db}.sqlite3')
    c = conn.cursor()
    c.execute('''INSERT INTO files (file_id, chat_id, file_name, mime_type, file_unique_id, file_size) VALUES (?, ?, ?, ?, ?, ?)''',
              (file_data['document']['file_id'], chat_id, file_data['document']['file_name'], file_data['document']['mime_type'],
               file_data['document']['file_unique_id'], file_data['document']['file_size']))
    conn.commit()
    conn.close()


create_table()