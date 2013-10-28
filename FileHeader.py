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

def refresh():
    try:
        sublime.set_timeout(lambda:sublime.active_window().run_command(
                            'refresh_folder_list'), 200);
        sublime.set_timeout(lambda:sublime.active_window().run_command(
                            'refresh_folder_list'), 1300);
    except:
        pass

class FileHeaderNewFileCommand(sublime_plugin.WindowCommand):
    def get_template(self, syntax_type):
        template_file = open('%s%s.tmpl' % (TEMPLATE_PATH, syntax_type), 'r')
        contents = template_file.read() + '\n'
        template_file.close()
        return contents

    def render_template(self, syntax_type):
        from jinja2 import Template
        template = Template(self.get_template(syntax_type))
        render_string = template.render({'author': 'Lime', 
                                         'date': datetime.now() })
        return render_string

    def syntax_type(self, name, syntax_type='Text'):
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

    def get_syntax_file(self, syntax_type):
        return 'Packages/%s/%s.tmLanguage' % (syntax_type, syntax_type)

    def on_done(self, paths, name):
        if not name:
            return 

        syntax_type = self.syntax_type(name)
        header = self.render_template(syntax_type)

        if not paths:
           new_file = Window().new_file()
           new_file.set_name(name)
           new_file.run_command('insert', {'characters': header})
           new_file.set_syntax_file(self.get_syntax_file(syntax_type))
           return

        paths = paths[0]
        if(os.path.isdir(paths)):
            file_name = os.path.join(paths, name)
        else:
            file_name = os.path.join(os.path.dirname(paths), name)

        if os.path.exists(file_name):
            sublime.error_message('File exists!')
            return

        try:
            with open(file_name, 'w+') as f:
                f.write(header)
                f.close()
        except Exception(e):
            sublime.error_message(e)
            return

        new_file = Window().open_file(file_name)
        new_file.set_syntax_file(self.get_syntax_file(syntax_type))
        refresh()

    def run(self, paths=[]):
        Window().run_command('hide_panel');
        Window().show_input_panel(caption='File Name:', initial_text='', 
                                  on_done=functools.partial(self.on_done, paths
                                  ), on_change=None, on_cancel=None)

class FileHeaderAddHeaderCommand(sublime_plugin.TextCommand):
    def get_template(self):
        template_file = open(TEMPLATE_PATH + 'python.tmpl', 'r')
        contents = template_file.read() + '\n'
        template_file.close()
        return contents

    def render_template(self):
        template = Template(self.get_template())
        render_string = template.render({'author': 'Lime', 
                                         'date': datetime.now() })
        return render_string

    def run(self, edit):
        header = self.render_template()
        self.view.insert(edit, 0, header)
