#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2013-10-28 13:39:48
# @Email:  shiyanhui66@gmail.com
# @Last modified by:   lime
# @Last Modified time: 2013-11-03 00:23:31

import os
import sys
import re
import sublime
import sublime_plugin
import functools
import threading
import zipfile
import getpass
import shutil

from datetime import datetime

if sys.version < '3':
    import commands as process
else:
    import subprocess as process

PLUGIN_NAME = 'FileHeader'
PACKAGES_PATH = sublime.packages_path()
PLUGIN_PATH = os.path.join(PACKAGES_PATH, PLUGIN_NAME)
HEADER_PATH = os.path.join(PLUGIN_PATH, 'template/header')
BODY_PATH = os.path.join(PLUGIN_PATH, 'template/body')
INSTALLED_PLGIN_PATH = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, PLUGIN_PATH)


def plugin_loaded():
    '''ST3'''

    global PACKAGES_PATH
    global PLUGIN_PATH
    global HEADER_PATH
    global BODY_PATH

    PACKAGES_PATH = sublime.packages_path()
    PLUGIN_PATH = os.path.join(PACKAGES_PATH, PLUGIN_NAME)
    HEADER_PATH = os.path.join(PLUGIN_PATH, 'template/header')
    BODY_PATH = os.path.join(PLUGIN_PATH, 'template/body')

    sys.path.insert(0, PLUGIN_PATH)

    if os.path.exists(PLUGIN_PATH):
        try:
            shutil.rmtree(PLUGIN_PATH)
        except:
            pass

    if not os.path.exists(PLUGIN_PATH):
        os.mkdir(PLUGIN_PATH)

    if os.path.exists(INSTALLED_PLGIN_PATH):
        z = zipfile.ZipFile(INSTALLED_PLGIN_PATH, 'r')
        for f in z.namelist():
            z.extract(f, PLUGIN_PATH)
        z.close()

def Window():
    '''Get current act``ive window'''

    return sublime.active_window()


def Settings():
    '''Get settings'''

    setting_name = '%s.sublime-settings' % PLUGIN_NAME
    settings = sublime.load_settings(setting_name)
    return settings


def get_template_part(syntax_type, part):
    '''Get template header or body'''

    tmpl_name = '%s.tmpl' % syntax_type
    path = HEADER_PATH if part == 'header' else BODY_PATH
    tmpl_file = os.path.join(path, tmpl_name)

    custom_template_path = Settings().get('custom_template_%s_path' % part)
    if custom_template_path:
        _ = os.path.join(custom_template_path, tmpl_name)
        if os.path.exists(_) and os.path.isfile(_):
            tmpl_file = _

    try:
        template_file = open(tmpl_file, 'r')
        contents = template_file.read() + '\n'
        template_file.close()
    except Exception as e:
        sublime.error_message(str(e))
        contents = ''
    return contents


def get_template(syntax_type):
    parts = ['header', 'body']
    return ''.join([get_template_part(syntax_type, part) for part in parts])


def get_strftime():
    '''Get `time_format` setting'''

    _ = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%H:%M:%S']
    try:
        format = _[Settings().get('time_format')]
    except IndexError:
        format = _[0]
    return format


def get_user():
    '''Get user'''

    user = getpass.getuser()
    status, _ = process.getstatusoutput('git status')
    if status == 0:
        status, output = process.getstatusoutput('git config --get user.name')
        if status == 0 and output:
            user = output

    return user


def get_args(syntax_type):
    '''Get the args rendered'''

    args = Settings().get('Default')
    args.update(Settings().get(syntax_type, {}))

    format = get_strftime()
    time = datetime.now().strftime(format)

    args.update({'create_time': time})
    args.update({'last_modified_time': time})

    user = get_user()

    if 'author' not in args:
        args.update({'author': user})

    if 'last_modified_by' not in args:
        args.update({'last_modified_by': user})

    return args


def render_template(syntax_type, part=None):
    '''Render the template correspond `syntax_type`'''

    from jinja2 import Template
    try:
        if part is not None:
            template = Template(get_template_part(syntax_type, part))
        else:
            template = Template(get_template(syntax_type))

        render_string = template.render(get_args(syntax_type))
    except Exception as e:
        sublime.error_message(str(e))
        render_string = ''
    return render_string


def get_syntax_type(name):
    '''Judge `syntax_type` according to to `name`'''
    syntax_type = Settings().get('syntax_when_not_match')
    file_suffix_mapping = Settings().get('file_suffix_mapping')

    name = name.split('.')
    if len(name) <= 1:
        return syntax_type

    try:
        syntax_type = file_suffix_mapping[name[-1]]
    except KeyError:
        pass

    return syntax_type


def get_syntax_file(syntax_type):
    '''Get syntax file path'''

    lang2tmL = {
        'Graphviz': 'DOT',
        'RestructuredText': 'reStructuredText',
        'ShellScript': 'Shell-Unix-Generic',
        'TCL': 'Tcl',
        'Text': 'Plain text',
    }

    if syntax_type == 'C':
        syntax_type = 'C++'

    tmL = lang2tmL.get(syntax_type, syntax_type)
    return 'Packages/%s/%s.tmLanguage' % (syntax_type, tmL)


def block(view, callback, *args, **kwargs):
    '''Ensure the callback is executed'''

    def _block():
        if view.is_loading():
            sublime.set_timeout(_block, 100)
        else:
            callback(*args, **kwargs)

    _block()


class FileHeaderNewFileCommand(sublime_plugin.WindowCommand):

    '''Create a new file with header'''

    def new_file(self, path, syntax_type):
        if os.path.exists(path):
            sublime.error_message('File exists!')
            return

        header = render_template(syntax_type)

        try:
            with open(path, 'w+') as f:
                f.write(header)
                f.close()
        except Exception as e:
            sublime.error_message(str(e))
            return

        new_file = Window().open_file(path)
        block(new_file, new_file.set_syntax_file, get_syntax_file(syntax_type))
        block(new_file, new_file.show, 0)

    def new_view(self, syntax_type, name):
        header = render_template(syntax_type)
        new_file = Window().new_file()
        new_file.set_name(name)
        new_file.run_command('insert', {'characters': header})
        new_file.set_syntax_file(get_syntax_file(syntax_type))

    def get_path(self, paths):
        path = None
        if not paths:
            current_view = Window().active_view()
            if current_view:
                file_name = current_view.file_name()
                if file_name is not None:
                    path = os.path.dirname(file_name)
        else:
            path = paths[0]
            if not os.path.isdir(path):
                path = os.path.dirname(path)

        if path is not None:
            path = os.path.abspath(path)

        return path

    def on_done(self, path, name):
        if not name:
            return

        syntax_type = get_syntax_type(name)

        if path is None:
            self.new_view(syntax_type, name)
        else:
            path = os.path.join(path, name)
            self.new_file(path, syntax_type)

    def run(self, paths=[]):
        path = self.get_path(paths)

        caption = 'File Name:'
        # if caption is not None:
        #     caption = 'File Nanme: (Saved in %s)' % path

        Window().run_command('hide_panel')
        Window().show_input_panel(caption, '', functools.partial(
                                  self.on_done, path), None, None)


class BackgroundAddHeaderThread(threading.Thread):

    '''Add header in background.'''

    def __init__(self, path):
        self.path = path
        super(BackgroundAddHeaderThread, self).__init__()

    def run(self):
        syntax_type = get_syntax_type(self.path)
        header = render_template(syntax_type, 'header')

        try:
            with open(self.path, 'r') as f:
                contents = header + f.read()
                f.close()

            with open(self.path, 'w') as f:
                f.write(contents)
                f.close()
        except Exception as e:
            sublime.error_message(str(e))


class AddFileHeaderCommand(sublime_plugin.TextCommand):

    '''Command: add `header` in a file'''

    def run(self, edit, path, part=None):
        syntax_type = get_syntax_type(path)
        header = render_template(syntax_type, part)
        self.view.insert(edit, 0, header)


class FileHeaderAddHeaderCommand(sublime_plugin.WindowCommand):

    '''Conmmand: add `header` in a file or directory'''

    def is_hidden(self, path):
        '''Whether the file or dir is hidden'''

        hidden = False
        platform = sublime.platform()
        if platform == 'windows':
            status, output = process.getstatusoutput('attrib %s' % path)
            if status == 0:
                try:
                    if output[4].upper() == 'H':
                        hidden = True
                except:
                    pass
        else:
            basename = os.path.basename(path)
            if basename.startswith('.'):
                hidden = True
        return hidden

    def can_add(self, path):
        '''Whether can add header to path'''

        def can_add_to_dir(path):
            return enable_add_to_hidden_dir or (not enable_add_to_hidden_dir and
                                                not self.is_hidden(path))

        if not os.path.exists(path):
            return False

        file_suffix_mapping = Settings().get('file_suffix_mapping')
        enable_add_to_hidden_dir = Settings().get(
            'enable_add_header_to_hidden_dir')
        enable_add_to_hidden_file = Settings().get(
            'enable_add_header_to_hidden_file')

        if os.path.isfile(path):
            if can_add_to_dir(os.path.dirname(path)):
                if enable_add_to_hidden_file or (not enable_add_to_hidden_file
                                                 and not self.is_hidden(path)):
                    return True

        elif os.path.isdir(path):
            return can_add_to_dir(path)

        return False

    def add(self, path):
        '''Add to a file'''

        whether_open_file = Settings().get(
            'open_file_when_add_header_to_directory')

        if whether_open_file:
            modified_file = Window().open_file(path)
            block(modified_file, modified_file.run_command,
                  'add_file_header', {'path': path, 'part': 'header'})
            block(modified_file, modified_file.show, 0)
        else:
            thread = BackgroundAddHeaderThread(path)
            thread.start()

    def walk(self, path):
        '''Add files in the path'''

        for root, subdirs, files in os.walk(path):
            for f in files:
                file_name = os.path.join(root, f)
                if self.can_add(file_name):
                    self.add(file_name)

    def on_done(self, path):
        if not path:
            return

        if not os.path.exists(path):
            sublime.error_message('Path not exists!')
            return

        path = os.path.abspath(path)
        if os.path.isfile(path) and self.can_add(path):
            self.add(path)

        elif os.path.isdir(path) and self.can_add(path):
            self.walk(path)

    def run(self, paths=[]):
        initial_text = ''
        if paths:
            initial_text = os.path.abspath(paths[0])
        else:
            try:
                initial_text = Window().active_view().file_name()
            except:
                pass

        show_input_panel_when_add_header = Settings().get(
            'show_input_panel_when_add_header')

        if not show_input_panel_when_add_header:
            self.on_done(initial_text)
            return

        Window().run_command('hide_panel')
        Window().show_input_panel('Modified File or Directory:', initial_text,
                                  self.on_done, None, None)


class FileHeaderReplaceCommand(sublime_plugin.TextCommand):

    '''Replace contents in the `region` with `stirng`'''

    def run(self, edit, a, b, strings):
        region = sublime.Region(int(a), int(b))
        self.view.replace(edit, region, strings)


class FileHeaderListener(sublime_plugin.EventListener):

    '''Auto update `last_modified_time` when save file'''

    MODIFIED_TIME_REGEX = re.compile('\{\{\s*last_modified_time\s*\}\}')
    MODIFIED_BY_REGEX = re.compile('\{\{\s*last_modified_by\s*\}\}')

    new_view_id = []

    def time_pattern(self):
        choice = Settings().get('time_format')
        _ = [0, 1, 2]
        if choice not in _:
            choice = 0

        _ = ['\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}',
             '\d{4}-\d{2}-\d{2}', '\d{2}:\d{2}:\d{2}']
        return _[choice]

    def update_last_modified(self, view, what):
        what = what.upper()
        syntax_type = get_syntax_type(view.file_name())
        template = get_template_part(syntax_type, 'header')
        lines = template.split('\n')

        line_pattern = None
        for line in lines:
            regex = getattr(FileHeaderListener, 'MODIFIED_%s_REGEX' % what)
            search = regex.search(line)

            if search is not None:
                var = search.group()
                index = line.find(var)

                for i in range(index - 1, 0, -1):
                    if line[i] != ' ':
                        space_start = i + 1
                        line_header = line[: space_start]
                        break

                line_header = line_header.replace('*', '\*')
                if what == 'BY':
                    line_pattern = '%s.*\n' % line_header
                else:
                    line_pattern = '%s\s*%s.*\n' % (line_header,
                                                    self.time_pattern())
                break

        if line_pattern is not None:
            _ = view.find(line_pattern, 0)
            if(_ != sublime.Region(-1, -1) and _ is not None):
                a = _.a + space_start
                b = _.b - 1

                spaces = (index - space_start) * ' '
                if what == 'BY':
                    args = get_args(syntax_type)
                    strings = (spaces + args['last_modified_by'])
                else:
                    strftime = get_strftime()
                    time = datetime.now().strftime(strftime)
                    strings = (spaces + time)
                view.run_command('file_header_replace',
                                 {'a': a, 'b': b, 'strings': strings})

    def insert_template(self, view, exists):
        enable_add_template_to_empty_file = Settings().get(
            'enable_add_template_to_empty_file')

        path = view.file_name()
        condition = (path and enable_add_template_to_empty_file
                     and view.size() <= 0)

        if exists:
            condition = (condition and os.path.exists(path)
                         and os.path.isfile(path)
                         and os.path.getsize(path) <= 0)

        if condition:
            block(view, view.run_command, 'add_file_header', {'path': path})
            block(view, view.show, 0)

    def on_new(self, view):
        '''For ST2'''

        FileHeaderListener.new_view_id.append(view.id())

    def on_pre_save(self, view):
        if view.id() in FileHeaderListener.new_view_id:
            self.insert_template(view, False)
            index = FileHeaderListener.new_view_id.index(view.id())
            del FileHeaderListener.new_view_id[index]
        else:
            self.update_last_modified(view, 'by')
            self.update_last_modified(view, 'time')

    def on_activated(self, view):
        self.insert_template(view, True)
