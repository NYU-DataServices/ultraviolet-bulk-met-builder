import requests
import json
from urllib3.exceptions import InsecureRequestWarning

from settings import ENDPOINT_URL, UV_TOKEN

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_draft_id():
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
            else:
                num_times-=1
                continue
        except requests.Timeout:
            num_times-=1
            continue
        except requests.ConnectionError:
            return False, "Connection Error, check if UV website is down."
    return False, "Unable to draft record. Make sure UV website is working."



