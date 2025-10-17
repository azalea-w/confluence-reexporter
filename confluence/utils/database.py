import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Generic,  List, NamedTuple, Optional, Type, TypeVar


T = TypeVar('T')
U = TypeVar('U')


@dataclass
class TableMeta:
    name: str
    pk_field: str
    fk_fields: Dict[str, str]  # field -> referenced table


@dataclass
class MetaTable:
    tables: Dict[str, TableMeta] = field(default_factory=dict)

    def register(self, name: str, pk_field: str, fk_fields: dict = None) -> TableMeta:
        if fk_fields is None:
            fk_fields = {}

        meta = TableMeta(name, pk_field, fk_fields)
        self.tables[name] = meta
        return meta


class JoinedRow(NamedTuple):
    left: T
    right: U


class Table(Generic[T]):
    def __init__(self, meta: TableMeta, row_type: Type[T], database_ref: 'Database'):
        self.meta = meta
        self.row_type = row_type
        self.db_ref: 'Database' = database_ref
        self.rows: Dict[U, T] = {}

    def insert(self, row: T, silent: bool = False):
        pk = getattr(row, self.meta.pk_field)
        if pk in self.rows:
            if silent: return
            raise ValueError(f"Duplicate PK {pk} in table {self.meta.name}")

        self.rows[pk] = row

    def get(self, pk: U) -> Optional[T]:
        return self.rows.get(pk)

    def join(self, fk_field: str, limit: int = -1) -> Generator[JoinedRow, ..., ...]:
        fk_table_name = self.meta.fk_fields.get(fk_field)

        if not fk_table_name:
            raise ValueError(f"No FK defined for field '{fk_field}' in table '{self.meta.name}'")

        fk_table = self.db_ref.get_table(fk_table_name)

        for index, row in enumerate(self.rows.values()):
            if 0 <= limit < (index + 1): return
            fk_value = getattr(row, fk_field)
            related = fk_table.get(fk_value)
            if related: yield JoinedRow(left=row, right=related)

    def filter(self, predicate: Callable[[T], bool]) -> List[T]:
        return [row for row in self.rows.values() if predicate(row)]

    def aggregate(self, func: Callable[[List[T]], Any]) -> Any:
        return func(list(self.rows.values()))


class Database:
    def __init__(self):
        self.meta = MetaTable()
        self.tables: Dict[str, Table[T]] = {}

    def create_table(self, name: str, pk_field: str, row_type: Type[T], fk_fields: dict[str, str] = None) -> Table[T]:
        if fk_fields is None:
            fk_fields = {}

        meta = self.meta.register(name, pk_field, fk_fields)
        table = Table(meta, row_type, self)
        self.tables[name] = table
        return table

    def get_table(self, name: str) -> Table[T]:
        return self.tables[name]


    def load(self, location: Path):
        if not location.exists(): return

        with open(location, "rb") as f:
            saved = pickle.loads(f.read())
            self.meta = saved["meta"]
            self.tables = saved["tables"]

        for name, table in self.tables.items():
            table.db_ref = self

    def save(self, location: Path):
        for name in self.tables:
            self.tables[name].db_ref = None

        with open(location, "wb+") as f:
            f.write(
                pickle.dumps({
                    "meta": self.meta,
                    "tables": self.tables
                })
            )

    def __getitem__(self, table_name: str)  -> Table[T]:
        return self.tables[table_name]
