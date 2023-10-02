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
    args = shlex.split(command, posix=False)
    if len(args) < 1:
        return
    script = f"""
    import Foundation
    let mirror = Mirror(reflecting: {args[0]})
    mirror.children.enumerated().forEach {{
        print("\\($1.label ?? "[\\($0)]"): \\($1.value)")
    }}
    """
    util.exp_script(
        debugger,
        script,
        lang=lldb.eLanguageTypeSwift
    )
