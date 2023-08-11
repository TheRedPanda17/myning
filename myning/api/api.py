import os
from base64 import b64encode


# Needed once we had username and passwords
def basic_auth(username, password):
    return f'Basic {b64encode(bytes(f"{username}:{password}", "utf-8")).decode("ascii")}'


API_CONFIG = {
    "base_url": "https://myning.vercel.app/api",
    # "base_url": "http://localhost:3000",
    "auth": os.environ.get("API_KEY"),
}
