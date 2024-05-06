import json
from typing import List, Dict, Union

class Message:
    def __init__(self, message_id: int, from_id: int, from_bot: bool, from_first_name: str, from_username: str,
                 chat_id: int, chat_title: str, chat_type: str, all_members_are_administrators: bool,
                 date: int, m3u8_link: str, files_list: List[str], imdb_id: str, ss: int, ep: int):
        self.message_id = message_id
        self.from_id = from_id
        self.from_bot = from_bot
        self.from_first_name = from_first_name
        self.from_username = from_username
        self.chat_id = chat_id
        self.chat_title = chat_title
        self.chat_type = chat_type
        self.all_members_are_administrators = all_members_are_administrators
        self.date = date
        self.m3u8_link = m3u8_link
        self.files_list = files_list
        self.imdb_id = imdb_id
        self.ss = ss
        self.ep = ep

    @classmethod
    def from_json(cls, json_data: Dict[str, Union[int, str, bool, Dict[str, Union[int, str]], List[str]]]):
        return cls(
            message_id=json_data.get('message_id', 0),
            from_id=json_data.get('from', {}).get('id', 0),
            from_bot=json_data.get('from', {}).get('is_bot', False),
            from_first_name=json_data.get('from', {}).get('first_name', ''),
            from_username=json_data.get('from', {}).get('username', ''),
            chat_id=json_data.get('chat', {}).get('id', 0),
            chat_title=json_data.get('chat', {}).get('title', ''),
            chat_type=json_data.get('chat', {}).get('type', ''),
            all_members_are_administrators=json_data.get('chat', {}).get('all_members_are_administrators', False),
            date=json_data.get('date', 0),
            m3u8_link=json_data.get('m3u8_link', ''),
            files_list=json_data.get('files_list', []),
            imdb_id=json_data.get('imdb_id', ''),
            ss=json_data.get('ss', 0),
            ep=json_data.get('ep', 0)
        )

# Load JSON data from file
with open('st.json', 'r') as file:
    obj_j = json.load(file)

# Create Message object from JSON data
message = Message.from_json(obj_j)

# Print the attributes of the Message object
for key,values in message.__dict__.items():
    print(f'{key}:{values}')
