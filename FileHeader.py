#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import functools
import os
import sys
import re
import threading

from datetime import datetime

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_PATH = ROOT_PATH + '/template/'
PLUGIN_NAME = 'FileHeader'

sys.path.insert(0, ROOT_PATH)

def Window():
    '''Get current act``ive window'''

    return sublime.active_window()

def Settings():
    '''Get settings'''

    return sublime.load_settings('%s.sublime-settings' % PLUGIN_NAME)

def get_template(syntax_type):
    '''Get template correspond `syntax_type`'''

    tmpl_name = '%s.tmpl' % syntax_type

    tmpl_file = os.path.join(TEMPLATE_PATH, tmpl_name)

    options = Settings().get('options')
    custom_template_path = options['custom_template_path']
    if custom_template_path:
        _ = os.path.join(custom_template_path, tmpl_name)
        if os.path.exists(_) and os.path.isfile(_):
            tmpl_file = _

    try:
        template_file = open(tmpl_file, 'r')
        contents = template_file.read() + '\n'
        template_file.close()
    except Exception as e:
        sublime.error_message(e)
        contents = ''
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
    try:
        template = Template(get_template(syntax_type))
        render_string = template.render(get_args(syntax_type))
    except Exception as e:
        sublime.error_message(e)
        render_string = ''
    return render_string

def get_syntax_type(name):
    '''Judge `syntax_type` according to to `name`'''
    options = Settings().get('options')
    syntax_type = options['syntax_when_not_match']
    file_suffix_mapping = options['file_suffix_mapping']

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
        try:
            block(new_file, new_file.set_syntax_file, get_syntax_file(syntax_type))
        except:
            pass
        block(new_file, new_file.show_at_center, 0)

    def new_view(self, syntax_type, name):
        header = render_template(syntax_type)
        new_file = Window().new_file()
        new_file.set_name(name)
        new_file.run_command('insert', {'characters': header})
        try:
            new_file.set_syntax_file(get_syntax_file(syntax_type))
        except:
            pass

    def on_done(self, paths, name):
        if not name:
            return 

        syntax_type = get_syntax_type(name)
        
        if not paths:
            current_view = Window().active_view()
            if current_view:
                file_name = current_view.file_name()
                if file_name is None:
                    self.new_view(syntax_type, name)
                else:
                    path = os.path.join(os.path.dirname(file_name), name)
                    self.new_file(path, syntax_type)
            else:
                self.new_view(syntax_type, name)
            return

        path = paths[0]
        if(os.path.isdir(path)):
            path = os.path.join(path, name)
        else:
            path = os.path.join(os.path.dirname(path), name)

        self.new_file(path, syntax_type)
        
    def run(self, paths=[]):
        Window().run_command('hide_panel')
        Window().show_input_panel('File Name:', '', functools.partial(
                                  self.on_done, paths), None, None)


class BackgroundAddHeaderThread(threading.Thread):
    '''Add header in background.'''

    def __init__(self, path):
        self.path = path
        super(BackgroundAddHeaderThread, self).__init__()

    def run(self):
            
        syntax_type = get_syntax_type(self.path)
        header = render_template(syntax_type)

        try:
            with open(self.path, 'r') as f:
                contents = header + f.read()
                f.close()

            with open(self.path, 'w') as f:
                f.write(contents)
                f.close()
        except Exception as e:
            sublime.error_message(e)


class AddFileHeaderCommand(sublime_plugin.TextCommand):
    '''Command: add `header` in a file'''

    def run(self, edit, path):
        syntax_type = get_syntax_type(path)
        header = render_template(syntax_type)
        self.view.insert(edit, 0, header)

class FileHeaderAddHeaderCommand(sublime_plugin.WindowCommand):
    '''Conmmand: add `header` in a file or directory'''

    def add(self, path):
        '''Add to a file'''

        options = Settings().get('options')
        whether_open_file = options['open_file_when_add_header_to_directory'] 

        if whether_open_file:
            modified_file = Window().open_file(path)
            block(modified_file, modified_file.run_command, 
                  'add_file_header', {'path': path})
            block(modified_file, modified_file.show_at_center, 0)
        else:
            thread = BackgroundAddHeaderThread(path)
            thread.start()

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
        initial_text = ''
        if paths:
            initial_text = os.path.abspath(paths[0])
        else:
            try:
                initial_text = Window().active_view().file_name()
            except:
                pass

        options = Settings().get('options')
        show_input_panel_when_add_header = (options[
            'show_input_panel_when_add_header'])

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
                                 {'a': region.a, 
                                  'b': region.b,
                                  'strings': time})
