import logging
from atlassian import Confluence
from bs4 import BeautifulSoup
import urllib.parse

import graph
import model

confluence = None


def init(opts):
    global confluence
    if confluence is None:
        domain = opts["domain"]
        confluence = Confluence(
            url=f"https://{domain}.atlassian.net",
            username=opts.get("forge_email"),
            password=opts.get("forge_api_token"),
            cloud=True,
            api_version="cloud",
        )
        logging.info("Connected to Confluence " + confluence.url)


def export_all(opts):
    all_pages = fetch_all_pages(opts)
    for page in all_pages:
        export_page(page.get("id"))


def fetch_all_pages(opts):
    result = []
    cql = f'space={opts["space"]} and type=page and (label="se-opportunity" or label="se-tsd")'
    cql = urllib.parse.quote(cql)
    nextPath = f"/rest/api/content/search?cql={cql}&limit=50"
    while nextPath:
        logging.info(f"Fetching {nextPath}")
        response = confluence.get(nextPath)
        result.extend(response.get("results"))
        nextPath = response.get("_links").get("next")

    return result


def export_page(page_id):
    """Export a page to a pdf"""
    pageJson = confluence.get_page_by_id(page_id, expand="body.storage")
    page = model.Page(
        confluence_id=page_id,
        confluence_url=pageJson["_links"]["base"] + pageJson["_links"]["webui"],
        title=pageJson["title"],
        bodyXml=pageJson["body"]["storage"]["value"],
    )
    hub_folder_url = get_hub_account_folder(page.bodyXml)
    if not hub_folder_url:
        logging.error(f"No hub account folder found for {page}")
        return
    page.tsd_folder_name = url_to_tsd_path(hub_folder_url)
    graph.get_item_id_by_path(page)
    print(page)


def get_hub_account_folder(htmlBody):
    hub_folder_url = None
    try:
        soup = BeautifulSoup(htmlBody, "html.parser")
        details_macro = soup.find("ac:structured-macro", {"ac:name": "details"})
        hub_account_folder_text = details_macro.find(string="Hub Account Folder")
        tr = hub_account_folder_text.find_parent("tr")
        hub_folder_link = tr.find("a")
        hub_folder_url = hub_folder_link["href"]
    except:
        pass
    return hub_folder_url


SHAREPOINT_DOMAIN = "solacesystems"
SHAREPOINT_SITE = "SFDCAccounts"


# AllItems.aspx?FolderCTID=0x0120009C4EAADEC4E7FE41B08A8A5ED7D69056&id=%2Fteams%2FSFDCAccounts%2FShared%20Documents%2FBHP%20Group%20Limited%2FOpportunities%2FBHP%2FTSD&viewid=89434c29%2D7f37%2D422d%2D8677%2D79eb6b09a265
def ___from_all_items(url):
    url_components = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(url_components.query)
    path = None
    if "id" in query_params:
        path = query_params["id"][0]
    elif "RootFolder" in query_params:
        path = query_params["RootFolder"][0]
    else:
        return None
    return path[len("/teams/SFDCAccounts/Shared Documents/") :]


SHARED_ID_TO_FOLDER = {
    "EhLvUDh9T_dPkaxvX5s31y0BU1LaOKvEEntXXgVSdHuo8g": "https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FSFDCAccounts%2FShared%20Documents%2FKimberly%2DClark%20Corporation&p=true&ga=1&",
    "EjAqEPwI6xNElUyp1CiEI3kBkjam6g-UiSHOZfzrSVJaNQ": "https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FSFDCAccounts%2FShared%20Documents%2FRenault%20s%2Ea%2Es&p=true&ga=1",
    "EjQ76JtPecJIvS1RuFOSCkABipyahnC20K4D_KyiZTny4w": "https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FSFDCAccounts%2FShared%20Documents%2FAlstom%20Transport%20SA&p=true&ga=1",
    "EmdM2N0UoB1IvzNfdumdiXIBd2Z0H2s8QHs5eC6C17M2SA": "https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FSFDCAccounts%2FShared%20Documents%2FSchneider%20Electric&p=true&ga=1",
    "EnnZMG2OSglJvzgHRh7At4QBqbnMS3ZjMv-NgLabMYoP8w": "https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FSFDCAccounts%2FShared%20Documents%2FDassault%20Aviation&p=true&ga=1",
    "EntEFvdzbKVIkHJo76P0SKwBPw15lU3aTfLtS8pRo2Vk2g": "https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FSFDCAccounts%2FShared%20Documents%2FPiper%20Sandler&p=true&ga=1",
    "Ess9T1mwym9As5q-AMJHgdIB8d5JfUypmGFlvdXXErJK5A": "https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared%20Documents/Forms/AllItems.aspx?id=%2Fteams%2FSFDCAccounts%2FShared%20Documents%2FSAFRAN%20Cabin%20Inc&p=true&ga=1",
}


extractors = [
    {
        # https://solacesystems.sharepoint.com/:f:/r/teams/SFDCAccounts/Shared%20Documents/Charles%20Schwab?csf=1&web=1&e=Y3m8zw
        "head": f"https://{SHAREPOINT_DOMAIN}.sharepoint.com/:f:/r/teams/{SHAREPOINT_SITE}/Shared%20Documents/",
        "converter": lambda x: urllib.parse.unquote(x.split("?")[0]),
    },
    {
        # https://solacesystems.sharepoint.com/:f:/t/SFDCAccounts/EhLvUDh9T_dPkaxvX5s31y0BU1LaOKvEEntXXgVSdHuo8g?e=GXl2s7
        "head": f"https://{SHAREPOINT_DOMAIN}.sharepoint.com/:f:/t/{SHAREPOINT_SITE}/",
        "converter": lambda x: ___from_all_items(
            SHARED_ID_TO_FOLDER.get(urllib.parse.unquote(x.split("?")[0]))
        ),
    },
    {
        # https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared%20Documents/Forms/AllItems.aspx?FolderCTID=0x0120009C4EAADEC4E7FE41B08A8A5ED7D69056&id=%2Fteams%2FSFDCAccounts%2FShared%20Documents%2FBHP%20Group%20Limited%2FOpportunities%2FBHP%2FTSD&viewid=89434c29%2D7f37%2D422d%2D8677%2D79eb6b09a265
        "head": f"https://{SHAREPOINT_DOMAIN}.sharepoint.com/teams/{SHAREPOINT_SITE}/Shared%20Documents/Forms/",
        "converter": ___from_all_items,
    },
    {
        # https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared%20Documents/Air%20France
        "head": f"https://{SHAREPOINT_DOMAIN}.sharepoint.com/teams/{SHAREPOINT_SITE}/Shared%20Documents/",
        "converter": lambda x: urllib.parse.unquote(x),
    },
]


def url_to_tsd_path(url):
    path = None
    for extractor in extractors:
        if not url.startswith(extractor["head"]):
            continue
        rest = url[len(extractor["head"]) :]
        if "converter" in extractor:
            path = extractor["converter"](rest)
        else:
            path = rest
        break
    if not path:
        return path
    return path.split("/")[0] + "/TSDs"
