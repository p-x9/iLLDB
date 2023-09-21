import lldb
import shlex
import argparse
from typing import Union, cast
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    debugger.HandleCommand('command script add -f cookie.handle_command cookie -h "HTTP Cookie debugging[iLLDB]"')


def handle_command(
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
        internal_dict: dict) -> None:
    args: Union[list[str], argparse.Namespace] = shlex.split(command, posix=False)
    args = parse_args(cast(list[str], args))

    if args.subcommand == "read":
        read(args, debugger, result)


def parse_args(args: list[str]) -> argparse.Namespace:
    description = "HTTP Cookie debugging"
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=util.HelpFormatter)
    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    # read
    read_command = subparsers.add_parser("read",
                                         help="Read Cookie value",
                                         formatter_class=util.HelpFormatter)
    read_command.add_argument("--group-id", type=str, help="AppGroup identifier for cookie storage")
    read_command.add_argument("--domain", type=str, help="Domain for Cookie")
    read_command.add_argument("--name", type=str, help="Name for Cookie")
    read_command.add_argument("--path", type=str, help="Path for Cookie")

    return parser.parse_args(args)


def read(args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
    script = "@import Foundation;\n"
    if args.group_id is not None:
        script += f'NSHTTPCookieStorage *storage = [NSHTTPCookieStorage sharedCookieStorageForGroupContainerIdentifier:@"{args.group_id}"];\n'
    else:
        script += "NSHTTPCookieStorage *storage = [NSHTTPCookieStorage sharedHTTPCookieStorage];\n"

    script += util.read_script_file('objc/cookie_read.m')

    # domain
    if args.domain is not None:
        script = script.replace("<DOMAIN>", args.domain)
    else:
        script = script.replace("@\"<DOMAIN>\"", "NULL")

    # name
    if args.name is not None:
        script = script.replace("<NAME>", args.name)
    else:
        script = script.replace("@\"<NAME>\"", "NULL")

    # path
    if args.path is not None:
        script = script.replace("<PATH>", args.path)
    else:
        script = script.replace("@\"<PATH>\"", "NULL")

    _ = util.exp_script(
        debugger,
        script,
        lang=lldb.eLanguageTypeObjC
    )
