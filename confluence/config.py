from dataclasses import dataclass
from enum import Enum
from logging import getLogger, Logger
from pathlib import Path


class ThemeSelection(Enum):
    DARK = 0
    LIGHT = 1


class TextEncoding(Enum):
    UTF8 = 'utf-8'
    UTF16 = 'utf-16'
    ASCII = 'ascii'
    LATIN1 = 'latin-1'
    CP1252 = 'cp1252'
    ISO8859_1 = 'iso-8859-1'


@dataclass
class Config:
    save_db: bool               = True
    load_existing_db: bool      = True
    export_attachments: bool    = True
    text_encoding: TextEncoding = TextEncoding.UTF8
    logger: Logger              = getLogger(__name__)
    theme: ThemeSelection       = ThemeSelection.DARK
    db_save_path: Path          = Path("./confluence_db.pickle")
