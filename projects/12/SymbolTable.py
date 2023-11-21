import os
import sys


class TableRecord:
    def __init__(self, type: str, kind: str, num: int) -> None:
        self.type = type
        self.num = num
        self.kind = kind


class Table:
    def __init__(self) -> None:
        self.data: dict[str, TableRecord] = {}
        self.counters = {"static": 0, "field": 0, "argument": 0, "local": 0}

    def add(self, name: str, type: str, kind: str) -> None:
        self.data[name] = TableRecord(type, kind, self.counters[kind])
        self.counters[kind] += 1


class SymbolTable:
    """used to store the name, type, kind and index of each variable
    for one Jack class, we builf one class-level symbol table and one
    subroutine-level symbol table"""

    def __init__(self):
        self.cur_class = ""
        self.subroutine = ""
        self.class_table = Table()
        self.subroutine_table = Table()

    def start_subroutine(self, is_method: bool) -> None:
        self.subroutine_table = Table()
        if is_method:
            self.subroutine_table.add("this", self.cur_class, "argument")

    def define(self, name, type, kind):
        if kind in ["static", "field"]:
            self.class_table.add(name, type, kind)
        if kind in ["argument", "local"]:
            self.subroutine_table.add(name, type, kind)

    def varCount(self, kind):
        return self.subroutine_table.counters[kind] + self.class_table.counters[kind]

    def record_of(self, name: str) -> TableRecord:
        try:
            return self.subroutine_table.data[name]
        except KeyError:
            try:
                return self.class_table.data[name]
            except KeyError:
                return None

    # static/field....
    def kindOf(self, name):
        record = self.record_of(name)
        if record:
            return self.record_of(name).kind

    """def segment_of(self, name: str) -> str:
        record  = self._record_of(name)
        if record:    
            return consts.KIND_TO_SEGMENT[
                self._record_of(name).kind
                ]"""

    def typeOf(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        # Your code goes here!
        record = self.record_of(name)
        if record:
            return self.record_of(name).type

    def indexOf(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        # Your code goes here!
        record = self.record_of(name)
        if record:
            return self.record_of(name).num
