from plugin_interface import PluginInterface

class SampleTextPlugin(PluginInterface):
    def run(self, main_window):
        current_tab = main_window.stacked_widget.currentWidget()
        if current_tab:
            current_tab.insertPlainText("# Welcome to CattoPad!\n\n")
            
            current_tab.insertPlainText("This is a sample text inserted by a plugin.\n\n")
            
            current_tab.insertPlainText("- This is a list item.\n")
            current_tab.insertPlainText("- This is another list item.\n")
            current_tab.insertPlainText("- This is the last list item.\n\n")
            
            current_tab.insertPlainText("## CattoPad Preview\n\n")
            current_tab.insertPlainText("Ctrl + M - Show Markdown Preview\n\n")
            
            current_tab.insertPlainText("You can now start typing your own text here.\n")

    def get_name(self):
        return "Welcome Plugin"

    def get_version(self):
        return "1.0.0"

    def get_author(self):
        return "CattoPad"

    def get_description(self):
        return "Welcome message for new users."

    def run_on_startup(self):
        return False
    
    def needs_runtime(self):
        return False