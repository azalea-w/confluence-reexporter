from os.path import basename

from .._types import Attachment, Body, ContentProperty, Link, Page, Space, User
from ..config import Config
from .database import Database

SCHEMA = [{
        "name"     : "users",
        "pk_field" : "_id",
        "row_type" : User,
    }, {
        "name"     : "pages",
        "pk_field" : "_id",
        "row_type" : Page,
        "fk_fields": { "creator_id": "users", "space_id": "spaces"  }
    }, {
        "name"     : "spaces",
        "pk_field" : "_id",
        "row_type" : Space,
        "fk_fields": {"creator_id": "users", "home_page_id": "pages"}
    }, {
        "name"     : "properties",
        "pk_field" : "_id",
        "row_type" : ContentProperty,
        "fk_fields": {            "content_id": "pages"             }
    }, {
        "name"     : "links",
        "pk_field" : "_id",
        "row_type" : Link,
        "fk_fields": {            "content_id": "pages"             }
    }, {
        "name"     : "bodies",
        "pk_field" : "_id",
        "row_type" : Body,
        "fk_fields": {            "content_id": "pages"             }
    }, {
        "name"     : "attachments",
        "pk_field" : "_id",
        "row_type" : Attachment,
        "fk_fields": {"content_id": "pages", "creator_id": "users", "space_id": "spaces"}
}]

def setup_db(config: Config, database: Database):
    config.logger.info(f"[{basename(__file__)}] Setting up DB")

    if config.load_existing_db:
        config.logger.info(f"[{basename(__file__)}] Trying to load DB from file")
        database.load(config.db_save_path)
        if database.tables: return

    config.logger.info(f"[{basename(__file__)}] Creating DB Schema")
    for table_definition in SCHEMA:
        database.create_table(**table_definition)