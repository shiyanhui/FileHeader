==========
FileHeader
==========

:Info: File header manager for Sublime Text 2 and Sublime Text 3.
:Author: Lime YH.Shi

Overview
========

FileHeader is a plugin for ST2/ST3. It makes it easier to create new file with initial contents. It can also add new header to an existed file.

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

.. _Jinja2: http://jinja.pocoo.org/docs/

Installation
============


Usage
=====

Create a new file with project info
-----------------------------------

- From the sidebar 

    .. image:: ./doc/source/_static/new%20file%20sidebar.gif

- Shortcuts    

    .. image:: ./doc/source/_static/new%20file%20shortcuts.gif

    The shortcuts is `super+alt+n` on OS X, `ctrl+alt+n` on Windows and Linux.

Add header to an existed file
-----------------------------

- From the sidebar

    .. image:: ./doc/source/_static/add%20header%20sidebar.gif

- Shortcuts

    .. image:: ./doc/source/_static/add%20header%20shortcuts.gif

    The shortcuts is `super+alt+a` on OS X, `ctrl+alt+a` on Windows and Linux.

Add header to files in specified directory
------------------------------------------

    .. image:: ./doc/source/_static/add%20header%20in%20dir.gif


A very important feature of FileHeader is it can automic update file last modified time. Just look this, take care of the `@Last modified:` before save and after save: 

.. image:: ./doc/source/_static/update%20time.gif
