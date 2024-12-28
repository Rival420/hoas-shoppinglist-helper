import os
import json
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Use environment variables to store your sensitive data
HA_URL = os.environ.get("HA_URL")
HA_TOKEN = os.environ.get("HA_TOKEN")
NTFY_URL = os.environ.get("NTFY_URL")

headers_ha = {
    "Authorization": f"Bearer {HA_TOKEN}"
}

headers_ntfy = {
    "Title": "Shoppinglist",
    "Priority": "5",
}

@app.get("/shoppinglist")
def fetch_and_send_shopping_list():
    """
    Single endpoint that fetches the shopping list from Home Assistant
    and posts the incomplete items to ntfy.sh.
    """

    # 1. Fetch the shopping list items from Home Assistant
    try:
        response = requests.get(HA_URL, headers=headers_ha)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

    # 2. Filter to get only the incomplete tasks
    json_data = response.json()
    incomplete_tasks = [task["name"] for task in json_data if not task["complete"]]
    
    # 3. Format them for ntfy.sh
    formatted_output = "\n".join(f"- {task}" for task in incomplete_tasks)

    # 4. Send to ntfy.sh
    try:
        target_response = requests.post(NTFY_URL, data=formatted_output, headers=headers_ntfy)
        target_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error sending data to ntfy: {str(e)}")

    # 5. Return some status info
    return {
        "status": "OK",
        "message_sent": incomplete_tasks
    }
