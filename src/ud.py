import lldb
import shlex
import argparse
from typing import Union, cast
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    debugger.HandleCommand('command script add -f ud.handle_command ud -h "UserDefault debugging[iLLDB]"')


def handle_command(
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
        internal_dict: dict) -> None:
    args: Union[list[str], argparse.Namespace] = shlex.split(command, posix=False)
    args = parse_args(cast(list[str], args))

    script = ""
    if args.suite:
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

    ret = util.exp_script(
        debugger,
        script,
        lang=lldb.eLanguageTypeObjC_plus_plus
    )
    if ret:
        result.AppendMessage(ret.GetObjectDescription())


def parse_args(args: list[str]) -> argparse.Namespace:
    description = "UserDefault debugging"
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=util.HelpFormatter)
    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    # read
    read_command = subparsers.add_parser("read",
                                         help="read UserDefault value",
                                         formatter_class=util.HelpFormatter)
    read_command.add_argument("--suite", type=str, help="suite for UserDefault")
    read_command.add_argument("key",
                              type=str,
                              help="key")

    # write
    write_command = subparsers.add_parser("write",
                                          help="write UserDefault value",
                                          formatter_class=util.HelpFormatter)
    write_command.add_argument("--suite", type=str, help="suite for UserDefault")
    write_command.add_argument("key",
                               type=str,
                               help="key")
    write_command.add_argument("value",
                               type=str,
                               help="value to set")
    write_command.add_argument("--type",
                               type=str,
                               default='str',
                               help="type of value to set['str', 'number']")

    # delete
    delete_command = subparsers.add_parser("delete",
                                           help="delete UserDefault value",
                                           formatter_class=util.HelpFormatter)
    delete_command.add_argument("--suite", type=str, help="suite for UserDefault")
    delete_command.add_argument("key",
                                type=str,
                                help="key")

    read_all = subparsers.add_parser("read-all",
                                     help="read all UserDefault value",
                                     formatter_class=util.HelpFormatter)
    read_all.add_argument("--suite", type=str, help="suite for UserDefault")

    delete_all = subparsers.add_parser("delete-all",
                                       help="delete all UserDefault value",
                                       formatter_class=util.HelpFormatter)
    delete_all.add_argument("--suite", type=str, help="suite for UserDefault")

    return parser.parse_args(args)
