import lldb
import shlex
import argparse
from typing import Union, cast
from LLDBHelper.LLDBCommandBase import LLDBCommandBase
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    AppCommnad.register_lldb_command(debugger, AppCommnad.__module__)


class AppCommnad(LLDBCommandBase):

    @classmethod
    def cmdname(cls) -> str:
        return 'app'

    @classmethod
    def description(cls) -> str:
        return 'Application debugging. [iLLDB]'

    def create_argparser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="App debugging",
                                         formatter_class=util.HelpFormatter)
        subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

        subparsers.add_parser("info",
                              help="Show App info",
                              formatter_class=util.HelpFormatter)

        return parser

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject
    ) -> None:
        args: Union[list[str], argparse.Namespace] = shlex.split(command, posix=False)
        args = self.argparser.parse_args(cast(list[str], args))

        if args.subcommand == "info":
            self.info(args, debugger, result)
        else:
            self.argparser.print_help()

    def info(
        self,
        args: argparse.Namespace,
        debugger: lldb.SBDebugger,
        result: lldb.SBCommandReturnObject
    ) -> None:
        script = util.read_script_file('swift/app.swift')
        script += """
        printAppInfo()
        """

        _ = util.exp_script(
            debugger,
            script
        )
