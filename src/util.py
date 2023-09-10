import lldb
import argparse
from typing import Optional


def exp_script(
        debugger: lldb.SBDebugger,
        script: str,
        lang: int = lldb.eLanguageTypeSwift) -> Optional[lldb.SBValue]:

    frame: lldb.SBFrame = (
        debugger.GetSelectedTarget()
        .GetProcess()
        .GetSelectedThread()
        .GetSelectedFrame()
    )

    if not frame:
        return None

    options = lldb.SBExpressionOptions()
    options.SetLanguage(lang)
    options.SetIgnoreBreakpoints(True)
    options.SetTrapExceptions(False)
    options.SetTryAllThreads(True)
    options.SetFetchDynamicValue(lldb.eDynamicCanRunTarget)
    options.SetUnwindOnError(True)
    options.SetGenerateDebugInfo(True)

    value: lldb.SBValue = frame.EvaluateExpression(script, options)
    error: lldb.SBError = value.GetError()

    if error.Success() or error.value == 0x1001:  # success or unknown error
        return value
    else:
        print(error)
        return None


def isIOSSimulator(debugger: lldb.SBDebugger) -> bool:
    script = """
    @import Foundation;
    NSString *name = [[[NSProcessInfo processInfo] environment] objectForKey:@"SIMULATOR_DEVICE_NAME"];
    name;
    """
    ret = exp_script(debugger, script, lang=lldb.eLanguageTypeObjC)
    if ret:
        result: str = ret.GetObjectDescription()
        return result != "<nil>"
    else:
        return False


class HelpFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass
