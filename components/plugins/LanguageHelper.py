from plugin_interface import PluginInterface
from spellchecker import SpellChecker

import asyncio

async def check_syntax_async(content):
    spell = SpellChecker()

    # find those words that may be misspelled
    misspelled = spell.unknown(content.split())

    for word in misspelled:
        # Get the one 'most likely' answer
        print(f"{word} is misspelled. Did you mean {spell.correction(word)}?")

class LanguageHelper(PluginInterface):
    def run(self, main_window):
        while main_window.stacked_widget:
            current_tab = main_window.stacked_widget.currentWidget()
            if current_tab:
                print("Checking syntax")
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
        return False