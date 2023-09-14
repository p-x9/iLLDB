import os
import lldb
import argparse
from typing import Optional, cast


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
    options.SetFetchDynamicValue(lldb.eNoDynamicValues)
    options.SetUnwindOnError(True)
    options.SetGenerateDebugInfo(True)

    value: lldb.SBValue = frame.EvaluateExpression(script, options)
    error: lldb.SBError = value.GetError()

    if error.Success() or error.value == 0x1001:  # success or unknown error
        return value
    else:
        print(error)
        return None


def read_script_file(file_name: str) -> str:
    file_path = os.path.realpath(__file__)
    dir_name = os.path.dirname(file_path)

    file = open(f'{dir_name}/{file_name}', mode='r')
    text = file.read()
    file.close()

    return text


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


def isAppKit(debugger: lldb.SBDebugger) -> bool:
    script = """
    @import Foundation;
    Class app = NSClassFromString(@"NSApplication");
    BOOL val = (BOOL)(app != nil)
    val ? @"YES" : @"NO";
    """
    ret = exp_script(debugger, script, lang=lldb.eLanguageTypeObjC)

    if ret and ret.GetObjectDescription() == 'YES':
        return True
    else:
        return False


def isUIKit(debugger: lldb.SBDebugger) -> bool:
    script = """
    @import Foundation;
    Class app = NSClassFromString(@"UIApplication");
    BOOL val = (BOOL)(app != nil)
    val ? @"YES" : @"NO";
    """
    ret = exp_script(debugger, script, lang=lldb.eLanguageTypeObjC)
    if ret and ret.GetObjectDescription() == 'YES':
        return True
    else:
        return False


def isMacOS(debugger: lldb.SBDebugger) -> bool:
    model = sysctlbyname(debugger, "hw.model")
    if model:
        return 'Mac' in model and not isIOSSimulator(debugger)
    else:
        return isAppKit(debugger)


def isIOS(debugger: lldb.SBDebugger) -> bool:
    machine = sysctlbyname(debugger, "hw.machine")
    if machine:
        return 'iP' in machine or isIOSSimulator(debugger)
    else:
        return isUIKit(debugger)


def sysctlbyname(debugger: lldb.SBDebugger, key: str) -> Optional[str]:
    script = f"""
    @import Foundation;
    int sysctlbyname(const char *, void *, size_t *, void *, size_t);

    size_t size = 0;
    sysctlbyname("{key}", NULL, &size, NULL, 0);
    char *machine = (char *)malloc(size);
    sysctlbyname("{key}", machine, &size, NULL, 0);

    NSString *result = [NSString stringWithUTF8String:machine];
    free(machine);
    result;
    """

    ret = exp_script(debugger, script, lang=lldb.eLanguageTypeObjC)
    if ret:
        return cast(str, ret.GetObjectDescription())
    else:
        return None


class HelpFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass
