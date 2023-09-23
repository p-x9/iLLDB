import lldb
from typing import Optional


def asInt(self: lldb.SBValue) -> Optional[int]:
    if self.IsValid():
        try:
            value_str = self.GetValue()
            return int(value_str, 0)
        except BaseException:
            return None
    else:
        return None


def asFloat(self: lldb.SBValue) -> Optional[float]:
    if self.IsValid():
        try:
            value_str = self.GetValue()
            return float(value_str)
        except BaseException:
            return None
    else:
        return None


def asBool(self: lldb.SBValue) -> Optional[bool]:
    if self.IsValid():
        value_str = self.GetValue()
        if value_str == 'true' or value_str == 'TRUE' or value_str == 'YES':
            return True
        elif value_str == 'false' or value_str == 'FALSE' or value_str == 'NO':
            return False

        intValue = asInt(self)
        if intValue is not None:
            return intValue > 0
        else:
            return None
    else:
        return None


def asStr(self: lldb.SBValue) -> Optional[str]:
    if self.IsValid():
        summary: str = self.GetSummary()
        if summary is None:
            return None
        if summary.startswith('"') and summary.endswith('"') and len(summary) > 1:
            summary = summary[1:-1]
        elif summary.startswith('@"') and summary.endswith('"') and len(summary) > 2:
            summary = summary[2:-1]
        return summary
    else:
        return None


lldb.SBValue.asInt = asInt
lldb.SBValue.asFloat = asFloat
lldb.SBValue.asBool = asBool
lldb.SBValue.asStr = asStr
