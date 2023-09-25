import lldb
import shlex
import argparse
import subprocess
from typing import Union, cast
from lldbhelper import LLDBCommandBase
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    FileCommnad.register_lldb_command(debugger, FileCommnad.__module__)


class FileCommnad(LLDBCommandBase):

    @classmethod
    def cmdname(cls) -> str:
        return 'file'

    @classmethod
    def description(cls) -> str:
        return 'File debugging. [iLLDB]'

    def create_argparser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="File debugging",
                                         formatter_class=util.HelpFormatter)
        subparsers = parser.add_subparsers(title="Subcommands",
                                           dest="subcommand")

        tree_command = subparsers.add_parser("tree",
                                             help="Show file hierarchie",
                                             formatter_class=util.HelpFormatter)
        tree_command.add_argument("-b", "--bundle", action="store_true", help="bundle directory")
        tree_command.add_argument("-l", "--library", action="store_true", help="library directory")
        tree_command.add_argument("--documents", action="store_true", help="documents directory")
        tree_command.add_argument("--tmp", action="store_true", help="tmp directory")
        tree_command.add_argument("--depth", type=int, help="Maximum depth to be displayed")

        open_command = subparsers.add_parser("open",
                                             help="Open directory with Finder (Simulator Only)",
                                             formatter_class=util.HelpFormatter)
        open_command.add_argument("-b", "--bundle", action="store_true", help="bundle directory")
        open_command.add_argument("-l", "--library", action="store_true", help="library directory")
        open_command.add_argument("--documents", action="store_true", help="documents directory")
        open_command.add_argument("--tmp", action="store_true", help="tmp directory")

        cat_command = subparsers.add_parser("cat",
                                            help="The content of the specified file is retrieved and displayed",
                                            formatter_class=util.HelpFormatter)
        cat_command.add_argument("path",
                                 type=str,
                                 help="path")
        cat_command.add_argument("--mode", type=str, default='text', help="mode [text, plist]")

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
        elif args.subcommand == "open":
            self.open(args, debugger, result)
        elif args.subcommand == "cat":
            self.cat(args, debugger, result)
        else:
            self.argparser.print_help()

    def tree(self, args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
        script = util.read_script_file('swift/file.swift')

        depth = 'nil'
        if args.depth is not None:
            try:
                depth = str(int(args.depth))
            except ValueError:
                pass

        if args.bundle:
            script += f"listFilesInDirectory(Bundle.main.bundleURL, depth: {depth})"
        elif args.library:
            script += f"listFilesInDirectory(FileManager.default.urls(for: .libraryDirectory, in: .userDomainMask).first!, depth: {depth})"
        elif args.documents:
            script += f"listFilesInDirectory(FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!, depth: {depth})"
        elif args.tmp:
            script += f"listFilesInDirectory(FileManager.default.temporaryDirectory, depth: {depth})"
        elif args.path:
            script += f"listFilesInDirectory(URL(fileURLWithPath: {args.path}), depth: {depth})"

        _ = util.exp_script(
            debugger,
            script
        )

    def open(self, args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
        if not (util.isIOSSimulator(debugger) or util.isMacOS(debugger)):
            print("Supported only simulator or macOS")
            return

        shell = "open -R "

        script = ""
        if args.bundle:
            script += "Bundle.main.bundlePath"
        elif args.library:
            script += "FileManager.default.urls(for: .libraryDirectory, in: .userDomainMask).first!.path"
        elif args.documents:
            script += "FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!.path"
        elif args.tmp:
            script += "FileManager.default.temporaryDirectory.path"
        elif args.path:
            shell += f"{args.path}"

        if script != "":
            ret = util.exp_script(debugger, script)
            if ret:
                print(ret.asStr())
                shell += f"{ret.GetObjectDescription()}"

        subprocess.run(shell, shell=True)

    def cat(self, args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
        script = util.read_script_file('objc/cat.m')
        script = script.replace("<FILE_PATH>", args.path)
        script = script.replace("<MODE>", args.mode)

        _ = util.exp_script(
            debugger,
            script,
            lang=lldb.eLanguageTypeObjC
        )
