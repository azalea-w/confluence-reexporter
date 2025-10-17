from typing import Generic, Iterator, List, TypeVar

from .schema import setup_db
from .database import Database

T = TypeVar('T')
U = TypeVar('U')


class Node(Generic[T]):
    def __init__(self, value: T):
        self.value: T = value
        self.children: List['Node[T]'] = []

    def add_child(self, child: 'Node[T]') -> None:
        self.children.append(child)

    def walk(self) -> Iterator['Node[T]']:
        yield self
        for child in self.children:
            yield from child.walk()

    def print_tree(self, level: int = 0) -> None:
        print(" " * level * 2 + str(self.value))
        for child in self.children:
            child.print_tree(level + 1)

    def __repr__(self) -> str:
        return f"Node({self.value})"
