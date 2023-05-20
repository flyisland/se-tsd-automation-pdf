import requests
import urllib.parse
import json
import logging

# import the required MSAL for Python module(s)
from msal import ConfidentialClientApplication

import model

session = None
graph_url = "https://graph.microsoft.com/v1.0/"
site_id = "f00780b3-f81c-4c7e-9526-445daa3cb7af"  # SFDCAccounts


def init(opts):
    app = ConfidentialClientApplication(
        client_id=opts["azure_client_id"],
        authority="https://login.microsoftonline.com/" + opts["azure_tenant_id"],
        client_credential=opts["azure_client_secret"],
    )
    # First, check for a token in the cache, refreshing it if needed
    result = app.acquire_token_silent(
        scopes=["https://graph.microsoft.com/.default"], account=None
    )
    # If no token was found in the cache or the token refresh failed, get a new one
    if not result:
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
    global session
    access_token = result["access_token"]
    session = requests.Session()
    session.headers.update({"Authorization": "Bearer " + access_token})
    logging.info("Connected to Azure " + graph_url)


def get_item_id_by_path(page: model.Page) -> None:
    """
    Get the id of an item by path, make sure it's a folder.
    """
    url = f"/sites/{site_id}/drive/root:/{urllib.parse.quote(page.tsd_folder_name)}"
    full_url = graph_url + url
    response = session.get(full_url)
    if response.status_code != 200:
        logging.error(f"Failed to get item id by path: {full_url}\n{response.text}")
        return None
    respJson = response.json()
    if "folder" not in respJson:
        logging.error(f"{full_url} is NOT a folder\n{json.dumps(respJson, indent=2)}")
        return None
    page.tsd_folder_id = respJson.get("id")
    page.tsd_folder_url = respJson.get("webUrl")
