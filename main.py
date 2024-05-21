from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QFileDialog, QAction, QVBoxLayout, QWidget, QListWidget, QStackedWidget, QSplitter, QTextBrowser, QMessageBox, QLabel
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtGui import QIcon, QKeySequence, QFontDatabase, QFont

from markdown import markdown

import json
import sys
import os

import importlib.util

from plugin_interface import PluginInterface

script_dir = os.path.dirname(__file__)
components_dir = os.path.join(script_dir, 'components')
        
def load_stylesheet(filename):
    file = QFile(filename)
    if not file.exists():
        print(f"Error: The file {filename} does not exist.")
        return ""
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    stylesheet = stream.readAll()
    return stylesheet

class MainWindow(QMainWindow):
    
    def save_state(self):
        state = {
            'tabs': [],
            'current_tab': self.stacked_widget.currentIndex(),
            'markdown_preview_visible': self.markdown_preview.isVisible(),
        }
    
        for i in range(self.stacked_widget.count()):
            tab = self.stacked_widget.widget(i)
            tab_name = self.list_widget.item(i).text()
            tab_file_path = self.file_paths.get(str(id(tab)), "")
            state['tabs'].append({
                'content': tab.toPlainText(),
                'zoom_level': tab.font().pointSize(),
                'name': tab_name,
                'file_path': tab_file_path,
            })
    
        with open('temp/state.json', 'w') as file:
            json.dump(state, file)

    def load_state(self):
        if not os.path.exists('temp/state.json'):
            return

        with open('temp/state.json', 'r') as file:
            state = json.load(file)

        for i, tab_state in enumerate(state['tabs']):
            self.add_tab()
            tab = self.stacked_widget.widget(i)
            tab.setPlainText(tab_state['content'])
            font = tab.font()
            font.setPointSize(tab_state['zoom_level'])
            tab.setFont(font)
            self.list_widget.item(i).setText(tab_state['name'])
            self.file_paths[str(id(tab))] = tab_state['file_path']

        self.stacked_widget.setCurrentIndex(state['current_tab'])

        if state['markdown_preview_visible']:
            self.markdown_preview.show()
        else:
            self.markdown_preview.hide()

    def closeEvent(self, event):
        self.save_state()
        super().closeEvent(event)
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.plugins = {}
        
        def load_plugins(self):
            plugins_dir = 'components/plugins'
            plugin_files = [f for f in os.listdir(plugins_dir) if f.endswith('.py')]

            plugins_menu = self.menuBar().addMenu("Plugins")

            for plugin_file in plugin_files:
                try:
                    spec = importlib.util.spec_from_file_location("plugin_module", os.path.join(plugins_dir, plugin_file))
                    plugin_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(plugin_module)
                    for item_name in dir(plugin_module):
                        item = getattr(plugin_module, item_name)
                        if isinstance(item, type) and issubclass(item, PluginInterface) and item is not PluginInterface:
                            plugin_class = item
                            plugin_instance = plugin_class()
                
                            plugin_action = QAction(f"{plugin_instance.get_name()} (v{plugin_instance.get_version()}) by {plugin_instance.get_author()}: {plugin_instance.get_description()}", self)
                
                            if plugin_instance.run_on_startup():
                                plugin_instance.run(self)
                            else:
                                plugin_action.triggered.connect(lambda: plugin_instance.run(self))
                
                            self.plugins[plugin_instance.get_name()] = plugin_instance
                
                            plugins_menu.addAction(plugin_action)
                except Exception as e:
                    error_action = QAction(f"Failed to load plugin {plugin_file}: {str(e)}", self)
                    print(f"Failed to load plugin {plugin_file}: {str(e)}")
                    plugins_menu.addAction(error_action)
                
        self.unsaved_tabs = set()
        
        self.setWindowTitle('CattoPad')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('components/assets/icon.ico'))
        
        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(200)
        self.stacked_widget = QStackedWidget()
        
        self.list_widget.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        self.stacked_widget.currentChanged.connect(self.update_markdown_preview)
        
        self.markdown_preview = QTextBrowser()
        self.markdown_preview.hide()
        
        splitter = QSplitter()
        splitter.addWidget(self.list_widget)
        splitter.addWidget(self.stacked_widget)
        splitter.addWidget(self.markdown_preview)

        layout = QVBoxLayout()
        layout.addWidget(splitter)

        main_widget = QWidget()
        main_widget.setLayout(layout)

        self.setCentralWidget(main_widget)

        self.create_menu_bar()

        self.file_paths = {}
        self.load_file_paths()
        
        self.load_state()
        print("Loaded state")
        load_plugins(self)
        print("Loaded plugins")
        
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            self.open_file(file_path)
        
        font_database = QFontDatabase()
        for font_file in os.listdir('components/fonts'):
            font_database.addApplicationFont(os.path.join('components/fonts', font_file))
    
    def mark_unsaved(self):
        current_tab = self.stacked_widget.currentWidget()
        current_index = self.stacked_widget.currentIndex()
        current_item = self.list_widget.item(current_index)
        if current_tab and current_item.text()[-1] != "*":
            current_item.setText(current_item.text() + "*")
            self.unsaved_tabs.add(current_tab.objectName())
    
    def add_tab(self):
        new_tab = QPlainTextEdit()
        new_tab.setObjectName(str(id(new_tab)))
        new_tab.textChanged.connect(self.update_markdown_preview)
        self.stacked_widget.addWidget(new_tab)
        self.list_widget.addItem("Untitled")
        new_tab.textChanged.connect(self.mark_unsaved)

    def remove_tab(self):
        current_index = self.list_widget.currentRow()
        current_tab = self.stacked_widget.widget(current_index)
        current_tab_name = current_tab.objectName()

        if current_tab_name in self.file_paths:
            del self.file_paths[current_tab_name]

        self.save_file_paths()
        self.stacked_widget.removeWidget(current_tab)
        self.list_widget.takeItem(current_index)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        main_menu = menu_bar.addMenu('Editor')
    
        switch_theme = main_menu.addMenu('Themes')
    
        themes_dir = 'components/themes'
        theme_files = os.listdir(themes_dir)
    
        for theme_file in theme_files:
            theme_action = QAction(theme_file, self)
            theme_action.triggered.connect(lambda checked, theme_file=theme_file: self.switch_theme(os.path.join(themes_dir, theme_file)))
            switch_theme.addAction(theme_action)
        
        font_database = QFontDatabase()
        font_menu = main_menu.addMenu("Fonts")
        
        for font_name in font_database.families():
            font_action = QAction(font_name, self)
            font_action.setFont(QFont(font_name))  # Set the font of the QAction's text
            font_action.triggered.connect(lambda checked, font_name=font_name: self.switch_font(font_name))
            font_menu.addAction(font_action)
    
        file_menu = menu_bar.addMenu('File')
    
        new_tab_action = QAction('New Tab', self)
        new_tab_action.setShortcut(QKeySequence.New)
        new_tab_action.triggered.connect(self.add_tab)
        file_menu.addAction(new_tab_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
    
        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
    
        save_as_action = QAction('Save As', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        close_tab_action = QAction('Close Tab', self)
        close_tab_action.setShortcut('Ctrl+W')
        close_tab_action.triggered.connect(self.close_tab)
        file_menu.addAction(close_tab_action)
    
        view_menu = self.menuBar().addMenu('View')

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        markdown_preview_action = QAction('Markdown Preview', self)
        markdown_preview_action.setShortcut('Ctrl+M')
        markdown_preview_action.triggered.connect(self.toggle_markdown_preview)
        view_menu.addAction(markdown_preview_action)
    
    def toggle_markdown_preview(self):
        if self.markdown_preview.isVisible():
            self.markdown_preview.hide()
        else:
            self.markdown_preview.show()
            self.update_markdown_preview()
    
    def update_markdown_preview(self):
        current_tab = self.stacked_widget.currentWidget()
        if current_tab:
            markdown_text = current_tab.toPlainText()
            html = markdown(markdown_text)
            self.markdown_preview.setHtml(html)
        
    def zoom_in(self):
        current_tab = self.stacked_widget.currentWidget()
        if current_tab:
            font = current_tab.font()
            size = font.pointSize()
            if size < 30:  # limit the zoom in size
                font.setPointSize(size + 1)
                current_tab.setFont(font)

    def zoom_out(self):
        current_tab = self.stacked_widget.currentWidget()
        if current_tab:
            font = current_tab.font()
            size = font.pointSize()
            if size > 5:  # limit the zoom out size
                font.setPointSize(size - 1)
                current_tab.setFont(font)
        
    def switch_theme(self, theme_file):
        stylesheet = load_stylesheet(theme_file)
        self.setStyleSheet(stylesheet)
    
    def switch_font(self, font_name):
        font = QFont(font_name)
        current_tab = self.stacked_widget.currentWidget()
        if current_tab:
            current_tab.setFont(font)

    def load_file_paths(self):
        if os.path.exists('temp/file_paths.json'):
            with open('temp/file_paths.json', 'r') as file:
                self.file_paths = json.load(file)
    
    def save_file_paths(self):
        with open('temp/file_paths.json', 'w') as file:
            json.dump(self.file_paths, file)
    
    def open_file(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, 'Open file')

        if file_path:
            file = open(file_path, 'r')
            content = file.read()
            file.close()

            self.add_tab()
            current_index = self.stacked_widget.count() - 1
            self.stacked_widget.setCurrentIndex(current_index)
            current_tab = self.stacked_widget.currentWidget()

            current_tab.setPlainText(content)

            current_tab_name = current_tab.objectName()
            self.file_paths[current_tab_name] = file_path

            self.save_file_paths()

            # Update tab name to file name + extension
            file_name = os.path.basename(file_path)
            current_index = self.stacked_widget.currentIndex()
            self.list_widget.item(current_index).setText(file_name)
    
    def save_file(self):
        current_tab = self.stacked_widget.currentWidget()
        content = current_tab.toPlainText()
    
        current_tab_name = current_tab.objectName()
        if current_tab_name in self.file_paths:
            file_path = self.file_paths[current_tab_name]
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save file')
    
        if file_path:
            if current_tab_name in self.unsaved_tabs:
                self.unsaved_tabs.remove(current_tab_name)
            with open(file_path, 'w') as file:
                file.write(content)
    
            self.file_paths[current_tab_name] = file_path
            self.save_file_paths()
    
            # Update tab name to file name + extension
            file_name = os.path.basename(file_path)
            current_index = self.stacked_widget.currentIndex()
            self.list_widget.item(current_index).setText(file_name)
    
    def close_tab(self):
        current_index = self.list_widget.currentRow()
        current_tab = self.stacked_widget.widget(current_index)
        current_tab_name = current_tab.objectName()

        if current_tab_name in self.unsaved_tabs:
            reply = QMessageBox.question(self, 'Unsaved Changes',
                                         "There are unsaved changes. Do you want to save them?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)

            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        self.remove_tab()

        if current_tab_name in self.file_paths:
            del self.file_paths[current_tab_name]

        self.save_file_paths()
    
    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save file as')

        if file_path:
            current_tab = self.stacked_widget.currentWidget()
            current_tab_name = current_tab.objectName()
            content = current_tab.toPlainText()
            with open(file_path, 'w') as file:
                file.write(content)
                file.close()

            # Update tab name to file name + extension
            file_name = os.path.basename(file_path)
            self.unsaved_tabs.remove(current_tab_name)
            current_index = self.stacked_widget.currentIndex()
            self.list_widget.item(current_index).setText(file_name)

stylesheet = load_stylesheet("components/themes/classic.css")

app = QApplication(sys.argv)

app.setStyleSheet(stylesheet)
app.setApplicationName('CattoPad')
app.setApplicationDisplayName('CattoPad')
app.setWindowIcon(QIcon('components/assets/icon.ico'))
app.setApplicationVersion('1.0')
app.setOrganizationName('Tiago Mouta')

main_window = MainWindow()
main_window.show()

sys.exit(app.exec_())