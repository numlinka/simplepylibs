# Licensed under the LGPL 3.0 License.
# simplepylibs by numlinka.
# internationalization

# std
import os
import threading
from typing import Any

# requirements
try:
    import strutils

except ImportError as _:
    from . import strutils


__name__ = "internationalization"
__author__ = "numlinka"
__license__ = "LGPL 3.0"
__copyright__ = "Copyright (C) 2022 numlinka"

__version_info__ = (1, 1, 1)
__version__ = ".".join(map(str, __version_info__))


class I18nString (str): ...



class Internationalization (object):
    __class_name__ = "Internationalization"

    def __init__(self):
        self.__call_lock = threading.RLock()

        self.__lang_setn = ""
        self.__lang_base = "en_US"

        self.__lang_table = {}


    def _con_set_lang(self, value: str) -> None:
        with self.__call_lock:
            self.__lang_setn = value


    def _con_get_lang(self) -> str:
        with self.__call_lock:
            result = self.__lang_setn if self.__lang_setn else self.__lang_base

        return result


    def _con_get_langs(self) -> list[str]:
        with self.__call_lock:
            lst = [x for x in self.__lang_table]

        return lst


    def _con_add_value(self, type_: str, key: str, value: str):
        if not isinstance(type_, str):
            raise TypeError("The type_ type is not str.")

        if not isinstance(key, str):
            raise TypeError("The key type is not str.")

        if not isinstance(value, str):
            raise TypeError("The value type is not str.")

        with self.__call_lock:
            if type_ not in self.__lang_table:
                self.__lang_table[type_] = {}

            self.__lang_table[type_][key] = value


    def _con_get_self_value(self, target: str) -> str:
        try:
            for indexed, __name in enumerate(target.split(".")):
                # result = super().__getattribute__(__name) if indexed == 0 else result.__getattribute__(__name)
                result = super().__getattribute__(__name) if indexed == 0 else getattr(result, __name)

            if not isinstance(result, str):
                result = str(result)

        except Exception as _:
            result = target

        return result


    def _con_get_value(self, target: str) -> I18nString:
        with self.__call_lock:

            table = self.__lang_table.get(self.__lang_setn, {})
            result = table.get(target, None)

            if result is None:
                table = self.__lang_table.get(self.__lang_base, {})
                result = table.get(target, None)

            if result is None:
                result = self._con_get_self_value(target)

            reply = I18nString(result)
            reply._set_attribute(self, target)
            return reply


    def _con_load_file(self, path: str, type_: str = ..., superiors: str = ...) -> None:
        """
        ## Load language file
        ## 加载语言文件

        ```TEXT
        args:
            path: Language file path, usually a file ending with ".lang".
                  语言文件路径, 通常是以 ".lang" 结尾的文件.

            type_: Language type, such as "en_US", defaults to the file name.
                   语言类型, 例如 "en_US", 默认为文件名.

            superiors: Add a superiors, which may be used when loading multiple language files of the same type,
                       This parameter is invalid if the language file has the "#define superiors xxx" field.
                       增加父级, 加载多个同类型的语言文件时可能会用到,
                       若语言文件有 "#define superiors xxx" 字段时该参数无效.
        ```
        """
        if not isinstance(path, str):
            raise TypeError("The path type is not str.")

        if not isinstance(type_, str) and type_ is not Ellipsis:
            raise TypeError("The type_ type is not str.")

        if not isinstance(superiors, str) and superiors is not Ellipsis:
            raise TypeError("The superiors type is not str.")

        if not os.path.isfile(path):
            raise FileNotFoundError("Let's perform a magic trick and make this file appear.")

        # with self.__call_lock:
        # If "type_" is not specified then it is set to the filename.
        # 若未指定 "type_" 则将其设置为文件名.
        if type_ is Ellipsis:
            type_ = os.path.basename(path)
            index = type_.rfind(".")
            if index != -1:
                type_ = type_[:index]

        if superiors is Ellipsis:
            superiors = ""

        # Appended if "superiors" does not end with "." .
        # 如果 "superiors" 不以 "." 结尾, 则附加.
        if superiors and not superiors.endswith("."):
            superiors += "."

        with open(path, "r", encoding="utf-8") as fobj:
            contents = fobj.readlines()

        multiline_mode = False
        multiline_cont = ""

        for line in contents:
            if line.startswith("#define superiors "):
                superiors = line.split("#define superiors ", 1)[1].split(" ")[0].strip()

                if superiors and not superiors.endswith("."):
                    superiors += "."

                continue

            if multiline_mode:
                value = line.strip()

                if value.endswith(" +\\"):
                    multiline_mode = True
                    value = value[:-3]

                else:
                    multiline_mode = False

                if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

                value = strutils.escape_character_recognition(value)
                multiline_cont += f"\n{value}"

                if multiline_mode:
                    continue

                self._con_add_value(type_, key, multiline_cont)
                multiline_cont = ""

            else:
                lst = line.split("=", 1)

                if len(lst) == 1:
                    continue

                key = superiors + lst[0].strip()
                value = lst[1].strip()

                if value.endswith(" +\\"):
                    multiline_mode = True
                    value = value[:-3]

                if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

                value = strutils.escape_character_recognition(value)

                if multiline_mode:
                    multiline_cont = value
                    continue

                self._con_add_value(type_, key, value)


    def _con_load_dir(self, path: str, type_: str = ..., superiors: str = ...) -> list[str]:
        """
        ## Load language directory
        ## 加载语言文件夹(目录)

        ```TEXT
        args:
            path: Path to the folder containing language files ending in ".lang".
                  包含以 ".lang" 结尾的语言文件的文件夹路径.

            type_: Language type, such as "en_US", defaults to the directory name.
                   语言类型, 例如 "en_US", 默认为目录名.

            superiors: Add a superiors, which may be used when loading multiple language files of the same type,
                       This parameter is invalid if the language file has the "#define superiors xxx" field.
                       增加父级, 加载多个同类型的语言文件时可能会用到,
                       若语言文件有 "#define superiors xxx" 字段时该参数无效.

        return:
            list[str]
            File failed to load.
            加载失败的文件.
        ```
        """
        if not isinstance(path, str):
            raise TypeError("The path type is not str.")

        if not isinstance(type_, str) and type_ is not Ellipsis:
            raise TypeError("The type_ type is not str.")

        if not isinstance(superiors, str) and superiors is not Ellipsis:
            raise TypeError("The superiors type is not str.")

        if not os.path.isdir(path):
            raise FileNotFoundError("Let's perform a magic trick and make this dir appear.")

        # with self.__call_lock:
        exception_list = []
        if type_ is Ellipsis:
            type_ = os.path.basename(path)

        if superiors is Ellipsis:
            superiors = ""

        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if not filename.endswith(".lang"):
                    continue

                filepath = os.path.join(dirpath, filename)

                try:
                    self._con_load_file(filepath, type_, superiors)

                except Exception as _:
                    exception_list.append(filepath)

        return exception_list


    def _con_load_auto(self, path: str) -> list[str]:
        """
        ## Automatically load language files
        ## 自动加载语言文件

        ```TEXT
        args:
            path: Directory to store language files.
                  存放语言文件的目录.

        return:
            list[str]
            Project that failed to load.
            加载失败的项目.
        ```
        """
        if not isinstance(path, str):
            raise TypeError("The path type is not str.")

        if not os.path.isdir(path):
            raise FileNotFoundError("Let's perform a magic trick and make this dir appear.")

        exception_list = []
        for basename in os.listdir(path):
            target_path = os.path.join(path, basename)

            try:
                if os.path.isfile(target_path):
                    self._con_load_file(target_path)

                if os.path.isdir(target_path):
                    exception_list += self._con_load_dir(target_path)

            except Exception as _:
                exception_list.append(target_path)

        return exception_list


    def __getattribute__(self, __name: str) -> Any:
        superiors = super()

        # _con_ is identified by the action method, so it should not be overloaded.
        # _Internationalization represents access to its own private attributes, so it should not be overloaded.
        # ! Note that this method is not reliable.
        if __name.startswith("_con_") or __name.startswith("_Internationalization"):
            return superiors.__getattribute__(__name)

        # __xxx__ is used to identify magic methods, so it should not be overloaded.
        if __name.startswith("__") and __name.endswith("__"):
            return superiors.__getattribute__(__name)

        # I want to return a string whenever I access any other attribute,  我想在访问其他属性时返回一个字符串
        # However, the "." operation cannot be overloaded,                  但是 "." 操作符不能被重载
        # So this returns a special string object.                          所以这里返回一个特殊的字符串对象
        # This allows access to attributes of any depth,                    这将允许访问任何深度的属性
        # And it can always return a string object.                         且它总是可以返回一个字符串对象

        # reply = I18nString(self._con_get(__name))
        # reply._set_attribute(self, __name)
        # return reply
        return self._con_get_value(__name)



class I18nString (str):
    def _set_attribute(self, visit: Internationalization, prefixion: str = ""):
        self.__visit = visit
        self.__prefixion = prefixion


    def __getattr__(self, __name: str):
        target = __name if self.__prefixion == "" else f"{self.__prefixion}.{__name}"
        return self.__visit._con_get_value(target)


    def sformat(self, *args, **kwds):
        result = self
        for indexed, value in enumerate(args):
            result = result.replace("{" + f"{indexed}" + "}", f"{value}")

        for key, value in kwds.items():
            result = result.replace("{" + f"{key}" + "}", f"{value}")

        return result



__all__ = [
    "Internationalization",
    "I18nString"
]
