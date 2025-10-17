from pathlib import Path
from typing import cast, Generator

from confluence import ConfluenceParser


if __name__ == "__main__":
    for child in cast(Generator[Path, ..., ...], Path("./in_spaces").iterdir()):
        if child.is_file(): continue
        if not child.is_dir() and not (child / "entries.xml").exists(): continue

        parser = ConfluenceParser(child)
        parser.process()
