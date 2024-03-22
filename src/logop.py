# Licensed under the LGPL 3.0 License.
# simplepylibs by numlinka.
# logop

__name__ = "logop"
__version__ = "1.2.0"
__author__ = "numlinka"
__license__ = "LGPL 3.0"
__copyright__ = "Copyright (C) 2022 numlinka"

version = (1, 2, 0)

# std
import os
import sys
import inspect
import datetime
import threading
import traceback
import multiprocessing

from types import FrameType
from typing import Any, Union, Iterable, Callable, Mapping


ALL      = ~ 0x7F
TRACE    = ~ 0x40
DEBUG    = ~ 0x20
INFO     =   0x00
WARN     =   0x20
WARNING  =   0x20
SEVERE   =   0x30
ERROR    =   0x40
CRITICAL =   0x60
FATAL    =   0x60
OFF      =   0x7F

TRACE_NAME    = "TRACE"
DEBUG_NAME    = "DEBUG"
INFO_NAME     = "INFO"
WARN_NAME     = "WARN"
WARNING_NAME  = "WARNING"
SEVERE_NAME   = "SEVERE"
ERROR_NAME    = "ERROR"
FATAL_NAME    = "FATAL"
CRITICAL_NAME = "CRITICAL"

TRACE_ALIAS    = "trace"
DEBUG_ALIAS    = "debug"
INFO_ALIAS     = "info"
WARN_ALIAS     = "warn"
WARNING_ALIAS  = "warning"
SEVERE_NAME    = "severe"
ERROR_ALIAS    = "error"
FATAL_ALIAS    = "fatal"
CRITICAL_ALIAS = "critical"

LEVEL_TABLE = {
    TRACE_ALIAS    : (TRACE,    TRACE_NAME),
    DEBUG_ALIAS    : (DEBUG,    DEBUG_NAME),
    INFO_ALIAS     : (INFO,     INFO_NAME),
    WARN_ALIAS     : (WARN,     WARN_NAME),
    WARNING_ALIAS  : (WARNING,  WARNING_NAME),
    SEVERE_NAME    : (SEVERE,   SEVERE_NAME),
    ERROR_ALIAS    : (ERROR,    ERROR_NAME),
    FATAL_ALIAS    : (FATAL,    FATAL_NAME),
    CRITICAL_ALIAS : (CRITICAL, CRITICAL_NAME)
}
# ? LEVEL_TABLE[alias] = [level, levelname]

LEVEL = "level"
LEVELNAME = "levelname"
DATE = "date"
TIME = "time"
MOMENT = "moment"
MICRO = "micro"
FILE = "file"
FILEPATH = "filepath"
FILENAME = "filename"
PROCESS = "process"
THREAD = "thread"
FUNCTION = "function"
LINE = "line"
MESSAGE = "message"
MARK = "mark"

FORMAT_SIMPLE = "[$(.levelname)] $(.message)"
FORMAT_DEFAULT = "[$(.date) $(.time)] [$(.thread)/$(.levelname)] $(.message)"
FORMAT_DEBUG = "[$(.date) $(.time).$(.moment)] $(.file) [$(.thread)/$(.levelname)] [line:$(.line)] $(.message)"

FORMAT_DEFAULT_EXTEND = "[$(.date) $(.time)] [$(.thread)/$(.levelname)] $(.message) ($(.mark))"
FORMAT_DEBUG_EXTEND = "[$(.date) $(.time).$(.moment)] $(.file) [$(.thread)/$(.levelname)] [line:$(.line)] $(.message) ($(.mark))"

_VARIABLE_TABLE = """ $(variable)
.level      日志等级
.levelname  等级名称
.date       日期
.time       时间
.moment     毫秒
.micro      微秒
.file       文件相对路径
.filepath   文件绝对路径
.filename   文件名
.process    进程名
.thread     线程名
.function   函数
.line       行
.message    消息
.mark       标记名称
"""

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"


class LogopBaseException (Exception):
    """Logop base exception."""

class LoggingIsClosedError (LogopBaseException, RuntimeError):
    """Logging is closed"""

class LogLevelAliasNotFoundError (LogopBaseException):
    """The log level alias does not exist"""

class LogLevelExceedsThresholdError (LogopBaseException):
    """The log level exceeds the threshold."""

class LogFormatInvalidError (LogopBaseException):
    """The log format is invalid."""

class TooManyStandardTypeLogopObjectError (LogopBaseException):
    """Too many Logop objects of standard type."""

class ExistingLoggingError (LogopBaseException):
    """Existing logging."""

class LogopIdentNotFoundError (LogopBaseException):
    """The logop ident does not exist."""



class BaseLogop (object):
    """Log output object."""
    op_name = "standard" # Object name, used to distinguish objects of the same type.
    op_type = "standard" # An object type that distinguishes its implementation
    op_ident = 0 # It's unique in the logger where it's located.
    op_logging_object = None
    op_exception_count = 0


    def __init__(self, name: str = ..., **_):
        self.op_name = name if isinstance(name, str) else "standard"


    def call(self, content: dict, op_format: str = FORMAT_DEFAULT) -> None:
        if not isinstance(content, dict):
            raise TypeError("The content type is not dict.")

        if not isinstance(op_format, str):
            raise TypeError("The op_format type is not str.")

        if "$(.message)" not in op_format:
            raise ValueError("$(.message) must be included in format.")


    def add_exception_count(self) -> None:
        self.op_exception_count += 1


    def get_logging_onject(self) -> Union[object, None]:
        return self.op_logging_object



class Logging (object):
    def __init__(self, level: Union[str, int] = INFO, op_format: str = FORMAT_DEFAULT,
                 *, stdout: bool = True, asynchronous: bool = False, threadname: str = "LoggingThread"):
        """
        level: Log Level, Logs below this level are filtered.

        op_format: Log format, The format of the output log content,
        `Logging` does not process the log content, but passes it to the `Logop` object.

        stdout: Standard output, Automatically initializes a `LogopStandard` object in the output object list.

        asynchronous: Asynchronous mode, Let Logging run in a separate thread of control.

        threadname: Thread name, Sets the thread name of Logging, effective only when `asynchronous` is `True`.
        """
        self.__level = INFO
        self.__op_format = FORMAT_DEFAULT
        self.__op_list = []

        self.__call_lock = threading.RLock()
        self.__set_lock = threading.RLock()
        self.__is_close = False

        self.set_level(level)
        self.set_format(op_format)

        if stdout: self.add_op(LogopStandard())

        self.__asynchronous = bool(asynchronous)

        if self.__asynchronous:
            self.__call_event = threading.Event()
            self.__message_list = []
            self.__asynchronous_stop = False
            self.__asynchronous_task = threading.Thread(None, self.__async_mainloop, threadname, (), {}, daemon=False)
            self.__asynchronous_task.start()

        with _state._lock:
            if _state.logging is not ...: return
            _state.logging = self


    def __close_check(self) -> None:
        with self.__set_lock:
            if not self.__is_close:
                return

            raise LoggingIsClosedError("Logging is closed.")


    def set_level(self, level: Union[int, str]) -> None:
        """## Setting the log Level.

        Logs below this level are filtered.
        """
        self.__close_check()

        with self.__set_lock:
            if isinstance(level, int):
                lv = level

            elif isinstance(level, str):
                if level not in LEVEL_TABLE:
                    raise LogLevelAliasNotFoundError("The level alias does not exist.")

                lv = LEVEL_TABLE[level][0]

            else:
                raise TypeError("The level type is not int.")

            if not ALL <= lv <= OFF:
                raise LogLevelExceedsThresholdError("The level should be somewhere between -0x80 to 0x7F .")

            self.__level = lv


    def set_format(self, op_format: str) -> None:
        """## Setting log format.

        The format of the output log content,
        `Logging` does not process the log content, but passes it to the `Logop` object.
        """
        self.__close_check()

        with self.__set_lock:
            if not isinstance(op_format, str):
                raise TypeError("The op_format type is not str.")

            if "$(.message)" not in op_format:
                raise LogFormatInvalidError("$(.message) must be included in format.")

            self.__op_format = op_format


    def add_op(self, target: BaseLogop) -> None:
        """Adds the output object to the list"""
        self.__close_check()

        with self.__set_lock:
            if not isinstance(target, BaseLogop):
                raise TypeError("The target type is not Logop object.")

            if len(self.__op_list) > 0x10:
                raise Warning("There are too many Logop objects.")

            standard = BaseLogop.op_type
            typelist = [x.op_type for x in self.__op_list]

            if standard in typelist and target.op_type == standard:
                raise TooManyStandardTypeLogopObjectError("Only one standard op_object can exist.")

            if target.op_logging_object is not None:
                raise ExistingLoggingError("This logop already has logging.")

            target.op_logging_object = self

            identlist = [x.op_ident for x in self.__op_list]
            if identlist:
                ident = max(identlist) + 1
            else:
                ident = 1

            target.op_ident = ident

            self.__op_list.append(target)


    def del_op(self, ident: int) -> None:
        """Removes the output object from the list."""
        with self.__set_lock:
            for index, op in enumerate(self.__op_list):
                op: BaseLogop
                if op.op_ident == ident:
                    break

            else:
                raise LogopIdentNotFoundError("The ident value does not exist.")

            op = self.__op_list.pop(index)
            op: BaseLogop
            op.op_logging_object = None


    def get_op_list(self) -> list[dict]:
        """Gets a list of output object information."""
        with self.__set_lock:
            answer = []
            for item in self.__op_list:
                item: BaseLogop
                answer.append({
                    "op_ident": item.op_ident,
                    "op_name": item.op_name,
                    "op_type": item.op_type,
                    "exception_count": item.op_exception_count
                })
            return answer


    def get_op_count(self) -> int:
        """Gets the number of output objects."""
        with self.__set_lock:
            count = len(self.__op_list)
            return count


    def get_op_object(self, ident: int) -> Union[BaseLogop, None]:
        """Get output object."""
        with self.__set_lock:
            for opobj in self.__op_list:
                opobj: BaseLogop
                if opobj.op_ident == ident:
                    return opobj

            else:
                return None


    def get_stdop_object(self) -> Union[BaseLogop, None]:
        """## Gets the standard output object.

        Gets the standard output object in the output object list,
        Returns `None` when no standard output object exists.
        """
        with self.__set_lock:
            for opobj in self.__op_list:
                opobj: BaseLogop
                if opobj.op_type == BaseLogop.op_type:
                    return opobj

            else:
                return None


    def get_stdop_ident(self) -> Union[int, None]:
        """## Gets the ident of the standard output object.

        Gets the ident of the standard output object,
        Returns `None` when no standard output object exists.
        """
        with self.__set_lock:
            for opobj in self.__op_list:
                opobj: BaseLogop
                if opobj.op_type == BaseLogop.op_type:
                    return opobj.op_ident

            else:
                return None


    def join(self, timeout: Union[float, None] = None) -> None:
        """Wait for the log thread until the thread ends or a timeout occurs."""
        self.__close_check()

        if not self.__asynchronous:
            raise RuntimeError("The logging mode is not asynchronous.")

        return self.__asynchronous_task.join(timeout)


    def close(self) -> None:
        """Close logging."""
        self.__close_check()

        with self.__set_lock:
            self.__is_close = True

            if self.__asynchronous:
                self.__asynchronous_stop = True
                self.__call_event.set()


    def is_close(self) -> bool:
        """Logging is close."""
        with self.__set_lock:
            return self.__is_close


    def __try_op_call(self, content: dict) -> None:
        """Try to pass the log message to the output object."""
        with self.__set_lock:
            call_list = self.__op_list.copy()

        with self.__call_lock:
            for stdop in call_list:
                try: stdop.call(content, self.__op_format)
                except Exception:
                    try: stdop.add_exception_count()
                    except Exception: ...


    def __try_op_call_asynchronous(self) -> None:
        """Try to pass the log message to the output object, in asynchronous mode."""
        with self.__call_lock:
            if not len(self.__message_list): return None

            content = self.__message_list[0]
            del self.__message_list[0]

        self.__try_op_call(content)

        with self.__call_lock:
            if not len(self.__message_list): return None
            else: self.__try_op_call_asynchronous()


    def __async_mainloop(self, *args, **kwds):
        """Asynchronous mode threading task."""
        while not self.__asynchronous_stop:
            self.__call_event.wait()
            self.__try_op_call_asynchronous()
            self.__call_event.clear()


    def __run_call_asynchronous(self, content: dict) -> None:
        """Preparing output logs, in asynchronous mode."""
        with self.__call_lock: self.__message_list.append(content)
        self.__call_event.set()


    def __run_call(self, content: dict) -> None:
        """Preparing output logs."""
        if self.__asynchronous: self.__run_call_asynchronous(content)
        else: self.__try_op_call(content)


    def call(self, level: int = INFO, levelname: str = INFO_NAME, message: str = "", mark: str = "",
             *, back_count: int = 0) -> None:
        """## Output log.

        level: Log level.

        levelname: Level name.

        message: Message content.

        mark: Additional tag name (extended content), which is not output by the default log format.

        back_count: If you need to get status from an outer stack, you need to increase this number appropriately.
        """
        self.__close_check()

        if level < self.__level: return

        now = datetime.datetime.now()

        content = {}
        content[LEVEL] = level
        content[LEVELNAME] = levelname
        content[MESSAGE] = message
        # content[MARK] = mark

        content[DATE] = now.strftime(DATE_FORMAT)
        content[TIME] = now.strftime(TIME_FORMAT)
        content[MOMENT] = now.strftime("%f")[:3]
        content[MICRO] = now.strftime("%f")[3:]

        content[PROCESS] = multiprocessing.current_process().name
        content[THREAD] = threading.current_thread().name

        current_frame = inspect.currentframe()
        frame = current_frame

        for _ in range(back_count + 1):
            frame = frame.f_back

        content[MARK] = mark if mark else frame.f_globals.get("__name__", "")

        abspath = os.path.abspath(frame.f_code.co_filename)
        local = os.path.join(sys.path[0], "")
        slen = len(local)
        if abspath[:slen] == local: file = abspath[slen:]
        else: file = abspath

        content[FILE] = file
        content[FILEPATH] = abspath
        content[FILENAME] = os.path.basename(file)
        content[FUNCTION] = frame.f_code.co_name
        content[LINE] = frame.f_lineno

        self.__run_call(content)


    def trace(self, message: object = "", mark: str = "", *, back_count: int = 0):
        self.call(TRACE, TRACE_NAME, message, mark, double_back=back_count+1)


    def debug(self, message: object = "", mark: str = "", *, back_count: int = 0):
        self.call(DEBUG, DEBUG_NAME, message, mark, back_count=back_count+1)


    def info(self, message: object = "", mark: str = "", *, back_count: int = 0):
        self.call(INFO, INFO_NAME, message, mark, back_count=back_count+1)


    def warn(self, message: object = "", mark: str = "", *, back_count: int = 0):
        self.call(WARN, WARN_NAME, message, mark, back_count=back_count+1)


    def warning(self, message: object = "", mark: str = "", *, back_count: int = 0):
        self.call(WARNING, WARNING_NAME, message, mark, back_count=back_count+1)


    def severe(self, message: object = "", mark: str = "", *, back_count: int = 0):
        self.call(SEVERE, SEVERE_NAME, message, mark, back_count=back_count+1)


    def error(self, message: object = "", mark: str = "", *, back_count: int = 0):
        self.call(ERROR, ERROR_NAME, message, mark, back_count=back_count+1)


    def fatal(self, message: object = "", mark: str = "", *, back_count: int = 0):
        self.call(FATAL, FATAL_NAME, message, mark, back_count=back_count+1)


    def critical(self, message: object = "", mark: str = "", *, back_count: int = 0):
        self.call(CRITICAL, CRITICAL_NAME, message, mark, back_count=back_count+1)


    def __get_call(self, alias: str = INFO_ALIAS):
        """Output logs using custom log levels"""
        def call_table(message: object = "", mark: str = "", *, back_count: int = 0):
            nonlocal self
            nonlocal alias
            level, name = LEVEL_TABLE[alias]
            self.call(level, name, message, mark, back_count=back_count+1)

        return call_table


    def __getattr__(self, __name):
        if __name in LEVEL_TABLE: return self.__get_call(__name)
        else: raise LogLevelAliasNotFoundError("This alias is not defined in the level table.")



class LogopStandard (BaseLogop):
    """Standard log output object.

    Output log information to the console.
    """
    def call(self, content: dict, op_format: str = FORMAT_DEFAULT) -> None:
        super().call(content, op_format)

        op = op_character_variable(op_format, content)
        ops = f"{op}\n"
        level = content.get("level", 0)

        if level < ERROR:
            sys.stdout.write(ops)
            sys.stdout.flush()

        else:
            sys.stderr.write(ops)
            sys.stderr.flush()



class LogopStandardPlus (BaseLogop):
    """Standard log output object. Plus.

    Outputs the colored log information to the console.
    """
    def __init__(self, name: str = ..., **_):
        super().__init__(name)
        self.__color_code = {
            INFO: "30",
            WARN: "0",
            ERROR: "1;33",
            OFF: "1;31",
        }
        set_windows_console_mode()


    def _get_color_code(self, level) -> str:
        for astrict_level, color_code in self.__color_code.items():
            if level < astrict_level:
                return color_code

        else:
            return "0"


    def call(self, content: dict, op_format: str = FORMAT_DEFAULT) -> None:
        super().call(content, op_format)

        op = op_character_variable(op_format, content)
        level = content.get("level", 0)

        color_code = self._get_color_code(level)

        ops = f"\033[{color_code}m{op}\033[0m\n"

        if level < ERROR:
            sys.stdout.write(ops)
            sys.stdout.flush()

        else:
            sys.stderr.write(ops)
            sys.stderr.flush()



class LogopFile (BaseLogop):
    """Log file Indicates the log output object.

    Output log information to a log file.
    """
    op_name = "logfile"
    op_type = "logfile"


    def __init__(self, name: str = "logfile", pathdir: Union[str, Iterable] = "logs",
                 pathname: str = "$(.date).log", encoding: str = "utf-8"):
        super().__init__(name)

        if not isinstance(pathdir, (str, Iterable)):
            raise TypeError("The pathdir type is not str or Iterable.")

        if not isinstance(pathname, str):
            raise TypeError("The pathname type is not str.")

        if isinstance(pathdir, str):
            self._pathdir = pathdir

        elif isinstance(pathdir, Iterable):
            self._pathdir = os.path.join(*pathdir)

        else:
            raise Exception("Errors that should not occur.")

        self._pathname = pathname
        self._encoding = encoding


    def call(self, content: dict, op_format: str = FORMAT_DEFAULT) -> None:
        super().call(content, op_format)

        targetdir = op_character_variable(self._pathdir, content)
        targetname = op_character_variable(self._pathname, content)
        targetfile = os.path.join(targetdir, targetname)

        op = op_character_variable(op_format, content)
        ops = f"{op}\n"
        if not os.path.isdir(targetdir):
            os.makedirs(targetdir)

        with open(targetfile, "a", encoding=self._encoding) as fob:
            fob.write(ops)
            fob.flush()



class _Atomic (object):
    def __init__(self):
        self.value: int
        self.__lock = threading.RLock()
        self.__count = 0


    def __getattr__(self, __name: str) -> Any:
        if __name != "value":
            return super().__getattr__(__name)

        with self.__lock:
            value = self.__count
            self.__count += 1
            return value



class _state (object):
    _lock = threading.RLock()
    logging: Logging = ...

    track_callee = True
    track_result = True
    track_except = False



def op_character_variable(op_format: str, table: dict) -> str:
    if not isinstance(op_format, str):
        raise TypeError("The op_format type is not str.")

    if not isinstance(table, dict):
        raise TypeError("The table type is not dict.")

    op = op_format
    for key, value in table.items():
        op = op.replace(f"$(.{key})", f"{value}")

    return op


def set_windows_console_mode():
    if sys.platform == "win32":
        try:
            from ctypes import windll
            kernel32 = windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True

        except ImportError:
            return False

    return False


def callabletrack(
        function: Callable = ..., *, callee: bool = ..., result: bool = ...,
        exception: bool = ..., logging: Logging = ..., level: str | int = ...
        ):
    s_function = function
    s_state = _state()
    if isinstance(callee, bool): s_state.track_callee = callee
    if isinstance(result, bool): s_state.track_result = result
    if isinstance(exception, bool): s_state.track_except = exception
    if isinstance(logging, Logging): s_state.logging = logging

    s_level_alias = TRACE_ALIAS


    def level_correct(reference: str | int = ...):
        nonlocal s_level_alias

        if reference is Ellipsis:
            s_level_alias = TRACE_ALIAS

        elif isinstance(reference, (str, int)):
            for lv_alias, (lv, lv_name) in LEVEL_TABLE.items():
                if reference in [lv_alias, lv, lv_name]:
                    s_level_alias = lv_alias
                    break

            else:
                s_level_alias = TRACE_ALIAS

        else:
            s_level_alias = TRACE_ALIAS


    def log(level_alias: str = ..., message: str = "", mark: str = "", *, back_count: int = 0):
        nonlocal s_state, s_level_alias

        if level_alias is Ellipsis:
            level_alias = s_level_alias

        level, levelname = LEVEL_TABLE[level_alias]

        if isinstance(s_state.logging, Logging):
            s_state.logging.call(level, levelname, message, mark, back_count=back_count+1)
            return

        return


    def log_callee(iid: int, caller_frame: FrameType, args: Iterable, kwds: Mapping, *, back_count: int = 0):
        nonlocal s_state, s_function

        if not s_state.track_callee: return
        msg = f"calltrack iid-{iid}\n"
        msg += f"\tcaller: File \"{caller_frame.f_code.co_filename}\", line {caller_frame.f_lineno} in {caller_frame.f_code.co_name}\n"
        msg += f"\tcallee: File \"{s_function.__code__.co_filename}\", line {s_function.__code__.co_firstlineno} in {s_function.__name__}\n"
        msg += f"\targs: {args}\n\tkwds: {kwds}\n\twait return"
        log(..., msg, back_count=back_count+1)


    def log_result(iid: int, result: Any, *, back_count: int = 0):
        nonlocal s_state

        if not s_state.track_result: result
        msg = f"calltrack iid-{iid} return: {result}"
        log(..., msg, back_count=back_count+1)


    def shell(*args, **kwds):
        nonlocal s_state, s_function

        iid = _atomic.value

        currentframe = inspect.currentframe()
        # caller_frame = sys._getframe(1)
        caller_frame = currentframe.f_back
        log_callee(iid, caller_frame, args, kwds, back_count=1)

        if s_state.track_except:
            try:
                result = s_function(*args, **kwds)

            except Exception as e:
                exc = traceback.format_exc()
                log(ERROR_ALIAS, exc, back_count=1)
                raise e
                return

        else:
            result = s_function(*args, **kwds)

        log_result(iid, result, back_count=1)


    def decorate(function: Callable):
        nonlocal s_function

        s_function = function
        return shell


    level_correct(level)

    if callable(function):
        return shell

    else:
        return decorate


_atomic = _Atomic()


__all__ = [
    "ALL",
    "TRACE",
    "DEBUG",
    "INFO",
    "WARN",
    "WARNING",
    "SEVERE",
    "ERROR",
    "CRITICAL",
    "FATAL",
    "OFF",

    "TRACE_NAME",
    "DEBUG_NAME",
    "INFO_NAME",
    "WARN_NAME",
    "WARNING_NAME",
    "SEVERE_NAME",
    "ERROR_NAME",
    "FATAL_NAME",
    "CRITICAL_NAME",

    "TRACE_ALIAS",
    "DEBUG_ALIAS",
    "INFO_ALIAS",
    "WARN_ALIAS",
    "WARNING_ALIAS",
    "SEVERE_NAME",
    "ERROR_ALIAS",
    "FATAL_ALIAS",
    "CRITICAL_ALIAS",

    "LEVEL",
    "LEVELNAME",
    "DATE",
    "TIME",
    "MOMENT",
    "MICRO",
    "FILE",
    "FILEPATH",
    "FILENAME",
    "PROCESS",
    "THREAD",
    "FUNCTION",
    "LINE",
    "MESSAGE",
    "MARK",

    "FORMAT_SIMPLE",
    "FORMAT_DEFAULT",
    "FORMAT_DEBUG",
    "FORMAT_DEFAULT_EXTEND",
    "FORMAT_DEBUG_EXTEND",

    "LogopBaseException",
    "LoggingIsClosedError",
    "LogLevelAliasNotFoundError",
    "LogLevelExceedsThresholdError",
    "LogFormatInvalidError",
    "TooManyStandardTypeLogopObjectError",
    "ExistingLoggingError",
    "LogopIdentNotFoundError",

    "Logging",

    "BaseLogop",
    "LogopStandard",
    "LogopStandardPlus",
    "LogopFile",

    "op_character_variable",
    "callabletrack"
]
