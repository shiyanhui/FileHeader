==========
FileHeader
==========

Overview
========

FileHeader is a powerful file templating plugin for SublimeText 2 and SublimeText 3. It makes it easier to create new file with initial contents. It also can add new header to an existed file or directory.

:Info: FileHeader, a powerful file templating plugin for ST2/ST3.
:Author: Lime YH.Shi

Features
=========

- Add new file with initial contents.
- Auto detect **New File** action from SulimeText or other plugin.
- Add header to an existed file or directory.
- Batch add header to files in the specified directory.
- Auto update file last modified time and last modified by.
- Auto detect file type.
- Powerful template with Jinja2_.
- Custom templates supported.
- Rich languages supported.
- Support both Sublime Text 2 and Sublime Text 3.

Installation
============

Package Control
---------------

Install `Package Control`_. Then **Package Control: Install Package**, look for **FileHeader** and install it.

.. _Package Control: https://sublime.wbond.net/

Source Installation
--------------------

Go to the "Packages" directory **(Preferences / Browse Packages)**. Then clone this repository::

    git clone git@github.com:shiyanhui/FileHeader.git

Or download zip from Github, and put it in "Packages" directory **(Preferences / Browse Packages)**.

Releases
--------

See releases and logs `here <https://github.com/shiyanhui/FileHeader/releases>`_, it's stable.

Usage
=====

Create a new file
-----------------

- Sidebar Menu

    .. image:: https://raw.github.com/shiyanhui/shiyanhui.github.io/master/images/FileHeader/new-file.gif

- Shortcuts

    The default shortcuts is **super+alt+n** on OS X, **ctrl+alt+n** on Windows and Linux.

- Context Menu

    Similar to **Sidebar Menu**.

Add header to an existed file
-----------------------------

- Sidebar Menu

    .. image:: https://raw.github.com/shiyanhui/shiyanhui.github.io/master/images/FileHeader/add-header.gif

- Shortcuts

    The default shortcuts is **super+alt+a** on OS X, **ctrl+alt+a** on Windows and Linux.

- Context Menu

    Similar to **Sidebar Menu**.

Add header to files in the specified directory
----------------------------------------------

    .. image:: https://raw.github.com/shiyanhui/shiyanhui.github.io/master/images/FileHeader/add-header-dir.gif

A very important feature of FileHeader is that it can automatically update **last_modified_time** and **last_modified_by** (see options below). Just look this picture, take care of the **@Last modified time:** before save and after save:

.. image:: https://raw.github.com/shiyanhui/shiyanhui.github.io/master/images/FileHeader/update.gif


Settings
========

There are two kinds of arguments: **options** and kinds of languages variables settings. **options** is the functional setting, **Default** is the default language variables settings. Language variables setting will cover that in **Default**.

.. code-block:: c++

    {
        /*
        options
        =======
        */

        /*
        The datetime format.

            0: "%Y-%m-%d %H:%M:%S"
            1: "%Y-%m-%d"
            2: "%H:%M:%S"
        */
        "time_format": 0,
        /*
        The custom time format. It will format `create_time` and `last_modified_time`
        instead of `time_format` if you set it. The time format refers to`
        https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior`.
        */
        "custom_time_format": "",
        /*
        Whether add template to the empty file.

        It's useful when you create new file through other command, for
        example, the default Sublime Text's **New File...** or other plugin.
        */
        "enable_add_template_to_empty_file": true,
        /*
        Set your custom template header path here, it is a directory in which
        you write your own header files. The file name should be a language,
        "Python.tmpl" for example.
        */
        "custom_template_header_path": "",
        /*
        Set your custom template body path here, it is a directory in which
        you write your own body files. The file name should be a language,
        "Python.tmpl" for example.

        The template structure is:

            I am a file
            -----------
            header
            body

        */
        "custom_template_body_path": "",
        /*
        Whether show input panel when you add header. The default file which
        you add header to is the current file you edit.
        */
        "show_input_panel_when_add_header": true,
        /*
        Whether open file when you add header to files in the specified
        directory.
        */
        "open_file_when_add_header_to_directory": true,
        /*
        Whether enable add header to hidden directory. If false, FileHeader
        won't add header to files under it.
        */
        "enable_add_header_to_hidden_dir": false,
        /*
        Whether enable add header to hidden file. If false, FileHeader
        won't add header to it.
        */
        "enable_add_header_to_hidden_file": false,
        /*
        FileHeader judges programming language according file suffix.

        Default programming language if FileHeader judges failed when you
        create new file.
        */
        "syntax_when_not_match": "Text",
        /*
        FileHeader will judge programming language according to file suffix.
        You can add more file suffix here. Note: language should be one of
        that under **Default**. If FileHeader don't find the suffix,
        FileHeader will set language as **syntax_when_not_match** above.
        */
        "file_suffix_mapping": {
            "as": "ActionScript",
            "scpt": "AppleScript",
            "asp": "ASP",
            "aspx": "ASP",
            "bat": "Batch File",
            "cmd": "Batch File",
            "c": "C",
            "cs": "C#",
            "cpp": "C++",
            "clj": "Clojure",
            "css": "CSS",
            "D": "D",
            "erl": "Erlang",
            "go": "Go",
            "groovy": "Groovy",
            "hs": "Haskell",
            "htm": "HTML",
            "html": "HTML",
            "java": "Java",
            "js": "JavaScript",
            "tex": "LaTeX",
            "lsp": "Lisp",
            "lua": "Lua",
            "md": "Markdown",
            "mat": "Matlab",
            "m": "Objective-C",
            "ml": "OCaml",
            "p": "Pascal",
            "pl": "Perl",
            "php": "PHP",
            "py": "Python",
            "R": "R",
            "rst": "RestructuredText",
            "rb": "Ruby",
            "scala": "Scala",
            "sh": "ShellScript",
            "sql": "SQL",
            "tcl": "TCL",
            "txt": "Text",
            "xml": "XML"
        },
        /*
        Set special file suffix equivalence. Take `blade.php` for example,
        FileHeader will initial file with suffix `blade.php` with that of `html`.

        */
        "extension_equivalence": {
            "blade.php": "html",
        },

        /*
        Variables
        =========
        */

        /*
        Below is the variables you render templater.
        */
        "Default": {
            /*
            Builtin Variables
            =================

            - create_time

                The file created time. It will be automatically set when you create
                a new file if you use it.

                Can't be set custom.

            - author

                The file creator.

                FileHeader will set it automatically. If it's in
                a git repository and the `user.name` has been set, `autor`
                will set to `user.name`, otherwise it will be set to current
                system user.

                Can be set custom.

            - last_modified_by

                The file last modified by who? It is specially useful when
                cooperation programming.

                FileHeader will set it automatically. If it's in
                a git repository and the `user.name` has been set, `autor`
                will set to `user.name`, otherwise it will be set to current
                system logined user.

                Can be set custom.

            - last_modified_time

                The file last modified time.

                FileHeader will set it automatically when you save the file.

                Can't be set custom.

            - file_path

                The absolute path of the current file.

                FileHeader will update it automatically when you change it.

                Can't be set custom.

            - file_name

                The name of current file with extension.

                FileHeader will update it automatically when you change it.

                Can't be set custom.

            - file_name_without_extension

                The name of current file without extension.

                FileHeader will update it automatically when you change it.

                Can't be set custom.

            - project_name

                The project name.

                Note: `project_name` only works in ST3.

                Can't be set custom.
            */

            /*
            Email
            */
            "email": "email@example.com"

            // You can add more here......
        },
        /*
        You can set different variables in different languages. It will cover
        that in "Default".
        */
        "ASP": {},
        "ActionScript": {},
        "AppleScript": {},
        "Batch File": {},
        "C#": {},
        "C++": {},
        "CSS": {},
        "Clojure": {},
        "D": {},
        "Diff": {},
        "Erlang": {},
        "Go": {},
        "Graphviz": {},
        "Groovy": {},
        "HTML": {},
        "Haskell": {},
        "Java": {},
        "JavaScript": {},
        "LaTeX": {},
        "Lisp": {},
        "Lua": {},
        "Makefile": {},
        "Markdown": {},
        "Matlab": {},
        "OCaml": {},
        "Objective-C": {},
        "PHP": {},
        "Pascal": {},
        "Perl": {},
        "Python": {},
        "R": {},
        "RestructuredText": {},
        "Ruby": {},
        "SQL": {},
        "Scala": {},
        "ShellScript": {},
        "TCL": {},
        "Text": {},
        "Textile": {},
        "XML": {},
        "YAML": {}
    }


Template
========

FileHeader use Jinja2_ template, find out how to use it `here <http://jinja.pocoo.org/docs/>`_.

The template is made up of **header** and **body**.  You also can write you
own templates. Take the Python template header **Python.tmpl** for example.

    .. code-block:: ++

        # -*- coding: utf-8 -*-
        # @Author: {{author}}
        # @Date:   {{create_time}}
        # @Email:  {{email}}
        # @Last modified by:   {{last_modified_by}}
        # @Last Modified time: {{last_modified_time}}

**{{ }}** is variable, you can set it in setting files. **create_time** will be set when you create a new file using FileHeader, **last_modified_time** and **last_modified_by** will be update every time you save your file.

You can define your functions and classes or other contents in your **body**
file.  Also take Python template body for example.

    .. code-block:: python

        def main():
            pass

        class MainClass(object):
            pass

        if __name__ == '__main__':
            pass

.. _Jinja2: http://jinja.pocoo.org/docs/
