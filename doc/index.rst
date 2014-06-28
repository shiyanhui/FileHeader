**FileHeader** 是一个Sublime Text的File Templating插件。目前ST已经有几款File Templating插件了，像SublimeTmpl、Template​Ninja、File​Templates等，但是这些插件的功能太简单了，他们几乎都使用了ST的内置snippets来实现模板的渲染，并且支持的语言很有限(像SublimeTmpl仅支持Python、Ruby、JavaScript、PHP、HTML、CSS、XML)，有的插件仅仅支持ST2(File​Templates)，还有的使用起来及其不效率。

本插件与其他插件有很大的不同。

- 将一个模板文件分为header和body两部分。允许用户自定义自己的模板文件。
- FileHeader能够自动的监测创建新文件动作，自动的添加模板。
- 不仅支持创建已经使用模板初始化好的文件，而且支持将header添加到已经存在的文件头部，并且支持批量添加。
- 使用了非常强大并且很容易使用的 `Jinja2 <http://jinja.pocoo.org/docs>`_ 模板系统，在模板文件里你可以完成很多复杂的初始化。
- 几乎支持所有的编程语言，并且支持用户自定义语言。
- 能够自动的更新文件最后修改时间。
- 能够自动的更新文件最后的修改者，这在协同开发中是一个很有用的功能。
- 支持ST2/ST3。

安装
------

可以通过 **Package Control** 搜索 **FileHeader** 安装。

或者：

进入到你的"Packages"文件夹 **(Preferences / Browse Packages)** ，然后：

.. code-block:: python
    
    git clone git@github.com:shiyanhui/FileHeader.git

使用
------

FileHeader非常容易使用。

创建新文件
`````````

FileHeader能够自动的监测创建新文件动作，自动的添加模板。因此你可以用别的插件创建新文件，FileHeader会自动的给你添加模板。

- Sidebar Menu
    
  .. image:: https://raw.github.com/shiyanhui/shiyanhui.github.io/master/images/FileHeader/new-file.gif

- Shortcuts    

  The default shortcuts is **super+alt+n** on OS X, **ctrl+alt+n** on Windows and Linux.

- Context Menu

  Similar to **Sidebar Menu**.


添加文件头
`````````

- Sidebar Menu
    
  .. image:: https://raw.github.com/shiyanhui/shiyanhui.github.io/master/images/FileHeader/add-header.gif

- Shortcuts

  The default shortcuts is **super+alt+a** on OS X, **ctrl+alt+a** on Windows and Linux.

- Context Menu

  Similar to **Sidebar Menu**.
    
批量添加文件头
`````````

.. image:: https://raw.github.com/shiyanhui/shiyanhui.github.io/master/images/FileHeader/add-header-dir.gif


自动更新文件修改时间和最后修改者
`````````

.. image:: https://raw.github.com/shiyanhui/shiyanhui.github.io/master/images/FileHeader/update.gif


详细设置及文档请看 `GitHub <https://github.com/shiyanhui/FileHeader>`_ 。