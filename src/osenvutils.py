# Licensed under the LGPL 3.0 License.
# simplepylibs by numlinka.
# osenvutils

__name__ = "osenvutils"
__version__ = "1.1.2"
__author__ = "numlinka"
__license__ = "LGPL 3.0"
__copyright__ = "Copyright (C) 2022 numlinka"

version = (1, 1, 2)

# std
import os
import sys
import locale
import datetime
import subprocess
import time as _time
from typing import Any


class DateTimeVariable (object):
    date: str
    time: str
    microsecond: int
    timestamp: int
    timestamp_ms: int
    timestamp_us: int

    timetuple: _time.struct_time

    timestamp_hex: str
    timestamp_hex_up: str
    timestamp_hex_simple: str
    timestamp_hex_simple_up: str
    timestamp_ms_hex: str
    timestamp_ms_hex_up: str
    timestamp_ms_hex_simple: str
    timestamp_ms_hex_simple_up: str
    timestamp_us_hex: str
    timestamp_us_hex_up: str
    timestamp_us_hex_simple: str
    timestamp_us_hex_simple_up: str


    def __getattr__(self, __name: str) -> Any:
        now = datetime.datetime.now()

        match __name:
            case "date":
                return now.strftime("%Y-%m-%d")

            case "time":
                return now.strftime("%H:%M:%S")

            case "microsecond":
                return now.strftime("%f")

            case "timestamp":
                return int(now.timestamp())

            case "timestamp_ms":
                return int(now.timestamp() * 10 ** 3)

            case "timestamp_us":
                return int(now.timestamp() * 10 ** 6)

            case "timetuple":
                return now.timetuple() 

            case "timestamp_hex":
                return hex(self.timestamp)

            case "timestamp_hex_up":
                return self.timestamp_hex.upper().replace("X", "x")

            case "timestamp_hex_simple":
                return self.timestamp_hex.replace("0x", "")

            case "timestamp_hex_simple_up":
                return self.timestamp_hex_up.replace("0x", "")

            case "timestamp_ms_hex":
                return hex(self.timestamp_ms)

            case "timestamp_ms_hex_up":
                return self.timestamp_ms_hex.upper().replace("X", "x")

            case "timestamp_ms_hex_simple":
                return self.timestamp_ms_hex.replace("0x", "")

            case "timestamp_ms_hex_simple_up":
                return self.timestamp_ms_hex_up.replace("0x", "")

            case "timestamp_us_hex":
                return hex(self.timestamp_us)

            case "timestamp_us_hex_up":
                return self.timestamp_us_hex.upper().replace("X", "x")

            case "timestamp_us_hex_simple":
                return self.timestamp_us_hex.replace("0x", "")

            case "timestamp_us_hex_simple_up":
                return self.timestamp_us_hex_up.replace("0x", "")

        raise AttributeError(__name)



def get_system_uuid() -> str:
    """
    ## get system UUID
    ## 获取系统 UUID

    获取失败时返回一个空字符串
    """
    try:
        if sys.platform == "win32":
            result = subprocess.check_output("wmic csproduct get UUID", shell=True)
            bios_uuid = result.decode("utf-8").replace("UUID", "").strip()
            return bios_uuid

        elif sys.platform == "linux":
            result = subprocess.check_output("dmidecode -s system-uuid", shell=True)
            bios_uuid = result.decode("utf-8").strip()
            return bios_uuid

        elif sys.platform == "darwin":
            return ""

        else:
            return ""

    except Exception as _:
        return ""


def get_locale_alias() -> str:
    """
    ## get system locale alias
    ## 获取系统语言别名

    获取失败时返回一个空字符串
    """

    ors = os.environ.get("LANG", "")
    return ors.split(".")[0]



now = DateTimeVariable()
UUID = get_system_uuid()

CURRENT_WORKING_DIRECTORY = os.getcwd()
CWD = CURRENT_WORKING_DIRECTORY

LOCALE_NAME = locale.getlocale()[0]
LOCALE_ALIAS = get_locale_alias()
ENCODEING = locale.getencoding()


__all__ = [
    "UUID",
    "CWD",
    "CURRENT_WORKING_DIRECTORY",
    "LOCALE_NAME",
    "LOCALE_ALIAS",
    "ENCODEING"
]
