import requests

# Set up your bot's API token
TOKEN = '6731479806:AAEIu9BamwRVhXeEwhzQzdELgA74t3WCkKk'

# URL for the getFile endpoint

def download_file_link(file_id:str,token:str=TOKEN):
    get_file_url = f'https://api.telegram.org/bot{TOKEN}/getFile'

    # Parameters for getting the file
    file_id = file_id  # Replace 'your_file_id' with the actual file ID you received when sending the document
    params = {'file_id': file_id}
    # Send request to get file path
    response = requests.get(get_file_url, params=params)
    file_path = response.json()['result']['file_path']
    # Construct the download URL
    download_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
    return download_url
