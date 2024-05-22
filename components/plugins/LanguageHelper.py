from plugin_interface import PluginInterface

import asyncio

async def check_syntax_async(content):
    print("Hello!")

class LanguageHelper(PluginInterface):
    def run(self, main_window):
        current_tab = main_window.stacked_widget.currentWidget()
        if current_tab:
            content = current_tab.current_tab.toPlainText()
            asyncio.run(check_syntax_async(content))

    def get_name(self):
        return "LanguageHelper"

    def get_version(self):
        return "1.0.0"

    def get_author(self):
        return "CattoPad"

    def get_description(self):
        return "Fixes your grammar for you"

    def run_on_startup(self):
        return True
    
    def needs_runtime(self):
        return True