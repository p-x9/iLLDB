import lldb
import os
import lldbhelper  # noqa: F401

iLLDB_VERSION = "0.6.1"


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    file_path = os.path.realpath(__file__)
    dir_name = os.path.dirname(file_path)
    load_commands(dir_name, debugger)
    print(f"[iLLDB] loaded: Version {iLLDB_VERSION}")


def load_commands(dir_name: str, debugger: lldb.SBDebugger) -> None:
    ignored_files = {"iLLDB.py"}

    for file in os.listdir(dir_name):
        full_path = dir_name + '/' + file

        if file in ignored_files:
            continue
        elif file.endswith('.py'):
            cmd = 'command script import '
        elif file.endswith('.h'):
            cmd = 'command source -e0 -s1 '
        elif os.path.isdir(full_path):
            load_commands(full_path, debugger)
            continue
        else:
            continue

        lldb.debugger.HandleCommand(cmd + full_path)
