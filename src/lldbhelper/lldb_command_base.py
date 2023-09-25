import lldb
from abc import ABC, abstractmethod
import argparse

# ref: https://lldb.llvm.org/use/python-reference.html#create-a-new-lldb-command-using-a-python-function


class LLDBCommandBase(ABC):
    """
    Abstract base class for creating LLDB commands.

    This class provides a framework for creating LLDB commands.
    It defines abstract methods for command name, description, argument parser creation, and command execution.
    It also provides methods for registering the command with LLDB and retrieving help information.
    """

    @classmethod
    @abstractmethod
    def cmdname(cls) -> str:
        """
        Abstract method that returns the name of the command.

        Returns:
            str: The name of the command.
        """
        pass

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        """
        Abstract method that returns the description of the command.

        Returns:
            str: The description of the command.
        """
        pass

    @classmethod
    def register_lldb_command(cls, debugger: lldb.SBDebugger, module_name: str) -> None:
        """
        Registers the command with LLDB.

        This method sets the command's description and adds it to the debugger.

        Args:
            debugger (lldb.SBDebugger): The LLDB debugger.
            module_name (str): The name of the module.

        Returns:
            None
        """
        cls.__doc__ = cls.description()

        command = f"command script add -o -c {module_name}.{cls.__name__} {cls.cmdname()}"
        debugger.HandleCommand(command)

    @abstractmethod
    def create_argparser(self) -> argparse.ArgumentParser:
        """
        Abstract method that creates and returns an argument parser for the command.

        Returns:
            argparse.ArgumentParser: The argument parser for the command.
        """
        pass

    def __init__(self, debugger: lldb.SBDebugger, internal_dict: dict):
        """
        Initializes the LLDBCommandBase instance.

        Args:
            debugger (lldb.SBDebugger): The LLDB debugger.
            internal_dict (dict): The internal dictionary.

        Returns:
            None
        """
        self.argparser = self.create_argparser()

    @abstractmethod
    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject
    ) -> None:
        """
        Abstract method that executes the command logic.

        Args:
            debugger (lldb.SBDebugger): The LLDB debugger.
            command (str): The command string.
            exe_ctx (lldb.SBExecutionContext): The execution context.
            result (lldb.SBCommandReturnObject): The command result.

        Returns:
            None
        """
        pass

    def get_short_help(self) -> str:
        """
        Returns the short help message for the command.
        Default implementation is that `description` is returned.

        Returns:
            str: The short help message.
        """
        return self.description()

    def get_long_help(self) -> str:
        """
        Returns the long help message for the command.
        Default implementation is that the argparser help message is returned.

        Returns:
            str: The long help message.
        """
        return self.argparser.format_help()
