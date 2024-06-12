![output](https://github.com/OMouta/CattoPad/assets/79537410/6b2989e1-b019-4ffd-9d6b-cbe09869ec89)

# Building the Application with PyInstaller

To build this application into a standalone executable using PyInstaller, follow these steps:

1. Install PyInstaller if you haven't already. You can do this using pip.
2. Navigate to the directory containing your Python script (main.py in this case) in the terminal.
3. Run the following command to create a single executable file:

    ```
    pyinstaller main.py
    ```

    This will create a `dist` directory in your current directory. Inside `dist`, you will find your standalone executable file named `main.exe`.

## How the Application Works

This application is a simple text editor built with PyQt5. It allows you to create, open, save, and close tabs, each containing a text document. It also supports markdown preview and zooming in/out.

Here's a brief overview of the main features:

- Tabs: You can create a new tab by selecting 'New Tab' from the 'File' menu or by pressing Ctrl+N. Each tab is associated with a plain text editor where you can write and edit text.
- Opening Files: You can open a file by selecting 'Open' from the 'File' menu or by pressing Ctrl+O. This will open a dialog where you can select the file to open. The content of the file will be loaded into a new tab.
- Saving Files: You can save the content of the current tab to a file by selecting 'Save' from the 'File' menu or by pressing Ctrl+S. If the tab is associated with a file, the content will be saved to that file. Otherwise, a dialog will open where you can specify the file to save to.
- Closing Tabs: You can close the current tab by selecting 'Close Tab' from the 'File' menu or by pressing Ctrl+W. If there are unsaved changes, you will be asked whether you want to save them.
- Markdown Preview: You can toggle the markdown preview by selecting 'Markdown Preview' from the 'View' menu or by pressing Ctrl+M. This will show a preview of the current tab's content as rendered markdown on the right side of the window.
- Zooming: You can zoom in and out by selecting 'Zoom In' or 'Zoom Out' from the 'View' menu, or by pressing Ctrl++ and Ctrl+-, respectively.
- Themes: You can switch the theme of the editor by selecting a theme from the 'Themes' submenu in the 'Editor' menu.

The state of the application (including the content of all tabs) is saved when the application is closed and restored when the application is opened.
