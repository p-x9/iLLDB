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

    tree_command = subparsers.add_parser("tree",
                                         help="Show view hierarchie",
                                         formatter_class=util.HelpFormatter)
    tree_command.add_argument("-d", "--detail", action="store_true", help="Enable detailed mode")
    tree_command.add_argument("-s", "--simple", action="store_true", help="Enable simpled mode")
    tree_command.add_argument("--depth", type=int, help="Maximum depth to be displayed")

    tree_command.add_argument("--window", type=str, help="Specify the target window")
    tree_command.add_argument("--view", type=str, help="Specify the target view")
    tree_command.add_argument("--vc", type=str, help="Specify the target viewController")
    tree_command.add_argument("--layer", type=str, help="Specify the target CALayer")

    return parser.parse_args(args)


def tree(args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
    file_path = os.path.realpath(__file__)
    dir_name = os.path.dirname(file_path)

    script_ret = subprocess.run(f"cat {dir_name}/swift/tree.swift", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    mode = 'normal'
    if args.detail:
        mode = 'detail'
    if args.simple:
        mode = 'simple'

    depth = 'nil'
    if args.depth is not None:
        try:
            depth = str(int(args.depth))
        except ValueError:
            pass

    script = ''

    if util.isUIKit(debugger):
        script += """
        import UIKit
        typealias NSUIView = UIView
        typealias NSUIViewController = UIViewController
        typealias NSUIWindow = UIWindow
        typealias NSUIApplication = UIApplication
        """
    elif util.isAppKit(debugger):
        script += """
        import AppKit
        typealias NSUIView = NSView
        typealias NSUIViewController = NSViewController
        typealias NSUIWindow = NSWindow
        typealias NSUIApplication = NSApplication
        """

    script += script_ret.stdout
    if args.window:
        script += f"\n windowHierarchy({args.window}, mode: \"{mode}\", depth: {depth})"
    elif args.view:
        script += f"\n viewHierarchy({args.view}, mode: \"{mode}\", depth: {depth})"
    elif args.vc:
        script += f"\n viewControllerHierarchy({args.vc}, mode: \"{mode}\", depth: {depth})"
    elif args.layer:
        script += f"\n layerHierarchy({args.layer}, mode: \"{mode}\", depth: {depth})"
    else:
        script += f"\n windowHierarchy(NSUIApplication.shared.keyWindow, mode: \"{mode}\", depth: {depth})"

    _ = util.exp_script(
        debugger,
        script
    )
