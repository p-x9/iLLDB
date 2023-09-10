import lldb
import shlex
import argparse
import subprocess
import os
from typing import Union, cast
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    debugger.HandleCommand('command script add -f app.handle_command app -h "application debugging[iLLDB]"')


def handle_command(
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
        internal_dict: dict) -> None:
    args: Union[list[str], argparse.Namespace] = shlex.split(command, posix=False)
    args = parse_args(cast(list[str], args))

    if args.subcommand == "info":
        info(args, debugger, result)


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="App debugging",
                                     formatter_class=util.HelpFormatter)
    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    subparsers.add_parser("info",
                          help="Show App info",
                          formatter_class=util.HelpFormatter)

    return parser.parse_args(args)


def info(args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
    file_path = os.path.realpath(__file__)
    dir_name = os.path.dirname(file_path)

    script_ret = subprocess.run(f"cat {dir_name}/swift/app.swift", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    script = script_ret.stdout
    script += """
    printAppInfo()
    """

    _ = util.exp_script(
        debugger,
        script
    )
