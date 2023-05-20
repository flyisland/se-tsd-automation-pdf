import logging
from atlassian import Confluence
from bs4 import BeautifulSoup
import urllib.parse

logging.basicConfig(level=logging.INFO)
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
    page = confluence.get_page_by_id(page_id, expand="body.storage")
    print(f"P: {page['_links']['base']+page['_links']['webui']}")
    hub_folder_url = get_hub_account_folder(page["body"]["storage"]["value"])
    if hub_folder_url:
        print(f"F: {hub_folder_url}")
    else:
        print("E: No hub account folder found")
    return


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
