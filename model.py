from dataclasses import dataclass, field
import re


def safe_file_name(s):
    s = s.strip()
    s = s.replace(" ", "_")
    # Remove any non-alphanumeric, non-underscore, and non-hyphen characters
    s = re.sub(r"[^a-zA-Z0-9_\-]", "", s)
    return s


@dataclass
class Page:
    page_id: str
    page_url: str
    title: str
    page_lastUpdated: str
    bodyXml: str = field(repr=False, default="")
    tsd_folder_path: str = field(default="")
    tsd_folder_url: str = field(default="")
    tsd_pdf_path: str = field(default="")
    tsd_pdf_lastModifiedDateTime: str = field(default="")

    def tsd_file_name(self) -> str:
        return "TSD-" + safe_file_name(self.title) + "-autoCreated.pdf"
