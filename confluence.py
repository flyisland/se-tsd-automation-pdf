import logging
from atlassian import Confluence
from bs4 import BeautifulSoup
import urllib.parse
import re

import graph
import model

confluence = None
dry_run = False


def init(opts):
    global confluence
    global dry_run
    if confluence is None:
        domain = opts["domain"]
        confluence = Confluence(
            url=f"https://{domain}.atlassian.net",
            username=opts.get("forge_email"),
            password=opts.get("forge_api_token"),
            cloud=True,
            api_version="cloud",
        )
    if opts.get("dry_run"):
        dry_run = True


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


def analyze_page(page_id: str):
    has_good_folder_url = "X"
    has_good_account_id = "X"
    pageJson = confluence.get_page_by_id(
        page_id, expand="body.storage,history.lastUpdated"
    )
    page = model.Page(
        page_id=page_id,
        page_url=pageJson["_links"]["base"] + pageJson["_links"]["webui"],
        title=pageJson["title"],
        page_lastUpdated=pageJson["history"]["lastUpdated"]["when"],
        bodyXml=pageJson["body"]["storage"]["value"],
    )

    try:
        if hub_folder_url := __get_account_folder_by_details(page.bodyXml):
            logging.debug(f"hub_folder_url: {hub_folder_url}")
            if tsd_folder_path := url_to_tsd_path(hub_folder_url):
                page.tsd_folder_path = tsd_folder_path
                logging.debug(f"page.tsd_folder_path: {page.tsd_folder_path}")
                graph.setup_tsd_info(page)
                logging.debug(f"page.tsd_folder_url: {page.tsd_folder_url}")
                if page.tsd_folder_url:
                    has_good_folder_url = "Y"

        account_id = __get_account_id(page.bodyXml)
        logging.debug(f"account_id: {account_id}")
        if account_id:
            account_folder = graph.get_account_folder_by_id(account_id)
            logging.debug(f"account_folder: {account_folder}")
            if tsd_folder_path := url_to_tsd_path(account_folder):
                page.tsd_folder_path = tsd_folder_path
                logging.debug(f"page.tsd_folder_path: {page.tsd_folder_path}")
                graph.setup_tsd_info(page)
                logging.debug(f"page.tsd_folder_url: {page.tsd_folder_url}")
                if page.tsd_folder_url:
                    has_good_account_id = "Y"
    except Exception as e:
        logging.error(f"Error analyzing page {page.page_url}: {e}")
    print(
        f"{page.page_id}, {has_good_folder_url}, {has_good_account_id}, {page.page_url}"
    )

    pass


def __get_account_folder_by_id(bodyXml):
    account_id = __get_account_id(bodyXml)
    account_folder = graph.get_account_folder_by_id(account_id)
    return account_folder


def __set_up_tsd_folder_path(page) -> bool:
    for get_method in [
        __get_account_folder_by_id,  # Get the Account Folder by Account ID first
        __get_account_folder_by_details,
    ]:
        account_folder = get_method(page.bodyXml)
        if not account_folder:
            continue
        page.tsd_folder_path = url_to_tsd_path(account_folder)
        graph.setup_tsd_info(page)
        if page.tsd_folder_url:
            return True
    return False


def export_page(page_id):
    """Export a page to a pdf"""
    pageJson = confluence.get_page_by_id(
        page_id, expand="body.storage,history.lastUpdated"
    )
    page = model.Page(
        page_id=page_id,
        page_url=pageJson["_links"]["base"] + pageJson["_links"]["webui"],
        title=pageJson["title"],
        page_lastUpdated=pageJson["history"]["lastUpdated"]["when"],
        bodyXml=pageJson["body"]["storage"]["value"],
    )
    logging.info(f"Checking page {page.page_url} ...")
    if not __set_up_tsd_folder_path(page):
        logging.warning(f"Cannot find the TSD folder for this page {page.page_url}")
        return
    logging.debug(page)
    if (
        page.tsd_pdf_lastModifiedDateTime
        and page.tsd_pdf_lastModifiedDateTime > page.page_lastUpdated
    ):
        logging.info(
            f"This page has already been uploaded to the folder {page.tsd_folder_url}"
        )
        return
    logging.info(f"Exporting page {page.page_url} to the TSD folder ...")
    if dry_run:
        logging.info("Dry run, skip the actual action")
        return
    pdf_data = confluence.export_page(page.page_id)
    graph.upload_file(page, pdf_data)
    logging.info(
        f"This page has been successfully uploaded to the folder {page.tsd_folder_url}"
    )


def __find_all_details_macros(htmlBody):
    soup = BeautifulSoup(htmlBody, "html.parser")
    return soup.find_all("ac:structured-macro", {"ac:name": "details"})


def __find_field_td(htmlBody, keyName):
    try:
        for details_macro in __find_all_details_macros(htmlBody):
            try:
                account_id_text = details_macro.find(string=keyName)
                tr = account_id_text.find_parent("tr")
                td = tr.find("td")
                return td
            except:
                continue
    except:
        pass


def __find_field_href(htmlBody, keyName):
    for details_macro in __find_all_details_macros(htmlBody):
        try:
            account_id_text = details_macro.find(string=keyName)
            tr = account_id_text.find_parent("tr")
            link = tr.find("td").find("a")
            href = link["href"]
            return href
        except:
            continue


def __get_account_folder_by_details(htmlBody):
    hub_folder_url = None
    try:
        hub_folder_url = __find_field_href(htmlBody, "Hub Account Folder")
    except:
        pass
    return hub_folder_url


OPPORTUNITY_ID_RE = re.compile("Opportunity/([^/]+)/view")
ACCOUNT_ID_RE = re.compile("/([^/]+)/view")
ACCOUNT_ID_RE2 = re.compile("/([^/]+)/$")


def __get_account_id(htmlBody):
    account_id = None
    try:
        account_link = __find_field_href(htmlBody, "SalesForce Account Link")
        # https://solacecorp.lightning.force.com/lightning/r/Account/00130000005pUpkAAE/view
        if m := OPPORTUNITY_ID_RE.search(account_link):
            logging.error(
                f"Could not parse account id from the opportunity link {account_link}"
            )
        elif m := ACCOUNT_ID_RE.search(account_link):
            account_id = m.group(1)
        elif m := ACCOUNT_ID_RE2.search(account_link):
            account_id = m.group(1)
        else:
            logging.error(f"Could not parse account id from {account_link}")
    except:
        pass
    return account_id


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
