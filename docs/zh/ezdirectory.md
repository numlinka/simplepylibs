# ezdirectory

快速构建目录结构


## `Directory` 基础的目录构建类

基础的目录构建类，它已经被淘汰了，因此不推荐使用

`Directory` 继承自 `str` 

当你在尝试访问 `Directory` 中的字符串时，它会检查对应文件夹是否存在，并返回这个字符串

当你使用如下目录结构时

```TEXT
\
├── home
│   └── ...
│
├── resources
│   └── ...
│
└ ...
```

你可以尝试书写如下代码

```Python
from structure import *

class __directory (Directory):
    home = "home"
    resources = "resources"

directory = __directory()
```

你也可以尝试对他进行嵌套

```Python
from os.path import join
from structure import *

class __directory (Directory):
    home = "home"

    class __resources (Directory):
        preview = join("resources", "preview")
        cache = join("resources", "cache")

    resources = __resources("resources")

directory = __directory()
```

当然，这很麻烦，你必须自己书写完整的文件夹路径，并且它不支持记录文件路径


## `DirectoryPlus` 更好的目录构建类

更好的目录构建类，支持嵌套、文件夹别名、记录文件路径

`DirectoryPlus` 继承自 `str`

与 `Directory` 不同，在进行嵌套时不需要提供完整的路径

当你在尝试访问 `DirectoryPlus` 中的字符串时，它会检查并计算完整的文件夹路径<br/>
再检查对应文件夹是否存在，并返回这个字符串

现在让我们来实现如下目录结构

```TEXT
\
├── data
│   └── configuration
│
├── resources
│   ├── cache
│   │   └── ...
│   │
│   └── ...
│
└ favicon.ico
```

可以尝试书写如下代码

```Python
import os

from structure import *

current_working_directory = os.getcwd()

class __directory (DirectoryPlus):
    class data (DirectoryPlus): # data 文件夹下有子文件夹, 所以使用 DirectoryPlus 类
        # 在 DirectoryPlus 对象中的 DirectoryPlus 类可以不需要实例化
        # 可以提供 _value_ 值来表示文件夹名称
        # _value_ 不需要与 class name 相同
        # 在没有提供 _value_ 时则默认使用 class name
        _value_ = "data"

        # FilePath 对象表示这是一个文件的路径
        # DirectoryPlus 就不会尝试创建文件夹
        configuration = FilePath("configuration")

    class resources (DirectoryPlus):
        # cache 文件夹下没有子文件夹
        # 所以可以直接使用 str 类型
        cache = "cache"

    iconbitmap = FilePath("favicon.ico")


cwd = __directory(current_working_directory)
# 修改 _include_ 为 False
# 表示在计算路径时不包括自身 ( 返回相对路径 )
cwd._include_ = False

abscwd = __directory(current_working_directory)
# _include_ 默认为 True
# 表示在计算路径时包括自身 ( 返回绝对路径 )
```

在不访问其属性的情况下 `cwd` 和 `abscwd` 都是当前工作路径

而 `cwd` 在访问其属性的情况下会忽略自身的值返回相对路径

