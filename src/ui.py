import lldb
import shlex
import argparse
from typing import Union, cast
from lldbhelper import LLDBCommandBase
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    UICommnad.register_lldb_command(debugger, UICommnad.__module__)


class UICommnad(LLDBCommandBase):

    @classmethod
    def cmdname(cls) -> str:
        return 'ui'

    @classmethod
    def description(cls) -> str:
        return 'UI debugging. [iLLDB]'

    def create_argparser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="UI debugging",
                                         formatter_class=util.HelpFormatter)
        subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

        tree_command = subparsers.add_parser("tree",
                                             help="Show view hierarchie",
                                             formatter_class=util.HelpFormatter)
        tree_command.add_argument("-d", "--detail", action="store_true", help="Enable detailed mode")
        tree_command.add_argument("-s", "--simple", action="store_true", help="Enable simpled mode")
        tree_command.add_argument("--depth", type=int, help="Maximum depth to be displayed")
        tree_command.add_argument("--with-address", action="store_true", help="Print address of ui")

        tree_command.add_argument("--window", type=str, help="Specify the target window")
        tree_command.add_argument("--view", type=str, help="Specify the target view (property or address)")
        tree_command.add_argument("--vc", type=str, help="Specify the target viewController (property or address)")
        tree_command.add_argument("--layer", type=str, help="Specify the target CALayer (property or address)")

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

        if args.subcommand == "tree":
            self.tree(args, debugger, result)
        else:
            self.argparser.print_help()

    def tree(self, args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
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

        with_address = 'true' if args.with_address else 'false'

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

        self.resolve_adress(args)

        script += util.read_script_file('swift/tree.swift')
        if args.window is not None:
            script += f"\n windowHierarchy({args.window}, mode: \"{mode}\", depth: {depth}, address: {with_address})"
        elif args.view is not None:
            script += f"\n viewHierarchy({args.view}, mode: \"{mode}\", depth: {depth}, address: {with_address})"
        elif args.vc is not None:
            script += f"\n viewControllerHierarchy({args.vc}, mode: \"{mode}\", depth: {depth}, address: {with_address})"
        elif args.layer is not None:
            script += f"\n layerHierarchy({args.layer}, mode: \"{mode}\", depth: {depth}, address: {with_address})"
        else:
            script += f"\n windowHierarchy(NSUIApplication.shared.keyWindow, mode: \"{mode}\", depth: {depth}, address: {with_address})"

        _ = util.exp_script(
            debugger,
            script
        )

    def resolve_adress(self, args: argparse.Namespace) -> None:
        try:
            if args.window is not None and int(args.window, 16):
                args.window = f"Unmanaged<NSUIWindow>.fromOpaque(.init(bitPattern: {args.window})!).takeUnretainedValue()"
            elif args.view is not None and int(args.view, 16):
                args.view = f"Unmanaged<NSUIView>.fromOpaque(.init(bitPattern: {args.view})!).takeUnretainedValue()"
            elif args.vc is not None and int(args.vc, 16):
                args.vc = f"Unmanaged<NSUIViewController>.fromOpaque(.init(bitPattern: {args.vc})!).takeUnretainedValue()"
            elif args.layer is not None and int(args.layer, 16):
                args.layer = f"Unmanaged<CALayer>.fromOpaque(.init(bitPattern: {args.layer})!).takeUnretainedValue()"
        except ValueError:
            pass
