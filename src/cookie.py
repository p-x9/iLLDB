import lldb
import shlex
import argparse
from typing import Union, cast
from LLDBHelper.LLDBCommandBase import LLDBCommandBase
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    CookieCommnad.register_lldb_command(debugger, CookieCommnad.__module__)


class CookieCommnad(LLDBCommandBase):

    @classmethod
    def cmdname(cls) -> str:
        return 'cookie'

    @classmethod
    def description(cls) -> str:
        return 'HTTP Cookie debugging. [iLLDB]'

    def create_argparser(self) -> argparse.ArgumentParser:
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

        # delete
        delete_command = subparsers.add_parser("delete",
                                               help="Delete Cookie",
                                               formatter_class=util.HelpFormatter)
        delete_command.add_argument("--group-id", type=str, help="AppGroup identifier for cookie storage")
        delete_command.add_argument("--domain", type=str, help="Domain for Cookie")
        delete_command.add_argument("--name", type=str, help="Name for Cookie")
        delete_command.add_argument("--path", type=str, help="Path for Cookie")

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

        if args.subcommand == "read":
            self.read(args, debugger, result)
        elif args.subcommand == "delete":
            self.read(args, debugger, result)
            confirm = input('The above cookies will be deleted. Please type "Yes" if OK\n')
            if confirm == "Yes":
                self.delete(args, debugger, result)
            else:
                print("Cancelled")
        else:
            self.argparser.print_help()

    def read(self, args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
        script = ""
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

    def delete(self, args: argparse.Namespace, debugger: lldb.SBDebugger, result: lldb.SBCommandReturnObject) -> None:
        script = ""
        if args.group_id is not None:
            script += f'NSHTTPCookieStorage *storage = [NSHTTPCookieStorage sharedCookieStorageForGroupContainerIdentifier:@"{args.group_id}"];\n'
        else:
            script += "NSHTTPCookieStorage *storage = [NSHTTPCookieStorage sharedHTTPCookieStorage];\n"

        script += util.read_script_file('objc/cookie_delete.m')

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
