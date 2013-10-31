==========
FileHeader
==========

Overview
========

FileHeader is a plugin for ST2/ST3. It makes it easier to create new file with initial contents. It also can add new header to an existed file or directory.

:Info: File header manager for Sublime Text 2 and Sublime Text 3.
:Author: Lime YH.Shi

Features
=========

- Add new file with initial contents.
- Add header to an existed file or directory.
- Batch add header to files in the specified dircetory.
- Auto detect file type.
- Powerful template with Jinja2_.
- Custom templates supported.
- Rich languages supported.
- Auto update file last modified time.
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

- Sidebar menu

    .. image:: https://github.com/shiyanhui/shiyanhui.github.io/blob/master/images/FileHeader/new_file_sidebar.gif

- Shortcuts    

    The default shortcuts is **super+alt+n** on OS X, **ctrl+alt+n** on Windows and Linux.

- Context menu

    Similar to **Sidebar menu**.

Add header to an existed file
-----------------------------

- Sidebar menu

    .. image:: https://github.com/shiyanhui/shiyanhui.github.io/blob/master/images/FileHeader/add_header_sidebar.gif

- Shortcuts

    The default shortcuts is **super+alt+a** on OS X, **ctrl+alt+a** on Windows and Linux.

- Context menu

    Similar to **Sidebar menu**.
    
Add header to files in the specified directory
----------------------------------------------

    .. image:: https://github.com/shiyanhui/shiyanhui.github.io/blob/master/images/FileHeader/add_header_in_dir.gif

A very important feature of FileHeader is that it can automic update last modified time of file. Just look this picture, take care of the **@Last modified:** before save and after save: 

.. image:: https://github.com/shiyanhui/shiyanhui.github.io/blob/master/images/FileHeader/update_time.gif


Settings
========

There are three kinds of arguments, **options**, **Default** and kinds of languages variables settings. **options** is the functional setting, **Default** is the default language variables settings. Language variables setting will cover that in **Default**.

.. code-block:: c++
    
    {
        "options": {
            // Whether enable variable `create_time`. If false the variable 
            // `create_time` won't work. 
            "create_time": true,
            // Whether enable variable `modified_time`. If false the variable 
            // `modified_time` won't work. 
            // If enable it, it will update {{ modified_time }} every time you
            // save file.
            "modified_time": true,
            // The datetime format.
            // 0: "%Y-%m-%d %H:%M:%S"
            // 1: "%Y-%m-%d"
            // 2: "%H:%M:%S"
            "time_format": 0,
            // Set your custom template path here, it is a directory. In it you 
            // write your own .tmpl files. The file name should be a language, 
            // "Python.tmpl" for example. FileHeader will search your custom path
            // prior, and FileHeader will use the default .tmpl file if fail.
            "custom_template_path": "",
            //Whether show input panel when you add header. The default file which 
            //you add header to is the current file you edit.
            "show_input_panel_when_add_header": true,
            //Whether open file when you add header to files in the specified 
            // directory.
            "open_file_when_add_header_to_directory": true,
            // FileHeader judges programming language according file suffix.
            //
            // Default programming language if FileHeader judges failed when you
            // create new file.
            "syntax_when_not_match": "Text",
            // FileHeader will judge programming language according to file suffix.
            // You can add more file suffix here. Note: language should be one of 
            // that under **Default**. If FileHeader don't find the suffix,
            // FileHeader will set language as **syntax_when_not_match** above.
            "file_suffix_mapping":{
                "as": "ActionScript",
                "scpt": "AppleScript",
                "asp": "ASP",
                "aspx": "ASP",
                "c": "C++",
                "cs": "C#",
                "cpp": "C++",
                "clj": "Clojure",
                "css": "CSS",
                "d": "D",
                "erl": "Erlang",
                "go": "Go",
                "hs": "Haskell",
                "htm": "HTML",
                "html": "HTML",
                "java": "Java",
                "js": "JavaScript",
                "tex": "LaTeX",
                "lisp": "Lisp",
                "lua": "Lua",
                "mat": "Matlab",
                "cc": "Objective-C",
                "pas": "Pascal",
                "pl": "Perl",
                "php": "PHP",
                "py": "Python",
                "rb": "Ruby",
                "scala": "Scala",
                "sh": "ShellScript",
                "sql": "SQL",
                "tcl": "TCL",
                "txt": "Text",
                "xml": "XML"
            }
        } ,
        // The default variables you render.
        "Default": {
            // Author 
            "author": "Your Name",
            // Email
            "email": "email@example.com"
            // You can add more here......
        },
        // You can set different variables in different languages. It will cover 
        // that in "Default".
        "ASP": {},
        "ActionScript": {},
        "AppleScript": {},
        "Batch File": {},
        //more languages...... 
    }


Template
========

FileHeader use Jinja2_ template, you can find how to use it `here <http://jinja.pocoo.org/docs/>`_. You can write you own template. Take **Python.tmpl** for example.

    .. code-block:: c++

        # -*- coding: utf-8 -*-
        # @Date:    {{create_time}}
        # @Author:  {{author}}
        # @Email:   {{email}}
        # @Last modified: {{modified_time}}

Variable in **{{ }}** is set in the language settings, you can set it in setting files. **create_time** will be automic set when you create a new file using FileHeader, and **modified_time** will be update every time you save your file.


.. _Jinja2: http://jinja.pocoo.org/docs/
