import lldb
import shlex
import argparse
import subprocess
import os
from typing import Union, cast
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    debugger.HandleCommand('command script add -f file.handle_command file -h "file debugging[iLLDB]"')


def handle_command(
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
        internal_dict: dict) -> None:
    args: Union[list[str], argparse.Namespace] = shlex.split(command, posix=False)
    args = parse_args(cast(list[str], args))

    if args.subcommand == "tree":
        tree(args, debugger, result)


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="File debugging",
                                     formatter_class=util.HelpFormatter)
    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    tree_command = subparsers.add_parser("tree", help="Show file hierarchie")
    tree_command.add_argument("-l", "--library", action="store_true", help="library directory")
    tree_command.add_argument("--documents", action="store_true", help="documents directory")
    tree_command.add_argument("--tmp", type=str, help="tmp directory")

    parser.add_argument("path",
                        nargs='?',
                        default='',
                        type=str,
                        help="path to show tree")

    return parser.parse_args(args)


def tree(args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
    file_path = os.path.realpath(__file__)
    dir_name = os.path.dirname(file_path)

    script_ret = subprocess.run(f"cat {dir_name}/swift/file.swift", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    script = script_ret.stdout
    if args.library:
        script += "listFilesInDirectory(FileManager.default.urls(for: .libraryDirectory, in: .userDomainMask).first!)"
    elif args.documents:
        script += "listFilesInDirectory(FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!)"
    elif args.tmp:
        script += "listFilesInDirectory(FileManager.default.temporaryDirectory)"
    elif args.path:
        script += f"listFilesInDirectory(URL(fileURLWithPath: {args.path}))"

    ret = util.exp_script(
        debugger,
        script
    )
    result.AppendMessage(ret)
