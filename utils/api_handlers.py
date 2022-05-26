import requests
import json
from random import random
from urllib3.exceptions import InsecureRequestWarning

from settings import ENDPOINT_URL, UV_TOKEN

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_draft_id(insert_record):
    header = {
        'content-type': 'application/json',
        'authorization': 'Bearer {}'.format(UV_TOKEN)
    }
    metadata = {
        "access": {
            "record": "public",
            "files": "public"
            },
        "files": {
            "enabled": True
            },
        "metadata": {
            "title": "(DRAFT: Reserved UV ID Number)"
        }
    }

    num_times = 3

    while num_times > 0:
        try:
            r = requests.post(url=ENDPOINT_URL,
                      data=json.dumps(metadata),
                      headers=header,
                      verify=False,
                      timeout=1)
            if r.status_code == 201:
                return True, json.loads(r.text)["id"]
                break
            else:
                num_times-=1
                continue
        except requests.Timeout:
            num_times-=1
            continue
        except requests.ConnectionError:
            return False, "Connection Error, check if UV website is down."
    return False, "Unable to draft record. Make sure UV website is working."


def get_temp_random_id():
    char_options = ["1","2","3","4","5","6","7","8","9","a","b","c","d","e",
                    "f","g","h","j","k","m","n","p","q","r","s","t","u","v",
                    "w","x","y","z"]

    temp_id = ""
    for i in range(0, 10):
        temp_id += char_options[int(random() * len(char_options))]
        if i == 4:
            temp_id += "-"
    return True, temp_id