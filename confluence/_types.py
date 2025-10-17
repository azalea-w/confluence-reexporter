from dataclasses import  dataclass
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar
import re

from bs4 import BeautifulSoup, Tag

T = TypeVar('T')

DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
parse_time = lambda time_string: datetime.strptime(time_string, DATE_FORMAT) if time_string != "0" else None


class BaseEnum(Enum):
    @classmethod
    def get(cls, index: int | str):
        try: return cls(index) if isinstance(index, int) else cls.__members__[index.upper()]
        except KeyError: return cls(-1)


class SpaceType(BaseEnum):
    GLOBAL  =  0
    UNKNOWN = -1


class ContentStatus(BaseEnum):
    DRAFT   =  0
    DELETED =  1
    CURRENT =  2
    UNKNOWN = -1


class BodyType(BaseEnum):
    UNKNOWN = -1


@dataclass
class NoRes:
    text = "0"


# * Space
@dataclass
class Space:
    _id: int
    key: str
    name: str
    creator_id: str
    home_page_id: int
    space_type: SpaceType
    creation_date: datetime
    modification_date: datetime
    space_status: ContentStatus = ContentStatus.UNKNOWN

    @staticmethod
    def from_bs4(soup: BeautifulSoup | Tag):
        return Space(**{
            "_id": int(soup.find("id").text),
            "key": soup.find("property", {"name": "key"}).text,
            "name": soup.find("property", {"name": "name"}).text,
            "creator_id": soup.find("property", {"name": "creator"}).text,
            "home_page_id": int(soup.find("property", {"name": "homePage"}).text),
            "space_type": SpaceType.get(soup.find("property", {"name": "spaceType"}).text),
            "creation_date": parse_time(soup.find("property", {"name": "creationDate"}).text),
            "space_status": ContentStatus.get(soup.find("property", {"name": "spaceStatus"}).text),
            "modification_date": parse_time(soup.find("property", {"name": "lastModificationDate"}).text),
        })


# * ConfluenceUserImpl
@dataclass
class User:
    _id: str
    name: str
    email: str

    @staticmethod
    def from_bs4(soup: BeautifulSoup | Tag):
        return User(**{
            "_id": soup.find("id", {"name": "key"}).text,
            "name": soup.find("property", {"name": "name"}).text,
            "email": (soup.find("property", {"name": "email"}) or NoRes).text,
        })


# * OutgoingLink
@dataclass
class Link:
    _id: str
    source_id: int
    creator_id: str
    creation_date: datetime
    destination_space_key: str
    destination_page_title: str
    modification_date: datetime

    @staticmethod
    def from_bs4(soup: BeautifulSoup | Tag):
        return Link(**{
            "_id": soup.find("id", {"name": "id"}).text,
            "creator_id": soup.find("property", {"name": "creator"}).text,
            "source_id": soup.find("property", {"name": "sourceContent"}).text,
            "creation_date": parse_time(soup.find("property", {"name": "creationDate"}).text),
            "destination_space_key": soup.find("property", {"name": "destinationSpaceKey"}).text,
            "destination_page_title": soup.find("property", {"name": "destinationPageTitle"}).text,
            "modification_date": parse_time(soup.find("property", {"name": "lastModificationDate"}).text),
        })


# * ContentProperty
@dataclass
class ContentProperty(Generic[T]):
    _id: int
    name: str
    value: T
    content_id: int

    @staticmethod
    def from_bs4(soup: BeautifulSoup | Tag):
        return ContentProperty(**{
            "_id": int(soup.find("id", {"name": "id"}).text),
            "name": soup.find("property", {"name": "name"}).text,
            "content_id": soup.find("property", {"name": "content"}).text,
            "value": soup.find("property", {"name": re.compile(".*Value")}).text,
        })


# * Page
@dataclass
class Page:
    _id: int
    title: str
    version: int
    space_id: int
    creator_id: str
    parent: int | None
    position: int | None
    creation_date: datetime
    modification_date: datetime
    content_properties: list[ContentProperty]
    content_status: ContentStatus = ContentStatus.UNKNOWN

    @staticmethod
    def from_bs4(soup: BeautifulSoup | Tag):
        return Page(**{
            "_id": int(soup.find("id", {"name": "id"}).text),
            "title": (soup.find("property", {"name": "title"}) or NoRes).text,
            "creator_id": soup.find("property", {"name": "creator"}).text,
            "parent": int((soup.find("property", {"name": "parent"}) or NoRes).text or 0),
            "space_id": int((soup.find("property", {"name": "space"}) or NoRes).text or 0),
            "version": int((soup.find("property", {"name": "version"}) or NoRes).text or 0),
            "position": int((soup.find("property", {"name": "position"}) or NoRes).text or 0),
            "content_status": ContentStatus.get(soup.find("property", {"name": "contentStatus"}).text),
            "creation_date": parse_time((soup.find("property", {"name": "creationDate"}) or NoRes).text),
            "modification_date": parse_time((soup.find("property", {"name": "lastModificationDate"}) or NoRes).text),
            "content_properties": [int(prop_ref.text.strip()) for prop_ref in
                soup.find("element", {"package": "com.atlassian.confluence.content"})
            ]
        })


# * BodyContent
@dataclass
class Body:
    _id: int
    content_id: int
    body_type: BodyType
    body: str


    @staticmethod
    def from_bs4(soup: BeautifulSoup | Tag):
        return Body(**{
            "body": str(soup),
            "_id": soup.find("id", {"name": "id"}).text,
            "content_id": soup.find("property", {"name": "content"}).text,
            "body_type": BodyType.get(soup.find("property", {"name": "bodyType"}).text),
        })


# * Attachment
@dataclass
class Attachment:
    _id: str
    title: str
    source: int
    version: int
    space_id: int
    creator_id: str
    creation_date: datetime
    modification_date: datetime
    content_properties: list[ContentProperty]
    content_status: ContentStatus = ContentStatus.UNKNOWN

    @staticmethod
    def from_bs4(soup: BeautifulSoup | Tag):
        return Attachment(**{
            "_id": int(soup.find("id", {"name": "id"}).text),
            "title": soup.find("property", {"name": "title"}).text,
            "creator_id": soup.find("property", {"name": "creator"}).text,
            "source": int((soup.find("property", {"name": "parent"}) or NoRes).text or 0),
            "space_id": int((soup.find("property", {"name": "space"}) or NoRes).text or 0),
            "version": int((soup.find("property", {"name": "version"}) or NoRes).text or 0),
            "creation_date": parse_time(soup.find("property", {"name": "creationDate"}).text),
            "content_status": ContentStatus.get(soup.find("property", {"name": "contentStatus"}).text),
            "modification_date": parse_time((soup.find("property", {"name": "lastModificationDate"}) or NoRes).text),
            "content_properties": [int(prop_ref.text.strip()) for prop_ref in
                soup.find("element", {"package": "com.atlassian.confluence.content"})
            ]
        })