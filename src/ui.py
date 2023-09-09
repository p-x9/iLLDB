import lldb
import shlex
import argparse
import subprocess
import os
from typing import Union, cast
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    debugger.HandleCommand('command script add -f ui.handle_command ui -h "ui debugging[iLLDB]"')


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
    parser = argparse.ArgumentParser(description="UI debugging",
                                     formatter_class=util.HelpFormatter)
    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    tree_command = subparsers.add_parser("tree", help="Show view hierarchie")
    tree_command.add_argument("-d", "--detail", action="store_true", help="Enable detailed mode")
    tree_command.add_argument("-s", "--simple", action="store_true", help="Enable simpled mode")
    tree_command.add_argument("--window", type=str, help="Specify the target window")
    tree_command.add_argument("--view", type=str, help="Specify the target view")
    tree_command.add_argument("--vc", type=str, help="Specify the target viewController")

    return parser.parse_args(args)


def tree(args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
    file_path = os.path.realpath(__file__)
    dir_name = os.path.dirname(file_path)

    script_ret = subprocess.run(f"cat {dir_name}/swift/tree.swift", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    isDetail = "true" if args.detail is True else "false"
    isSimple = "true" if args.simple is True else "false"

    script = script_ret.stdout
    if args.window:
        script += f"\n windowHierarchy({args.window}, isSimple: {isSimple}, isDetail: {isDetail})"
    elif args.view:
        script += f"\n viewHierarchy({args.view}, isSimple: {isSimple}, isDetail: {isDetail})"
    elif args.vc:
        script += f"\n viewControllerHierarchy({args.vc}, isSimple: {isSimple}, isDetail: {isDetail})"
    else:
        script += f"\n windowHierarchy(UIApplication.shared.keyWindow, isSimple: {isSimple}, isDetail: {isDetail})"

    ret = util.exp_script(
        debugger,
        script
    )
    result.AppendMessage(ret)
