import logging
from atlassian import Confluence
from bs4 import BeautifulSoup

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


def export_page(page_id, opts):
    """Export a page to a pdf"""
    init(opts)
    page = confluence.get_page_by_id(page_id, expand="body.storage")
    print(f"L: {page['_links']['base']+page['_links']['webui']}")
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
