import lldb
import shlex
import util


@lldb.command('mirror', doc='Display child elements using Mirror. [iLLDB]')
def mirror(
    debugger: lldb.SBDebugger,
    command: str,
    exe_ctx: lldb.SBExecutionContext,
    result: lldb.SBCommandReturnObject,
    internal_dict: dict
) -> None:
    """
    Display the child elements of an object using the Mirror class in Swift.

    Args:
        debugger (lldb.SBDebugger): The LLDB debugger object.
        command (str): The command string passed to the mirror command.
        exe_ctx (lldb.SBExecutionContext): The execution context of the command.
        result (lldb.SBCommandReturnObject): The object used to return the result of the command.
        internal_dict (dict): The internal dictionary of the command.
    """
    args = shlex.split(command, posix=False)
    if len(args) < 1:
        return
    script = f"""
    import Foundation
    let mirror = Mirror(reflecting: {args[0]})
    mirror.children.enumerated().forEach {{
        print("\\($1.label ?? "[\\($0)]"): \\(String(reflecting: type(of: $1.value))) = \\($1.value)")
    }}
    """
    util.exp_script(
        debugger,
        script,
        lang=lldb.eLanguageTypeSwift
    )
