import lldb
import shlex
import argparse
from typing import Union, cast
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    debugger.HandleCommand('command script add -f device.handle_command device -h "Device debugging. [iLLDB]"')


def handle_command(
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
        internal_dict: dict) -> None:
    parser = create_argparser()
    args: Union[list[str], argparse.Namespace] = shlex.split(command, posix=False)
    args = parser.parse_args(cast(list[str], args))

    if args.subcommand == "info":
        info(args, debugger, result)
    else:
        parser.print_help()


def create_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Device debugging",
                                     formatter_class=util.HelpFormatter)
    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    subparsers.add_parser("info",
                          help="Show device info",
                          formatter_class=util.HelpFormatter)

    return parser


def info(args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
    swift_file_name = "deviceMacOS" if util.isAppKit(debugger) else "deviceIOS"

    script = util.read_script_file(f'swift/{swift_file_name}.swift')
    script += """
    printDeviceInfo()
    """

    _ = util.exp_script(
        debugger,
        script
    )
