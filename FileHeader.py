#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2013-10-29 11:28:36
# @Author: Lime
# @Email: shiyanhui66@gmail.com
# @Last modified: 2013-10-29 12:55:42

import sublime
import sublime_plugin
import functools
import os
import sys
import re

from datetime import datetime

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_PATH = ROOT_PATH + '/template/'
PLUGIN_NAME = 'FileHeader'

sys.path.insert(0, ROOT_PATH)

def Window():
    '''Get current active window'''

    return sublime.active_window()

def Settings():
    '''Get settings'''

    return sublime.load_settings('%s.sublime-settings' % PLUGIN_NAME)

def get_template(syntax_type):
    '''Get template correspond `syntax_type`'''

    template_file = open('%s%s.tmpl' % (TEMPLATE_PATH, syntax_type), 'r')
    contents = template_file.read() + '\n'
    template_file.close()
    return contents

def get_strftime():
    '''Get `time_format` setting'''

    options = Settings().get('options')
    _ = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%H:%M:%S']
    try:
        format = _[options['time_format']]
    except IndexError:
        format = _[0]
    return format

def get_args(syntax_type):
    '''Get the args rendered'''

    options = Settings().get('options')
    args = Settings().get('Default')
    args.update(Settings().get(syntax_type, {}))

    format = get_strftime()
    time = datetime.now().strftime(format)

    if options['create_time']:
        args.update({'create_time': time})

    if options['modified_time']:
        args.update({'modified_time': time})

    return args

def render_template(syntax_type):
    '''Render the template correspond `syntax_type`'''

    from jinja2 import Template
    template = Template(get_template(syntax_type))
    render_string = template.render(get_args(syntax_type))
    return render_string

def get_syntax_type(name):
    '''Judge `syntax_type` according to to `name`'''
    options = Settings().get('options')
    syntax_type = options['syntax_when_not_match']

    name = name.split('.')
    if len(name) <= 1:
        return syntax_type

    syntax_map = {
        'as': 'ActionScript',
        'scpt': 'AppleScript',
        'asp': 'ASP',
        'aspx': 'ASP',
        'c': 'C++',
        'cs': 'C#',
        'cpp': 'C++',
        'clj': 'Clojure',
        'css': 'CSS',
        'd': 'D',
        'erl': 'Erlang',
        'go': 'Go',
        'hs': 'Haskell',
        'htm': 'HTML',
        'html': 'HTML',
        'java': 'Java',
        'js': 'JavaScript',
        'tex': 'LaTeX',
        'lisp': 'Lisp',
        'lua': 'Lua',
        'mat': 'Matlab',
        'cc': 'Objective-C',
        'pas': 'Pascal',
        'pl': 'Perl',
        'php': 'PHP',
        'py': 'Python',
        'rb': 'Ruby',
        'scala': 'Scala',
        'sh': 'ShellScript',
        'sql': 'SQL',
        'tcl': 'TCL',
        'txt': 'Text',
        'xml': 'XML',
    }

    try:
        syntax_type = syntax_map[name[-1]]
    except KeyError:
        pass

    return syntax_type

def get_syntax_file(syntax_type):
    '''Get syntax file path'''

    return 'Packages/%s/%s.tmLanguage' % (syntax_type, syntax_type)

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
            sublime.error_message(e)
            return

        new_file = Window().open_file(path)
        block(new_file, new_file.set_syntax_file, get_syntax_file(syntax_type))

    def on_done(self, paths, name):
        if not name:
            return 

        syntax_type = get_syntax_type(name)
        
        if not paths:
            current_view = Window().active_view()
            if current_view:
                file_name = current_view.file_name()
                path = os.path.join(os.path.dirname(file_name), name)
                self.new_file(path, syntax_type)
            else:
                header = render_template(syntax_type)
                new_file = Window().new_file()
                new_file.set_name(name)
                new_file.run_command('insert', {'characters': header})
                new_file.set_syntax_file(get_syntax_file(syntax_type))
            return

        path = paths[0]
        if(os.path.isdir(path)):
            path = os.path.join(path, name)
        else:
            path = os.path.join(os.path.dirname(path), name)

        self.new_file(path, syntax_type)
        
    def run(self, paths=[]):
        Window().run_command('hide_panel')
        Window().show_input_panel(caption='File Name:', initial_text='', 
                                  on_done=functools.partial(self.on_done, paths
                                  ), on_change=None, on_cancel=None)


class AddFileHeaderCommand(sublime_plugin.TextCommand):
    '''Command: add `header` in a file'''

    def run(self, edit, path):
        syntax_type = get_syntax_type(path)
        header = render_template(syntax_type)
        self.view.set_syntax_file(get_syntax_file(syntax_type))
        self.view.insert(edit, 0, header)


class FileHeaderAddHeaderCommand(sublime_plugin.WindowCommand):
    '''Conmmand: add `header` in a file or directory'''

    def add(self, path):
        '''Add to a file'''

        modified_file = Window().open_file(path)
        block(modified_file, modified_file.run_command, 
              'add_file_header', {'path': path})

    def walk(self, path):
        '''Add files in the path'''
        
        for root, subdirs, files in os.walk(path):
            for f in files:
                file_name = os.path.join(root, f)
                self.add(file_name)
                
    def on_done(self, path):
        if not path:
            return

        if not os.path.exists(path):
            sublime.error_message('Path not exists!')
            return

        path = os.path.abspath(path)

        if os.path.isfile(path):
            self.add(path)
        elif os.path.isdir(path):
            self.walk(path)

    def run(self, paths=[]):
        initial_text = (os.path.abspath(paths[0]) if paths else 
                        Window().active_view().file_name())

        Window().run_command('hide_panel')
        Window().show_input_panel(caption='Modified File or Directory:', 
                                  initial_text=initial_text, 
                                  on_done=self.on_done, on_change=None,
                                  on_cancel=None)


class FileHeaderReplaceCommand(sublime_plugin.TextCommand):
    '''Replace contents in the `region` with `stirng`'''

    def run(self, edit, region, strings):
        region = sublime.Region(region[0], region[1])
        self.view.replace(edit, region, strings)

class UpdateModifiedTimeListener(sublime_plugin.EventListener):
    '''Auto update `modified_time` when save file'''

    MODIFIED_REGEX = re.compile('\{\{\s*modified_time\s*\}\}') 

    @classmethod
    def time_pattern(cls):
        options = Settings().get('options')

        choice = options['time_format']
        _ = [0, 1, 2]
        if choice not in _:
            choice = 0

        _ = ['\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}', 
             '\d{4}-\d{2}-\d{2}', '\d{2}:\d{2}:\d{2}']
        return _[choice]

    def on_pre_save(self, view):
        options = Settings().get('options')
        if not options['modified_time']:
            return

        syntax_type = get_syntax_type(view.file_name())
        template = get_template(syntax_type)    

        line_pattern = None
        lines = template.split('\n')
        for line in lines:
            search = UpdateModifiedTimeListener.MODIFIED_REGEX.search(line)
            if search is not None:
                var = search.group()
                line_pattern = line.replace(var, 
                                    UpdateModifiedTimeListener.time_pattern())
                break

        if line_pattern is not None:
            _ = view.find(line_pattern, 0)
            if(_ != (-1, -1) and _ is not None):
                region = view.find(UpdateModifiedTimeListener.time_pattern(), 
                                   _.a)

                strftime = get_strftime()
                time = datetime.now().strftime(strftime)
                view.run_command('file_header_replace', 
                                 {'region': (region.a, region.b), 
                                  'strings': time})





