# -*- coding: utf-8 -*-
# @Author: Lime
# @Date:   2013-10-28 13:39:48
# @Last Modified by:   qkdreyer
# @Last Modified time: 2017-08-14 16:48:32

import os
import sys
import re
import functools
import threading
import zipfile
import getpass
import shutil
import pickle
import filecmp
import subprocess
from datetime import datetime

import sublime
import sublime_plugin

PLUGIN_NAME = 'FileHeader'
INSTALLED_PLUGIN_NAME = '%s.sublime-package' % PLUGIN_NAME
PACKAGES_PATH = sublime.packages_path()
PLUGIN_PATH = os.path.join(PACKAGES_PATH, PLUGIN_NAME)
HEADER_PATH = os.path.join(PLUGIN_PATH, 'template/header')
BODY_PATH = os.path.join(PLUGIN_PATH, 'template/body')
INSTALLED_PLGIN_PATH = os.path.abspath(os.path.dirname(__file__))

FILE_SUFFIX_MAPPING = {
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
    "scss": "SCSS",
    "sh": "ShellScript",
    "sql": "SQL",
    "tcl": "TCL",
    "txt": "Text",
    "xml": "XML"
}

HEADER_PREFIX_MAPPING = {
    "PHP": "<?php\n\n"
}

EXTENSION_EQUIVALENCE = {
    "blade.php": "html"
}

LANGUAGE_SYNTAX_MAPPING = {
    'Graphviz': 'DOT',
    'RestructuredText': 'reStructuredText',
    'ShellScript': 'Shell-Unix-Generic',
    'TCL': 'Tcl',
    'Text': 'Plain text'
}

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


def getOutputError(cmd):
    return map(str.strip, subprocess.Popen(
        cmd, shell=True, universal_newlines=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())


def View():
    '''Get current active window view'''

    return Window().active_view()


def Window():
    '''Get current active window'''

    return sublime.active_window()


def Settings():
    '''Get settings'''

    return sublime.load_settings('%s.sublime-settings' % PLUGIN_NAME)


def get_template_part(syntax_type, part):
    '''Get template header or body'''

    template_name = '%s.tmpl' % syntax_type
    tmplate_path = os.path.join(
        HEADER_PATH if part == 'header' else BODY_PATH, template_name)

    custom_template_path = Settings().get('custom_template_%s_path' % part)
    if custom_template_path:
        path = os.path.abspath(os.path.expanduser(os.path.expandvars(
            os.path.join(custom_template_path, template_name))))

        if os.path.exists(path) and os.path.isfile(path):
            tmplate_path = path

    try:
        with open(tmplate_path, 'r') as f:
            contents = f.read()
    except:
        contents = ''
    return contents


def get_template(syntax_type):
    return ''.join([
        get_template_part(syntax_type, part)
        for part in ['header', 'body']
    ])


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
    output, error = getOutputError(
        'cd {0} && git status'.format(get_dir_path()))

    if not error:
        output, error = getOutputError('git config --get user.name')
        if not error and output:
            user = output
    return user


def get_project_name():
    '''Get project name'''

    project_data = Window().project_data()
    project = os.path.basename(
        project_data['folders'][0]['path']) if project_data else None

    return project


def get_dir_path():
    '''Get current file dir path'''

    view, path = View(), None
    if view:
        file_name = view.file_name()
        if file_name is not None:
            path = os.path.dirname(file_name)
    return path


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
        c_time, m_time = map(
            datetime.fromtimestamp, (stat.st_ctime, stat.st_mtime))

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
        'file_path': file_path
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
        template = Template(
            get_template_part(syntax_type, part)
            if part else get_template(syntax_type))
        render_string = template.render(get_args(syntax_type, options))
    except:
        render_string = ''
    return render_string


def get_syntax_type(name):
    '''Judge `syntax_type` according to to `name`'''

    syntax_type = Settings().get('syntax_when_not_match')
    file_suffix_mapping = merge_defaults_with_settings(
        FILE_SUFFIX_MAPPING, 'file_suffix_mapping')
    extension_equivalence = merge_defaults_with_settings(
        EXTENSION_EQUIVALENCE, 'extension_equivalence')

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

    # weird workaround
    if syntax_type == 'C':
        syntax_type = 'C++'

    lang2tmL = merge_defaults_with_settings(
        LANGUAGE_SYNTAX_MAPPING, 'language_syntax_mapping')
    tmL = lang2tmL.get(syntax_type, syntax_type)

    if not '.' in tmL:
        tmL += '.tmLanguage'

    return 'Packages/%s/%s' % (syntax_type, tmL)


def get_content_index(haystack, needle):
    '''Get the right needle position in haystack'''
    pos = haystack.find(needle)
    return pos + len(needle) if pos >= 0 else 0


def get_header_prefix(syntax_type, default=''):
    '''Get the header prefix'''
    header_prefix_mapping = merge_defaults_with_settings(
        HEADER_PREFIX_MAPPING, 'header_prefix_mapping')
    try:
        return header_prefix_mapping.get(syntax_type, default)
    except KeyError:
        return default


def get_header_content(syntax_type, path=None, file=None):
    '''Get the correctly computed header content'''
    header_prefix = get_header_prefix(syntax_type)
    content = '' if isinstance(
        file, str) and header_prefix in file else header_prefix
    return content + render_template(syntax_type, 'header', {'path': path})


def get_file_content(file, syntax_type, header):
    '''Get the correctly computed file content'''
    header_prefix = get_header_prefix(syntax_type)
    file_index = get_content_index(file, header_prefix)
    return file[0:file_index] + header + file[file_index:]


def template_header_exists(file, syntax_type):
    '''Return whether template header has been compiled in file'''
    template_header = get_template_part(syntax_type, 'header').strip()
    regex = r'\\{\\{[a-z\\_]+\\}\\}'
    return re.search(re.sub(regex, '.*', re.escape(template_header)), file)


def merge_dicts(*dicts):
    '''Merge any number of dicts into a new dict'''
    result = {}
    for dict in dicts:
        result.update(dict)
    return result


def merge_defaults_with_settings(default, setting_name):
    '''Merge default dict with package settings'''
    return merge_dicts(default, Settings().get(setting_name, {}))


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

        header = get_header_content(syntax_type, path)

        try:
            with open(path, 'w+') as f:
                f.write(header)

        except Exception as e:
            sublime.error_message(str(e))
            return

        view = Window().open_file(path)
        file_syntax = get_syntax_file(syntax_type)

        if os.path.exists(file_syntax) and os.path.isfile(file_syntax):
            try:
                block(view, view.set_syntax_file, file_syntax)
            except:
                pass

        block(view, view.show, 0)

    def new_view(self, syntax_type, name):
        header = get_header_content(syntax_type)
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
            path = get_dir_path()
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
        Window().show_input_panel(
            'File Name:', '',
            functools.partial(self.on_done, path), None, None)


class BackgroundAddHeaderThread(threading.Thread):
    '''Add header in background.'''

    def __init__(self, path):
        self.path = path
        super(BackgroundAddHeaderThread, self).__init__()

    def run(self):
        syntax_type = get_syntax_type(self.path)

        try:
            with open(self.path, 'r') as f:
                file = f.read()

            if not template_header_exists(file, syntax_type):
                header_content = get_header_content(
                    syntax_type, self.path, file)
                contents = get_file_content(file, syntax_type, header_content)
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

        view = View()
        view_content = view.substr(sublime.Region(0, view.size()))

        if not template_header_exists(view_content, syntax_type):
            header_content = get_header_content(
                syntax_type, path, view_content)
            header_prefix = get_header_prefix(syntax_type)
            view_index = get_content_index(view_content, header_prefix)
            self.view.insert(edit, view_index, header_content)


class FileHeaderAddHeaderCommand(sublime_plugin.WindowCommand):
    '''Conmmand: add `header` in a file or directory'''

    def is_hidden(self, path):
        '''Whether the file or dir is hidden'''

        hidden, platform = False, sublime.platform()
        if platform == 'windows':
            output, error = getOutputError('attrib %s' % path)
            if not error:
                try:
                    if output[4].upper() == 'H':
                        hidden = True
                except:
                    pass
        elif os.path.basename(path).startswith('.'):
            hidden = True
        return hidden

    def can_add(self, path):
        '''Whether can add header to path'''

        def can_add_to_dir(path):
            return enable_add_to_hidden_dir or (
                not enable_add_to_hidden_dir and
                not self.is_hidden(path))

        def can_add_to_file(path):
            return enable_add_to_hidden_file or (
                not enable_add_to_hidden_file and
                not self.is_hidden(path))

        if not os.path.exists(path):
            return False

        enable_add_to_hidden_dir, enable_add_to_hidden_file = map(
            Settings().get, (
                'enable_add_header_to_hidden_dir',
                'enable_add_header_to_hidden_file'
            )
        )

        if (os.path.isfile(path) and
                can_add_to_dir(os.path.dirname(path)) and
                can_add_to_file(path)):
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
            BackgroundAddHeaderThread(path).start()

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
                initial_text = View().file_name() or 'untitled'
            except:
                pass

        show_input_panel_when_add_header = Settings().get(
            'show_input_panel_when_add_header')

        if not show_input_panel_when_add_header:
            self.on_done(initial_text)
            return

        Window().run_command('hide_panel')
        Window().show_input_panel(
            'Modified File or Directory:',
            initial_text, self.on_done, None, None)


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

    def update_automatically(self, view, what):
        syntax_type = get_syntax_type(view.file_name())

        line_pattern = None
        lines = get_template_part(syntax_type, 'header').split('\n')
        regex = getattr(FileHeaderListener, '%s_REGEX' % what)

        for line in lines:
            search = regex.search(line)
            if search is not None:
                variable = search.group()
                index = line.find(variable)

                line_head, line_tail = '', line[index + len(variable):]
                for i in range(index - 1, -1, -1):
                    if line[i] != ' ':
                        space_start = i + 1
                        line_head = line[:space_start]
                        break

                for r in '.^$*+?{}[]()':
                    line_head = line_head.replace(r, '\\{0}'.format(r))

                line_pattern = '{0}.*\n'.format(line_head)
                break

        if line_pattern is not None:
            _ = view.find(line_pattern, 0)
            if(_ != sublime.Region(-1, -1) and _ is not None):
                a, b = _.a + space_start, _.b - 1
                file_name = get_file_name(view.file_name())

                if what == LAST_MODIFIED_BY:
                    strings = get_args(syntax_type)['last_modified_by']
                elif what == LAST_MODIFIED_TIME:
                    strings = datetime.now().strftime(get_strftime())
                elif what == FILE_NAME:
                    strings = file_name
                elif what == FILE_NAME_WITHOUT_EXTENSION:
                    strings = get_file_name_without_extension(file_name)
                elif what == FILE_PATH:
                    strings = get_file_path(view.file_name())

                strings = '{0}{1}{2}'.format(
                    ' ' * (index - space_start), strings, line_tail)

                region = sublime.Region(int(a), int(b))
                if view.substr(region) != strings:
                    view.run_command(
                        'file_header_replace',
                        {'a': a, 'b': b, 'strings': strings})

    def insert_template(self, view, exists):
        enable_add_template_to_empty_file = Settings().get(
            'enable_add_template_to_empty_file') and view.settings().get(
            'enable_add_template_to_empty_file', True)

        path = view.file_name()
        condition = (path and enable_add_template_to_empty_file
                     and view.size() <= 0)

        if exists:
            condition = (
                condition
                and os.path.exists(path)
                and os.path.isfile(path)
                and os.path.getsize(path) <= 0
            )

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
        enable_add_template_on_save = Settings().get(
            'enable_add_template_on_save', False)
        file_name = view.file_name()

        if isinstance(enable_add_template_on_save, str):
            search = re.search(enable_add_template_on_save, file_name)
            enable_add_template_on_save = search != None

        if enable_add_template_on_save:
            block(view, view.run_command,
                  'add_file_header', {'path': file_name})

        if view.id() in FileHeaderListener.new_view_id:
            if not enable_add_template_on_save:
                self.insert_template(view, False)
            index = FileHeaderListener.new_view_id.index(view.id())
            del FileHeaderListener.new_view_id[index]
        else:
            if view.is_dirty():
                self.update_automatically(view, LAST_MODIFIED_BY)
                self.update_automatically(view, LAST_MODIFIED_TIME)

    def on_activated(self, view):
        block(view, self.update_automatically, view, FILE_PATH)
        block(view, self.update_automatically, view, FILE_NAME)
        block(view, self.update_automatically,
              view, FILE_NAME_WITHOUT_EXTENSION)

        settings = view.settings()
        c_time, _ = get_time(view.file_name())
        if c_time is not None and settings.get('c_time', None) is None:
            settings.set('c_time', pickle.dumps(c_time))

        self.insert_template(view, True)
