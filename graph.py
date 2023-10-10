import requests
import urllib.parse
import json
import logging

# import the required MSAL for Python module(s)
from msal import ConfidentialClientApplication

import model

session = None
graph_url = "https://graph.microsoft.com/v1.0"
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


def api_call(url, method="GET", data=None):
    response = session.request(method, graph_url + url, data=data)
    if response.status_code != 200:
        logging.error(f"Failed to {method} {url}\n{response.text}")
    return response.json()


def get_account_folder_by_id(account_id: str) -> str:
    list_id = "361fab66-4975-45b7-b2d4-f655eee1ae75"
    respJson = api_call(
        f"/sites/{site_id}/lists/{list_id}/items?$filter=fields/AccountId eq '{account_id}'"
    )
    logging.debug(json.dumps(respJson, indent=2))
    if len(respJson.get("value")) == 0:
        logging.error(f"No account folder found with id {account_id}")
    else:
        return respJson.get("value")[0].get("webUrl")


def setup_tsd_info(page: model.Page) -> None:
    """
    Get the id of an item by path, make sure it's a folder.
    """
    if not page.tsd_folder_path:
        # No folder path
        return
    url = f"/sites/{site_id}/drive/root:/{urllib.parse.quote(page.tsd_folder_path)}"
    full_url = graph_url + url
    response = session.get(full_url)
    if response.status_code != 200:
        logging.error(f"Failed to get item id by path: {full_url}\n{response.text}")
        return None
    respJson = response.json()
    if "folder" not in respJson:
        logging.error(f"{full_url} is NOT a folder\n{json.dumps(respJson, indent=2)}")
        return None
    page.tsd_folder_url = respJson.get("webUrl")
    page.tsd_pdf_path = page.tsd_folder_path + "/" + page.tsd_file_name()

    url = f"/sites/{site_id}/drive/root:/{urllib.parse.quote(page.tsd_pdf_path)}"
    full_url = graph_url + url
    response = session.get(full_url)
    respJson = response.json()
    page.tsd_pdf_lastModifiedDateTime = respJson.get("lastModifiedDateTime")


def upload_file(page: model.Page, data: bytes) -> None:
    """
    Upload a file to SharePoint folder.
    """
    logging.info(f"Uploading {page.tsd_file_name()} to {page.tsd_folder_url}")
    item_path = urllib.parse.quote(page.tsd_pdf_path)
    url = f"/sites/{site_id}/drive/root:/{item_path}:/createUploadSession"
    full_url = graph_url + url
    requestBody = {
        "item": {
            "@microsoft.graph.conflictBehavior": "replace",
            # "description": f"This PDF is exported from {page.confluence_url}",
        },
    }
    response = session.post(
        full_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(requestBody),
    ).json()
    logging.debug(f"POST {full_url}\n{json.dumps(response, indent=2)}")

    upload_url = response.get("uploadUrl")
    data_len = len(data)
    index_start = 0
    index_end = 0
    while index_end < data_len:
        index_end = index_start + 1024 * 1000
        if index_end > data_len:
            index_end = data_len
        chunk = data[index_start:index_end]
        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(chunk)),
            "Content-Range": f"bytes {index_start}-{index_end-1}/{data_len}",
        }

        response = session.put(
            upload_url,
            headers=headers,
            data=chunk,
        )
        logging.debug(f"PUT {upload_url}\n{json.dumps(response.json(), indent=2)}")
        index_start = index_end
