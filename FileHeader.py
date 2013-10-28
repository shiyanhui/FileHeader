# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import os
import sys
import functools

from datetime import datetime

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_PATH = ROOT_PATH + '/template/'

sys.path.insert(0, ROOT_PATH)

def Window():
    return sublime.active_window()

def get_template(syntax_type):
    template_file = open('%s%s.tmpl' % (TEMPLATE_PATH, syntax_type), 'r')
    contents = template_file.read() + '\n'
    template_file.close()
    return contents

def render_template(syntax_type):
    from jinja2 import Template
    template = Template(get_template(syntax_type))
    render_string = template.render({'author': 'Lime', 
                                     'date': datetime.now() })
    return render_string

def get_syntax_type(name, syntax_type='Text'):
    name = name.split('.')
    if len(name) <= 1:
        return syntax_type

    syntax_map = {
        'asp': 'ASP',
        'c': 'C++',
        'cs': 'C#',
        'cpp': 'C++',
        'css': 'CSS',
        'go': 'Go',
        'htm': 'HTML',
        'html': 'HTML',
        'java': 'Java',
        'js': 'JavaScript',
        'pl': 'Perl',
        'php': 'PHP',
        'py': 'Python',
        'rb': 'Ruby',
        'txt': 'Text',
        'xml': 'XML',
    }

    try:
        syntax_type = syntax_map[name[-1]]
    except KeyError:
        pass

    return syntax_type

def get_syntax_file(syntax_type):
    return 'Packages/%s/%s.tmLanguage' % (syntax_type, syntax_type)


class FileHeaderNewFileCommand(sublime_plugin.WindowCommand):
    def on_done(self, paths, name):
        if not name:
            return 

        syntax_type = get_syntax_type(name)
        header = render_template(syntax_type)
        
        if not paths:
           new_file = Window().new_file()
           new_file.set_name(name)
           new_file.run_command('insert', {'characters': header})
           new_file.set_syntax_file(get_syntax_file(syntax_type))
           return

        path = paths[0]
        if(os.path.isdir(path)):
            file_name = os.path.join(path, name)
        else:
            file_name = os.path.join(os.path.dirname(path), name)

        if os.path.exists(file_name):
            sublime.error_message('File exists!')
            return

        try:
            with open(file_name, 'w+') as f:
                f.write(header)
                f.close()
        except Exception as e:
            sublime.error_message(e)
            return

        new_file = Window().open_file(file_name)
        new_file.set_syntax_file(get_syntax_file(syntax_type))

    def run(self, paths=[]):
        Window().run_command('hide_panel')
        Window().show_input_panel(caption='File Name:', initial_text='', 
                                  on_done=functools.partial(self.on_done, paths
                                  ), on_change=None, on_cancel=None)


class AddFileHeaderCommand(sublime_plugin.TextCommand):
    def run(self, edit, path):
        syntax_type = get_syntax_type(path)
        header = render_template(syntax_type)
        self.view.set_syntax_file(get_syntax_file(syntax_type))
        self.view.insert(edit, 0, header)


class FileHeaderAddHeaderCommand(sublime_plugin.WindowCommand):
    def add(self, path):
        modified_file = Window().open_file(path)

        def _add():
            if modified_file.is_loading():
                sublime.set_timeout(_add, 100)
            else:
                modified_file.run_command('add_file_header', 
                                          {'path': path})
        _add()

    def walk(self, path):
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
        if paths:
            initial_text = os.path.abspath(paths[0])
        else:
            initial_text = Window().active_view().file_name()

        Window().run_command('hide_panel')
        Window().show_input_panel(caption='File or Directory:', 
                                  initial_text=initial_text, 
                                  on_done=self.on_done, on_change=None,
                                  on_cancel=None)

