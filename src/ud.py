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
        script += "@import Foundation;\nNSUserDefaults *userDefaults = [[NSUserDefaults alloc] initWithSuiteName:suiteName];\n"
    else:
        script += "@import Foundation;\nNSUserDefaults *userDefaults = [NSUserDefaults standardUserDefaults];\n"

    if args.read:
        key = args.read
        script += f"(id)(@[userDefaults objectForKey:@\"{key}\"]);"
    elif args.write:
        key = args.write
        type = args.type
        value = args.value
        if type == "number":
            script += f"[userDefaults setObject:@({value}) forKey:@\"{key}\"];"
        else:
            script += f"[userDefaults setObject:@\"{value}\" forKey:@\"{key}\"];"
    elif args.delete:
        key = args.delete
        script += f"[userDefaults removeObjectForKey:@\"{key}\"];"
    elif args.read_all:
        script += "[userDefaults dictionaryRepresentation];"
    elif args.delete_all:
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
    parser.add_argument("--read", "-r", type=str, help="read UserDefault value")
    parser.add_argument("--write", "-w", type=str, help="write UserDefault value")
    parser.add_argument("--delete", type=str, help="delete UserDefault value")

    parser.add_argument("--type",
                        type=str,
                        default='str',
                        help="type of value to set['str', 'number']")
    parser.add_argument("value",
                        nargs='?',
                        default='',
                        type=str,
                        help="value to set")

    parser.add_argument("--read-all", action="store_true", help="read all UserDefault value")
    parser.add_argument("--delete-all", action="store_true", help="read all UserDefault value")

    parser.add_argument("--suite", type=str, help="suite for UserDefault")

    return parser.parse_args(args)
