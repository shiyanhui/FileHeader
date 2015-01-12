#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2013-10-28 13:39:48
# @Last Modified by:   Lime
# @Last Modified time: 2015-01-12 09:51:33

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
import time
import pickle
import filecmp

from datetime import datetime

if sys.version < '3':
    import commands as process
else:
    import subprocess as process

PLUGIN_NAME = 'FileHeader'
INSTALLED_PLUGIN_NAME = '%s.sublime-package' % PLUGIN_NAME
PACKAGES_PATH = sublime.packages_path()
PLUGIN_PATH = os.path.join(PACKAGES_PATH, PLUGIN_NAME)
HEADER_PATH = os.path.join(PLUGIN_PATH, 'template/header')
BODY_PATH = os.path.join(PLUGIN_PATH, 'template/body')
INSTALLED_PLGIN_PATH = os.path.abspath(os.path.dirname(__file__))

IS_ST3 = sublime.version() >= '3'

sys.path.insert(0, PLUGIN_PATH)

def plugin_loaded():
    '''ST3'''

    global LOADED
    global PACKAGES_PATH
    global PLUGIN_PATH
    global HEADER_PATH
    global BODY_PATH
    global INSTALLED_PLGIN_PATH
    global IS_ST3

    PLUGIN_NAME = 'FileHeader'
    INSTALLED_PLUGIN_NAME = '%s.sublime-package' % PLUGIN_NAME

    PACKAGES_PATH = sublime.packages_path()
    PLUGIN_PATH = os.path.join(PACKAGES_PATH, PLUGIN_NAME)
    HEADER_PATH = os.path.join(PLUGIN_PATH, 'template/header')
    BODY_PATH = os.path.join(PLUGIN_PATH, 'template/body')
    INSTALLED_PLGIN_PATH = os.path.abspath(os.path.dirname(__file__))

    IS_ST3 = sublime.version() >= '3'

    sys.path.insert(0, PLUGIN_PATH)

    if INSTALLED_PLGIN_PATH != PLUGIN_PATH:
        _ = os.path.join(PLUGIN_PATH, INSTALLED_PLUGIN_NAME)
        if os.path.exists(_) and filecmp.cmp(_, INSTALLED_PLGIN_PATH):
            return

        if os.path.exists(PLUGIN_PATH):
            try:
                shutil.rmtree(PLUGIN_PATH)
            except:
                pass

        if not os.path.exists(PLUGIN_PATH):
            os.mkdir(PLUGIN_PATH)

        z = zipfile.ZipFile(INSTALLED_PLGIN_PATH, 'r')
        for f in z.namelist():
            z.extract(f, PLUGIN_PATH)
        z.close()

        shutil.copyfile(INSTALLED_PLGIN_PATH, _)


def Window():
    '''Get current active window'''

    return sublime.active_window()


def Settings():
    '''Get settings'''

    return sublime.load_settings('%s.sublime-settings' % PLUGIN_NAME)


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
        contents = template_file.read()
        template_file.close()
    except Exception as e:
        contents = ''
    return contents


def get_template(syntax_type):
    return ''.join(
        [get_template_part(syntax_type, part)
            for part in ['header', 'body']])


def get_strftime():
    '''Get `time_format` setting'''

    _ = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%H:%M:%S']

    format = Settings().get('custom_time_format')

    if not format:
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


def get_project_name():
    '''Get project name'''

    project_data = sublime.active_window().project_data()
    project = os.path.basename(
        project_data['folders'][0]['path']) if project_data else None

    return project


def get_file_path(path):
    '''Get absolute path of the file'''

    return 'undefined' if path is None else path


def get_file_name(path):
    '''Get name of the file'''

    return 'undefined' if path is None else os.path.basename(path)


def get_file_name_without_extension(file_name):
    '''Get name of the file without extension'''

    return '.'.join(file_name.split('.')[:-1]) or file_name


def get_time(path):
    c_time = m_time = None
    try:
        stat = os.stat(path)
    except:
        pass
    else:
        c_time = datetime(*time.localtime(stat.st_ctime)[:6])
        m_time = datetime(*time.localtime(stat.st_mtime)[:6])

    return c_time, m_time


def get_args(syntax_type, options={}):
    '''Get the args rendered.

    :Para:
        - `syntax_type`: Language type
        - `which`: candidates are 'new' and 'add'
    '''

    def get_st3_time():
        _ = c_time = m_time = datetime.now()

        path = options.get('path', None)
        if path is not None:
            c_time, m_time = get_time(path)

            if c_time is None:
                c_time = m_time = _

        return c_time, m_time

    def get_st2_time():
        c_time, m_time = get_st3_time()
        _ = options.get('c_time', None)
        if _ is not None:
            c_time = _

        return c_time, m_time

    args = Settings().get('Default')
    args.update(Settings().get(syntax_type, {}))

    format = get_strftime()
    c_time, m_time = get_st3_time() if IS_ST3 else get_st2_time()

    file_path = get_file_path(options.get('path', None))
    file_name = get_file_name(options.get('path', None))
    file_name_without_extension = get_file_name_without_extension(file_name)

    args.update({
        'create_time': c_time.strftime(format),
        'last_modified_time': m_time.strftime(format),
        'file_name': file_name,
        'file_name_without_extension': file_name_without_extension,
        'file_path' : file_path
    })

    if IS_ST3:
        args.update({'project_name': get_project_name()})

    user = get_user()
    if 'author' not in args:
        args.update({'author': user})
    if 'last_modified_by' not in args:
        args.update({'last_modified_by': user})

    return args


def render_template(syntax_type, part=None, options={}):
    '''Render the template correspond `syntax_type`'''

    from jinja2 import Template
    try:
        if part is not None:
            template = Template(get_template_part(syntax_type, part))
        else:
            template = Template(get_template(syntax_type))

        render_string = template.render(get_args(syntax_type, options))
    except:
        render_string = ''
    return render_string


def get_syntax_type(name):
    '''Judge `syntax_type` according to to `name`'''

    syntax_type = Settings().get('syntax_when_not_match')
    file_suffix_mapping = Settings().get('file_suffix_mapping')
    extension_equivalence = Settings().get('extension_equivalence')

    if name is not None:
        name = name.split('.')
        if len(name) <= 1:
            return syntax_type

        for i in range(1, len(name)):
            suffix = '.'.join(name[i:])
            if suffix in extension_equivalence:
                suffix = extension_equivalence[suffix]
                break
        else:
            suffix = name[-1]

        try:
            syntax_type = file_suffix_mapping[suffix]
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

        header = render_template(syntax_type, options={'path': path})

        try:
            with open(path, 'w+') as f:
                f.write(header)

        except Exception as e:
            sublime.error_message(str(e))
            return

        new_file = Window().open_file(path)

        try:
            block(new_file,
                new_file.set_syntax_file, get_syntax_file(syntax_type))
        except:
            pass

        block(new_file, new_file.show, 0)

    def new_view(self, syntax_type, name):
        header = render_template(syntax_type)
        new_file = Window().new_file()
        new_file.set_name(name)
        new_file.run_command('insert', {'characters': header})

        try:
            new_file.set_syntax_file(get_syntax_file(syntax_type))
        except:
            pass

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

        Window().run_command('hide_panel')
        Window().show_input_panel('File Name:', '', functools.partial(
                                  self.on_done, path), None, None)


class BackgroundAddHeaderThread(threading.Thread):
    '''Add header in background.'''

    def __init__(self, path):
        self.path = path
        super(BackgroundAddHeaderThread, self).__init__()

    def run(self):
        syntax_type = get_syntax_type(self.path)
        header = render_template(syntax_type, 'header', {'path': path})

        try:
            with open(self.path, 'r') as f:
                contents = header + f.read()

            with open(self.path, 'w') as f:
                f.write(contents)

        except Exception as e:
            sublime.error_message(str(e))


class AddFileHeaderCommand(sublime_plugin.TextCommand):
    '''Command: add `header` in a file'''

    def run(self, edit, path, part=None):
        syntax_type = get_syntax_type(path)

        options = {'path': path}
        if not IS_ST3:
            c_time = self.view.settings().get('c_time', None)
            if c_time is not None:
                c_time = pickle.loads(str(c_time))
                options.update({'c_time': c_time})

        header = render_template(syntax_type, part, options)
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
            return enable_add_to_hidden_dir or (not enable_add_to_hidden_dir
                                                and not self.is_hidden(path))

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


LAST_MODIFIED_BY = 'LAST_MODIFIED_BY'
LAST_MODIFIED_TIME = 'LAST_MODIFIED_TIME'
FILE_NAME = 'FILE_NAME'
FILE_NAME_WITHOUT_EXTENSION = 'FILE_NAME_WITHOUT_EXTENSION'
FILE_PATH = 'FILE_PATH'

class FileHeaderListener(sublime_plugin.EventListener):

    LAST_MODIFIED_BY_REGEX = re.compile('\{\{\s*last_modified_by\s*\}\}')
    LAST_MODIFIED_TIME_REGEX = re.compile('\{\{\s*last_modified_time\s*\}\}')
    FILE_NAME_REGEX = re.compile('\{\{\s*file_name\s*\}\}')
    FILE_NAME_WITHOUT_EXTENSION_REGEX = re.compile(
        '\{\{\s*file_name_without_extension\s*\}\}')
    FILE_PATH_REGEX = re.compile('\{\{\s*file_path\s*\}\}')

    new_view_id = []

    def time_pattern(self):
        choice = Settings().get('time_format')
        _ = [0, 1, 2]
        if choice not in _:
            choice = 0

        _ = ['\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}',
             '\d{4}-\d{2}-\d{2}', '\d{2}:\d{2}:\d{2}']
        return _[choice]

    def update_automatically(self, view, what):
        syntax_type = get_syntax_type(view.file_name())

        template = get_template_part(syntax_type, 'header')
        lines = template.split('\n')

        line_pattern = None
        regex = getattr(FileHeaderListener, '%s_REGEX' % what)
        for line in lines:
            search = regex.search(line)

            if search is not None:
                var = search.group()
                index = line.find(var)

                for i in range(index - 1, 0, -1):
                    if line[i] != ' ':
                        space_start = i + 1
                        line_header = line[:space_start]
                        break

                line_header = re.escape(line_header)
                if what == LAST_MODIFIED_BY or what == FILE_NAME or \
                        what == FILE_NAME_WITHOUT_EXTENSION or \
                        what == FILE_PATH:
                    line_pattern = '%s.*\n' % line_header

                elif what == LAST_MODIFIED_TIME:
                    line_pattern = '%s\s*%s.*\n' % (
                        line_header, self.time_pattern())

                else:
                    raise KeyError()

                break

        if line_pattern is not None:
            _ = view.find(line_pattern, 0)
            if(_ != sublime.Region(-1, -1) and _ is not None):
                a = _.a + space_start
                b = _.b - 1

                file_name = get_file_name(view.file_name())
                file_name_without_extension = get_file_name_without_extension(
                    file_name)
                file_path = get_file_path(view.file_name())

                if what == LAST_MODIFIED_BY:
                    strings = get_args(syntax_type)['last_modified_by']
                elif what == LAST_MODIFIED_TIME:
                    strings = datetime.now().strftime(get_strftime())
                elif what == FILE_NAME:
                    strings = file_name
                elif what == FILE_NAME_WITHOUT_EXTENSION:
                    strings = file_name_without_extension
                elif what == FILE_PATH:
                    strings = file_path

                spaces = (index - space_start) * ' '
                strings = spaces + strings

                region = sublime.Region(int(a), int(b))
                if view.substr(region) != strings:
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
        FileHeaderListener.new_view_id.append(view.id())

    def on_text_command(self, view, command_name, args):
        if command_name == 'undo' or command_name == 'soft_undo':
            while view.command_history(0)[0] == 'file_header_replace':
                view.run_command('undo')

    def on_pre_save(self, view):
        if view.id() in FileHeaderListener.new_view_id:
            self.insert_template(view, False)
            index = FileHeaderListener.new_view_id.index(view.id())
            del FileHeaderListener.new_view_id[index]
        else:
            if view.is_dirty():
                self.update_automatically(view, LAST_MODIFIED_BY)
                self.update_automatically(view, LAST_MODIFIED_TIME)

    def on_activated(self, view):
        block(view, self.update_automatically, view, FILE_NAME)
        block(view, self.update_automatically, view, FILE_NAME_WITHOUT_EXTENSION)
        block(view, self.update_automatically, view, FILE_PATH)

        settings = view.settings()
        c_time, _ = get_time(view.file_name())
        if c_time is not None and settings.get('c_time', None) is None:
            settings.set('c_time', pickle.dumps(c_time))

        self.insert_template(view, True)
