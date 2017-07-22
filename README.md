# Biohub-Server

[![Build Status](https://travis-ci.org/hsfzxjy/Biohub-Server.svg)](https://travis-ci.org/hsfzxjy/Biohub-Server)

**[组内文档](https://github.com/hsfzxjy/Biohub-Server/wiki)**

## 配置及开发相关要求

### 关于环境

#### 系统依赖

 + Python >= 3.5.0
 + MySQL 及对应的 dev 包
 + Windows 下需要 C/C++ 编译环境（如 MinGW）

#### virtualenv

**建议在 `virtualenv` 环境下开发**，以防全局包污染及可能产生的权限问题。使用 `pyvenv` 或 `virtualenvwrapper` 生成虚拟环境。

#### pip 源

**建议将 `pip` 的源切换至国内，如使用阿里云、豆瓣的源**。以豆瓣源为例，找到或创建 `pip` 的配置文件（Windows 下为 `%HOMEPATH%\pip\pip.ini`，Linux 下为 `~/.pip/pip.conf`），加入以下内容：

```
[global]
trusted-host=pypi.douban.com
index-url=https://pypi.douban.com/simple
[install]
trusted-host=https://pypi.douban.com/simple
```

#### manage.py

`~/biohub/manage.py` 为开发时高频命令，**建议将其符号链接至全局可见的位置**（`pyvenv` 下为 `<env_dir>/bin/` 目录，`virtualenvwrapper` 下为 `$VIRTUAL_ENV/bin/` 目录）。

#### 安装开发时依赖

```bash
pip install -r requirements/dev.txt
```

### 关于编码规范

为减少不必要的麻烦，本次开发需遵守 [PEP 8](http://legacy.python.org/dev/peps/pep-0008/) 规范。执行 `manage.py codestyle` 可对整个项目进行规范检查。

为保证被提交的代码都是符合规范的，**要求将以下内容加入 `<project_dir>/.git/hooks/pre-commit` 中**：

```bash
#!/bin/sh

# 如果能保证在虚拟环境下执行 commit，下面这句可以省略
. <path_to_venv>/bin/activate

# 若 manage.py 全局不可见，此处需添加其路径
manage.py codestyle
codestyleresult=$?

if [ $codestyleresult -ne 0 ]; then
	exit 1
fi
```

### 关于编辑器

 + 建议为编辑器装上有“按 PEP8 规范格式化代码”的插件
 + **请勿将编辑器的配置文件留在项目中**
 + **所有文件使用 UTF-8（无 BOM）编码保存**

### 关于项目结构

```bash
├── biohub/ # biohub主目录
│   ├── accounts/ # 账户系统
│   ├── compat/ # 兼容性代码
│   ├── core/ # biohub 核心模块，包括插件系统和自定义脚本
│   ├── main/ # biohub 主模块，包括配置文件
│   │   ├── settings
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   ├── prod.py
│   ├── manage.py
│   └── utils/ # 工具模块
├── config.json.example # 自定义配置文件，使用时需复制为 config.json 再做修改
├── docs/ # 文档的源文件
├── LICENSE
├── mkdocs.yml # 文档的配置文件
├── README.md
├── requirements/ # 依赖文件
│   ├── base.txt
│   ├── codestyle-base.txt
│   ├── dev.txt
│   ├── doc-base.txt
│   └── test-base.txt
└── tests/ # 测试文件
```

### 关于 config.json

鉴于开发过程中各成员的系统配置（如数据库密码等）难以保持一致，我将配置中需要个性化的部分单独抽出来做成一个接口，以方便开发。此接口日后也可能成为产品逻辑的一部分，使用户无需深入项目中修改 `settings` 文件即可完成配置工作。截至目前，此处只暴露了数据库接口。

默认内容如下：

```json
{
    "DATABASE": {
        "NAME": "",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
        "TEST": {
            "NAME": ""
        }
    }
}
```

此文件已加入 `.gitignore`，请勿将其提交出来。默认在项目的根目录下寻找此文件，你也可以通过设置环境变量 `BIOHUB_CONFIG_PATH` 指定文件的位置：

```bash
BIOHUB_CONFIG_PATH=other/path/config.json manage.py runserver
```

### 关于测试

测试使用 `pytest` 框架。为了更好的开发体验，`manage.py test` 命令已被重写。执行 `manage.py test` 即可测试 `tests/` 中的文件。

测试需要用到一个测试数据库，名称可在 `config.json` 的 `DATABASE.TEST.NAME` 字段中指定。为了加速测试，`pytest` 的 `--reuse-db` 选项默认被开启，从而不必每次测试时都重建测试数据库。当数据库表结构有更改时，需执行 `manage.py test --recreate` 重构测试数据库。通过指定子路径可以更改测试文件的查找范围，如 `manage.py test accounts` 只会在 `tests/accounts/` 下查找测试文件。

### 关于日志

建议使用 python 自带的日志功能代替 `print` 进行调试输出。日志级别已设置为 `DEBUG`，并带有彩色输出（需支持 ANSI Escape Code 的 Terminal）和相关调试信息（行号、模块等）。日志推荐使用方式：

```python
import logging

logger = logging.getLogger(__name__)

logger.debug('DEBUG message')
logger.info('INFO message')
logger.warn('WARNING message')
# ...
```

### 杂项

 + 不要直接在 `master` 分支上工作
 + Windows 环境下请打开 git 的 `Auto CRLF` 选项（`git config --global core.autocrlf true`，默认已开启）以保持跨平台兼容性
 + `manage.py startapp` 命令已被重写，默认在 `biohub/` 下创建 app 目录
 + `manage.py` 已将 **项目的根目录** 加入 python 的搜索路径中，为防止包冲突，引用 `biohub` 中模块时需使用完整路径（如 `biohub.accounts.models.User` 而不是 `accounts.models.User`）,相对导入时除外
