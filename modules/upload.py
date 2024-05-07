import requests
import time

# Set up your bot's API token

TOKEN = '6731479806:AAEIu9BamwRVhXeEwhzQzdELgA74t3WCkKk'

def send(filename: str, path: str, chat_id: str = '-4207795971', TOKEN: str = TOKEN, max_retries: int = 3, initial_retry_delay: float = 1.0, max_retry_delay: float = 60.0):
    url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
    params = {'chat_id': chat_id}

    with open(path, 'rb') as file:
        file_content = file.read()

    files = {'document': (filename , file_content)}

    retry_delay = initial_retry_delay

    for attempt in range(max_retries):
        response = requests.post(url, params=params, files=files, timeout=20)  # Timeout set to 10 seconds
        try:
            res = response.json()
            if response.status_code == 200:
                return res
            else:
                print(f"Failed to send document: {res}")
        except Exception as e:
            print(f"Failed to send document: {e}")

        # Exponential backoff for retry delay
        timeToRetry = response.json()['parameters']['retry_after']
        retry_delay = min(retry_delay, max_retry_delay)
        print(f"Retrying in {timeToRetry} seconds...")
        time.sleep(timeToRetry)

    print("Exceeded maximum retries, giving up.")
    return None