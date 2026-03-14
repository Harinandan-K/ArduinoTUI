from textual.app import App, ComposeResult
from textual.widgets import Static, DirectoryTree, RichLog

class TerminalView(RichLog):
    pass

class FolderTree(DirectoryTree):
    pass

class CodeEditor(Static):

    def load_new_path(self,path):
        try:
            with open(path,"r") as code_file:
                code_content : str = code_file.read()

            if not code_content:
                code_content : str  = "Selected file is empty"

            self.update(code_content)

        except FileNotFoundError:
            code_content = "Selected file does not exist."
            self.update(code_content)

        except UnicodeDecodeError:
            code_content = "Selected file is not a text based file and can not be viewed"
            self.update(code_content)



# Main app class
class ArduinoTUI(App):
    
    CSS = """
    CodeEditor {
        background: $surface;
        border: round #4FC7FF;           
        height: 100%;           
    }

    FolderTree {
        background: $surface;
        border: round #4FC7FF; 
        dock: left;          
        width: 20%;           
        height: 77%;           
    }

    TerminalView {
        background: $surface;
        border: round #F54927; 
        dock: bottom;          
        width: 100%;           
        height: 25%;           
    }
    """
    
    BINDINGS = [
        # ("d", "toggle_dark_mode", "Toggle dark mode")
        # ("b", "toggle_FolderTree", "Toggle folder tree view")
    ]

    def compose(self) -> ComposeResult:

        yield CodeEditor("Select a file to view code") 
        yield FolderTree("./")
        yield TerminalView()

    ''' 
    def action_toggle_dark_mode(self):
        if self.theme == "textual-dark":
            self.theme = "textual-light"

        else:
            self.theme = "textual-dark"
    '''

    # catch the path returned by FolderTree class and pass to CodeEditor
    def on_directory_tree_file_selected(self, event : DirectoryTree.FileSelected):
        new_file_path = event.path
        editor_widgets = self.query_one(CodeEditor)
        editor_widgets.load_new_path(new_file_path)


if __name__ == "__main__":
    app = ArduinoTUI()
    app.run()