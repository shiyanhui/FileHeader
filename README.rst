==========
FileHeader
==========

FileHeader is a powerful file templating plugin for SublimeText 2 and
SublimeText 3. It makes it easier to create new file with initial contents. It
also can add new header to an existed file or directory.

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

Install `Package Control`_. Then **Package Control: Install Package**, look for
**FileHeader** and install it.

.. _Package Control: https://sublime.wbond.net/

Source Installation
--------------------

Go to the "Packages" directory **(Preferences / Browse Packages)**. Then clone
this repository::

    git clone git@github.com:shiyanhui/FileHeader.git

Or download zip from Github, and put it in "Packages" directory
**(Preferences / Browse Packages)**.

Usage
=====

Create a new file
-----------------

- Sidebar Menu

  .. image:: https://raw.github.com/shiyanhui/FileHeader/master/doc/img/new-file.gif

- Shortcuts

  The default shortcuts is **super+alt+n** on OS X, **ctrl+alt+n** on Windows and Linux.

- Context Menu

  Similar to **Sidebar Menu**.

Add header to an existed file
-----------------------------

- Sidebar Menu

  .. image:: https://raw.github.com/shiyanhui/FileHeader/master/doc/img/add-header.gif

- Shortcuts

  The default shortcuts is **super+alt+a** on OS X, **ctrl+alt+a** on
  Windows and Linux.

- Context Menu

  Similar to **Sidebar Menu**.

Add header to files in the specified directory
----------------------------------------------

- Sidebar Menu

  .. image:: https://raw.github.com/shiyanhui/FileHeader/master/doc/img/add-header-dir.gif

A very important feature of FileHeader is that it can automatically update
**last_modified_time** and **last_modified_by** (see options below). Just look
this picture, take care of the **@Last modified time:** before save and after
save:

.. image:: https://raw.github.com/shiyanhui/FileHeader/master/doc/img/update.gif

Settings
========

There are two kinds of arguments: **options** and kinds of languages variables
settings. **options** is the functional setting, **Default** is the default
language variables settings. Language variables setting will cover that in
**Default**.

Open **Preferences => Package Settings => File Header => Settings - Default**
for more details.

Template
========

FileHeader use Jinja2_ template, find out how to use it
`here <http://jinja.pocoo.org/docs/>`_.

The template is made up of **header** and **body**.  You also can write you
own templates. Take the Python template header **Python.tmpl** for example.

    .. code-block:: ++

        # -*- coding: utf-8 -*-
        # @Author: {{author}}
        # @Date:   {{create_time}}
        # @Last modified by:   {{last_modified_by}}
        # @Last Modified time: {{last_modified_time}}

**{{ }}** is variable, you can set it in setting files. **create_time** will be
set when you create a new file using FileHeader, **last_modified_time** and
**last_modified_by** will be update every time you save your file.

You can define your functions and classes or other contents in your **body**
file.  Also take Python template body for example.

    .. code-block:: python

        class MyClass(object):
            pass

        if __name__ == '__main__':
            pass

FAQ
===

- **How to customize my headers?**

  Set **custom_template_header_path** to your path of customized header in
  user-settings, for example, **~/header/**

  NOTE: **DO NOT** modify directly that in **Packages/FileHeader**

- **What if FileHeader conflicts with other file template plugin?**

  For example, **FileHeader** and **Javatar** conflicts in files with
  extension **.java**.

  The solution is, open any file with extension **.java** in sublime text,
  and open **Preferences ==> Settings - More ==> Syntax Specific - User**,
  then add **"enable_add_template_to_empty_file": false**.

- **What if key-map of FileHeader conflicts with others?**

  Just change that of **FileHeader** or others.


Other Editors
=============

- `FileHeader for Atom <https://github.com/guiguan/file-header>`_ by `guiguan <https://github.com/guiguan>`_

If you have any questions, please let me know. 🙂

.. _Jinja2: http://jinja.pocoo.org/docs/
