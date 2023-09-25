import lldb
import shlex
import argparse
from typing import Union, cast
from LLDBHelper.LLDBCommandBase import LLDBCommandBase
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    UserDefaultsCommnad.register_lldb_command(debugger, UserDefaultsCommnad.__module__)


class UserDefaultsCommnad(LLDBCommandBase):

    @classmethod
    def cmdname(cls) -> str:
        return 'ud'

    @classmethod
    def description(cls) -> str:
        return 'UserDefault debugging. [iLLDB]'

    def create_argparser(self) -> argparse.ArgumentParser:
        description = "UserDefault debugging"
        parser = argparse.ArgumentParser(description=description,
                                         formatter_class=util.HelpFormatter)
        subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

        # read
        read_command = subparsers.add_parser("read",
                                             help="Read UserDefault value",
                                             formatter_class=util.HelpFormatter)
        read_command.add_argument("--suite", type=str, help="Suite for UserDefault")
        read_command.add_argument("key",
                                  type=str,
                                  help="key")

        # write
        write_command = subparsers.add_parser("write",
                                              help="Write UserDefault value",
                                              formatter_class=util.HelpFormatter)
        write_command.add_argument("--suite", type=str, help="Suite for UserDefault")
        write_command.add_argument("key",
                                   type=str,
                                   help="Key")
        write_command.add_argument("value",
                                   type=str,
                                   help="Value to set")
        write_command.add_argument("--type",
                                   type=str,
                                   default='str',
                                   help="Type of value to set['str', 'number']")

        # delete
        delete_command = subparsers.add_parser("delete",
                                               help="Delete UserDefault value",
                                               formatter_class=util.HelpFormatter)
        delete_command.add_argument("--suite", type=str, help="Suite for UserDefault")
        delete_command.add_argument("key",
                                    type=str,
                                    help="Key")

        read_all = subparsers.add_parser("read-all",
                                         help="Read all UserDefault value",
                                         formatter_class=util.HelpFormatter)
        read_all.add_argument("--suite", type=str, help="Suite for UserDefault")

        delete_all = subparsers.add_parser("delete-all",
                                           help="Delete all UserDefault value",
                                           formatter_class=util.HelpFormatter)
        delete_all.add_argument("--suite", type=str, help="Suite for UserDefault")

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

        if args.subcommand is None:
            self.argparser.print_help()
            exit(0)

        script = ""
        if args.suite is not None:
            script += """
            @import Foundation;
            NSUserDefaults *userDefaults = [[NSUserDefaults alloc] initWithSuiteName:suiteName];
            """
        else:
            script += """
            @import Foundation;
            NSUserDefaults *userDefaults = [NSUserDefaults standardUserDefaults];
            """

        if args.subcommand == "read":
            key = args.key
            script += f"""({{
            id val = [userDefaults stringForKey:@\"{key}\"];
            if (val != nil) {{
                printf("\\"%s\\"", (char*)[val UTF8String]);
            }} else {{
                val = [userDefaults objectForKey:@\"{key}\"];
            }}
            val;
            }})
            """
        elif args.subcommand == "write":
            key = args.key
            type = args.type
            value = args.value
            if type == "number":
                script += f"[userDefaults setObject:@({value}) forKey:@\"{key}\"];"
            else:
                script += f"[userDefaults setObject:@\"{value}\" forKey:@\"{key}\"];"
        elif args.subcommand == "delete":
            key = args.key
            script += f"[userDefaults removeObjectForKey:@\"{key}\"];"
        elif args.subcommand == "read-all":
            script += "[userDefaults dictionaryRepresentation];"
        elif args.subcommand == "delete-all":
            script += r"""
            NSDictionary *allUserDefaults = [userDefaults dictionaryRepresentation];

            for (NSString *key in [allUserDefaults allKeys]) {
                [userDefaults removeObjectForKey:key];
            }
            """
        else:
            self.argparser.print_help()
            exit(0)

        ret = util.exp_script(
            debugger,
            script,
            lang=lldb.eLanguageTypeObjC_plus_plus
        )
        if ret:
            result.AppendMessage(ret.GetObjectDescription())
