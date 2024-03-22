# Licensed under the LGPL 3.0 License.
# logop by numlinka.
# example

# std
import sys
from typing import NoReturn
sys.path.append("src")
sys.path.append("../src")

# libs
import logop


# Example executing too fast? Set the value below to True and let’s go through it step by step.
# 示例执行速度太快? 将下面的值设置为 True, 让我们一步一步来.
__step_by_step__ = False

s = lambda: input() if __step_by_step__ else None


# Let's start.
# 让我们开始吧


# Instantiate a logger object and make some settings.
# 实例化一个记录器对象并做一些设置.
logging = logop.Logging(stdout=False)
logging.set_level(logop.ALL)
logging.set_format(logop.FORMAT_DEBUG_EXTEND)

logging.add_op(logop.LogopStandardPlus())
logging.info("Let's start.")



s()
# Do some simple log output.
# 进行一些简单的日志输出.
logging.debug("This is a debug message.")
logging.info("This is a info message.")
logging.warn("This is a warn message.")
logging.error("This is a error message.")
logging.fatal("This is a fatal message.")



s()
# You can also define the log level yourself,
# You just need to add it to LEVEL_TABLE in the format alias: (level, name)
# 你也可以自己定义日志等级,
# 你只需要以 alias: (level, name) 的格式将它添加到 LEVEL_TABLE 中.
logop.LEVEL_TABLE["lookatme"] = (0x10, "LOOK-AT-ME")
# Then you can access it directly using this alias as an attribute.
# Don't worry about this non-existent attribute, it will be overloaded internally.
# 然后你可以使用此别名作为属性直接访问它.
# 不用担心这个不存在的属性, 它会在内部被重载.
logging.lookatme("You have to believe me.")



s()
# Of course, you can also use the call attribute to output any level of logs.
# 当然你也可以使用 call 属性来输出任何级别的日志.
logging.call(logop.DEBUG, "NAME_YOU_LIKE", "Log message.")
# Or wrap it into a function.
# 或者将它包装成一个函数.
def log_fate(message: object = ""):
    logging.call(logop.DEBUG, "FATE", message)

log_fate("My fate is mine.")



s()
# At this time you will find a problem.
# The status obtained by the logger is in log_fate, not when calling log_fate.
# At this point you need to increase the value of back_count.
# The more times you wrap, the more values you need to increase.
# 这时候你就会发现一个问题.
# 记录器获取的状态是在 log_fate 中, 而不是调用 log_fate 时.
# 此时你需要增加 back_count 的值,
# 包装的次数越多需要增加的值越多.
def log_fate(message: object = "", *, back_count: int = 0):
    logging.call(logop.DEBUG, "FATE", message, back_count=back_count+1)

log_fate("I control my own life.")



s()
# Adding the callabletrack decorator to a function can track who called the function,
# what parameters were passed, and the return value of the function.
# 为函数加上 callabletrack 装饰器可以追踪函数被谁调用、传递了哪些参数以及函数的返回值.
@logop.callabletrack
def fuck_you_nvidia(v: str) -> int:
    logging.warn(v)
    return 0

fuck_you_nvidia("fuck you nvidia")



s()
# This decorator can also be used on the method of object.
# 这个装饰器也可以用在对象的方法上.
class ObjectMethodTest (object):
    @logop.callabletrack
    def fuck_you_intel(self, v: str) -> int:
        logging.warn(v)
        return 1

omt = ObjectMethodTest()
omt.fuck_you_intel("fuck you intel")



s()
# You can modify the value of the _state attribute to modify what callabletrack will log.
# Although I don't recommend you to do this.
# 你可以修改 _state 属性的值以修改 callabletrack 会记录的内容.
# 虽然我不建议你这样做.
logop._state.track_callee = False

@logop.callabletrack
def why_not_fuck_amd() -> NoReturn:
    ...

why_not_fuck_amd()



s()
# You can set its properties individually when the callabletrack is created.
# Set the decorator's exception to True and it will log exceptions that occur within the function.
# Note that this does not prevent exceptions from being raise.
# 你可以在 callabletrack 建立时单独设置它的属性.
# 将装饰器的 exception 设置为 True, 它就会记录函数内发生的异常.
# 注意这并不会阻止异常被 raise.
@logop.callabletrack(exception=True)
def do_not_be_anxious() -> ZeroDivisionError:
    return 10086 / 0

try:
    do_not_be_anxious()
except ZeroDivisionError as _:
    logging.fatal("ZeroDivisionError")



s()
# Is the default log level too low? It doesn't matter, let's modify it。
# 默认的日志等级太低? 没有关系, 让我们来修改一下.
@logop.callabletrack(level=logop.WARN)
def fuck_you_amd(v: str) -> str:
    return v

fuck_you_amd("fuck you amd")
