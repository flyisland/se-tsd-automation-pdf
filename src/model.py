from dataclasses import dataclass, field


@dataclass
class Page:
    confluence_id: str
    confluence_url: str
    title: str
    bodyXml: str = field(repr=False)
    tsd_folder_name: str = field(default="")
    tsd_folder_id: str = field(default="")
    tsd_folder_url: str = field(default="")
