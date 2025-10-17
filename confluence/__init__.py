from os.path import basename
from pathlib import Path

from bs4 import BeautifulSoup
from coloredlogs import install

from ._types import Attachment, Body, ContentProperty, ContentStatus, Link, Page, parse_time, Space, SpaceType, User
from .config import Config, ThemeSelection
from .utils import Database, Node, setup_db


class ConfluenceParser:
    def __init__(self, export_location: Path, export_config: Config = Config()):
        self.config              = export_config
        self.database            = Database()
        self.location            = export_location
        self.node_tree           = Node(...)
        self.attachment_map      = {  }
        self.soup: BeautifulSoup = ...
        setup_db(self.config, self.database)

    def process(self):
        self.config.logger.info(f"[{basename(__file__)}] Reading & Parsing File...")
        with open(self.location / "entities.xml", "r", encoding = self.config.text_encoding.value) as f:
            self.soup = BeautifulSoup(f.read(), features="lxml")

        self.config.logger.info(f"[{basename(__file__)}] Starting Extraction")
        space = Space.from_bs4(self.soup.find("object", {"class": "Space"}))

        self.node_tree = Node(space)
        self.database["spaces"].insert(space)

        self.config.logger.info(f"[{basename(__file__)}] Extracted Space Node")

        for object_type, name in {
            "ContentProperty": ("properties", ContentProperty),
            "Page": ("pages", Page),
            "ConfluenceUserImpl": ("users", User),
            "OutgoingLink": ("links", Link),
            "BodyContent": ("bodies", Body),
            "Attachment": ("attachments", Attachment),
        }.items():
            name, constructor = name

            self.config.logger.info(f"[{basename(__file__)}] Extracting {name.title()}")
            for result in self.soup.find_all("object", {"class": object_type}):
                record = constructor.from_bs4(result)
                if hasattr(record, "content_properties") and record.content_properties:
                    record.content_properties = [
                        self.database["properties"].get(prop)
                        for prop in record.content_properties
                    ]

                self.database[name].insert(record)

            self.config.logger.info(f"[{basename(__file__)}] Extracted {len(self.database[name].rows.values())} {name.title()}")

        self.database.save(self.config.db_save_path)


install()