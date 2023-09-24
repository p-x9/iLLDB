import lldb
from abc import ABC, abstractmethod
import argparse


class LLDBCommandBase(ABC):

    @classmethod
    @abstractmethod
    def cmdname(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        pass

    @classmethod
    def register_lldb_command(cls, debugger: lldb.SBDebugger, module_name: str) -> None:
        cls.__doc__ = cls.description()

        command = f"command script add -o -c {module_name}.{cls.__name__} {cls.cmdname()}"
        debugger.HandleCommand(command)

    @abstractmethod
    def create_argparser(self) -> argparse.ArgumentParser:
        pass

    def __init__(self, debugger: lldb.SBDebugger, bindings: dict):
        self.argparser = self.create_argparser()

    @abstractmethod
    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject
    ) -> None:
        pass

    def get_short_help(self) -> str:
        return self.description()

    def get_long_help(self) -> str:
        return self.argparser.format_help()
