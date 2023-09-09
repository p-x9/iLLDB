import lldb
import argparse


def exp_script(debugger: lldb.SBDebugger, script: str, lang: str = 'swift') -> str:
    ret = lldb.SBCommandReturnObject()
    interpreter = debugger.GetCommandInterpreter()
    interpreter.HandleCommand(f"exp -l{lang} -F Foundation -O --  {script}", ret)

    if not ret.HasResult():
        return str(ret.GetError())

    output = ret.GetOutput()
    return str(output)


class HelpFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass
