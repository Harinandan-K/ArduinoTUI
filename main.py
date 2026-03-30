import subprocess
import json
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Static, DirectoryTree, RichLog, Input, OptionList
from textual.widgets.option_list import Option
from textual.events import Key
from textual.screen import ModalScreen, Screen
from textual.containers import Vertical, Center, Middle, VerticalScroll

LOGO = r"""
       _      ____    _   _   ___   _   _    ___       _____   _   _   ___ 
      / \    |  _ \  | | | | |_ _| | \ | |  / _ \     |_   _| | | | | |_ _|
     / _ \   | |_) | | | | |  | |  |  \| | | | | |      | |   | | | |  | | 
    / ___ \  |  _ <  | |_| |  | |  | |\  | | |_| |      | |   | |_| |  | | 
   /_/   \_\ |_| \_\  \___/  |___| |_| \_|  \___/       |_|    \___/  |___|
                                                                         
                                                                              
"""

class ManualBoardDialog(ModalScreen):
    def __init__(self, port: str):
        super().__init__()
        self.port = port

    def compose(self) -> ComposeResult:
        with Vertical(id="manual-board-dialog"):
            yield Static(f"Unknown board on [b]{self.port}[/b]", id="manual-title")
            yield Static("Enter the FQBN manually (e.g., arduino:avr:nano, arduino:avr:uno)", id="manual-desc")
            yield Input(placeholder="arduino:avr:uno", id="fqbn-input")
            yield Static("Press Enter to save, or ESC to cancel.", id="manual-hint")

    def on_input_submitted(self, event: Input.Submitted):
        fqbn = event.value.strip()
        if fqbn:
            self.app.selected_fqbn = fqbn
            self.app.selected_port = self.port
            self.app.selected_board_name = f"Manual ({fqbn})"
            self.app.notify(f"Configured {self.port} as {fqbn}", title="Board Configured", timeout=3)
            self.dismiss()

    def on_key(self, event: Key):
        if event.key == "escape":
            self.dismiss()

class BoardListScreen(Screen):
    CSS = """
    .board-container {
        padding: 2 4;
        height: 100%;
    }
    OptionList {
        background: #24283b;
        border: round #7aa2f7;
        margin-top: 1;
        margin-bottom: 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(classes="board-container"):
            yield Static("[#ff9e64]=== Select a Connected Arduino Board ===[/]")
            yield OptionList(id="board-list")
            yield Static("[#7aa2f7]Enter[/] - Select Board  |  [#7aa2f7]ESC[/] - Go back")

    def on_mount(self) -> None:
        board_list = self.query_one("#board-list", OptionList)
        try:
            result = subprocess.run(["arduino-cli", "board", "list", "--format", "json"], capture_output=True, text=True, check=True)
            boards_data = json.loads(result.stdout)
            
            detected_ports = boards_data.get("detected_ports", [])
            
            if not detected_ports:
                board_list.add_option(Option("No boards found. Please check your USB connections.", disabled=True))
                return

            for index, board_info in enumerate(detected_ports):
                port = board_info.get("port", {}).get("address", "Unknown")
                matching = board_info.get("matching_boards", [])
                
                if matching:
                    name = matching[0].get("name", "Unknown Board")
                    fqbn = matching[0].get("fqbn", "unknown")
                    option_id = f"{fqbn}|{port}|{name}"
                    board_list.add_option(Option(f"✅ {name} ({port})", id=option_id))
                else:
                    board_list.add_option(Option(f"❓ Unknown Board on {port}", id=f"unknown|{port}|Unknown"))

        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            board_list.add_option(Option("❌ Failed to fetch boards. Is arduino-cli installed?", disabled=True))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        if event.option_id:
            fqbn, port, name = event.option_id.split("|")
            
            if fqbn != "unknown":
                self.app.selected_fqbn = fqbn
                self.app.selected_port = port
                self.app.selected_board_name = name
                self.app.notify(f"Selected: {name} on {port}", title="Board Configured", timeout=3)
                self.app.pop_screen()
            else:
                self.app.pop_screen()
                self.app.push_screen(ManualBoardDialog(port))

    def on_key(self, event: Key):
        if event.key == "escape":
            self.app.pop_screen()

class HelpScreen(Screen):
    CSS = """
    .help-container {
        padding: 2 4;
    }
    #tui-help {
        margin-bottom: 2;
    }
    #cli-help {
        color: #c0caf5;
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="help-container"):
            yield Static(
                "[#ff9e64]=== ArduinoTUI Hotkeys ===[/]\n\n"
                "[#7aa2f7]f[/] - Open Editor / Find file\n"
                "[#7aa2f7]l[/] - List all boards\n"
                "[#7aa2f7]v[/] - Show version / Check CLI install\n"
                "[#7aa2f7]h[/] - Show this help screen\n"
                "[#7aa2f7]:[/] - Open Command Palette\n"
                "[#7aa2f7]:q[/] - Quit app\n"
                "[#7aa2f7]:c[/] - Compile the code\n"
                "[#7aa2f7]:u[/] - Upload the code to board\n"
                "[#7aa2f7]:h[/] - Go to home screen\n"
                "[#7aa2f7]ESC[/] - Go back to the previous screen\n\n"
                "[#ff9e64]=== Arduino CLI Help (arduino-cli -h) ===[/]", 
                id="tui-help"
            )
            yield Static("Fetching Arduino CLI help...", id="cli-help")

    def on_mount(self) -> None:
        try:
            result = subprocess.run(["arduino-cli", "-h"], capture_output=True, text=True, check=True)
            self.query_one("#cli-help", Static).update(result.stdout)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.query_one("#cli-help", Static).update("❌ arduino-cli is not installed or not in PATH.")

    def on_key(self, event: Key):
        if event.key == "escape":
            self.app.pop_screen()

class VersionDialog(ModalScreen):
    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="version-dialog"):
            yield Static("Arduino CLI Status", id="version-title")
            yield Static(self.message, id="version-message")
            yield Static("Press any key to close...", id="version-hint")

    def on_key(self, event: Key):
        self.dismiss()

class CommandModeView(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Input(placeholder=":")

    def on_input_submitted(self, event: Input.Submitted):
        command_key: str = event.value.strip().lstrip(":")
        
        if command_key == "q":
            self.app.exit()
        elif command_key == "h":
            self.dismiss()
            self.app.switch_screen("home")
        elif command_key == "c":
            self.dismiss()
            self.app.switch_screen("editor")
            self.app.run_arduino_command("compile")
        elif command_key == "u":
            self.dismiss()
            self.app.switch_screen("editor")
            self.app.run_arduino_command("upload")
        elif command_key == "":
            self.dismiss()
        else:
            self.dismiss()
            self.app.notify(f"No commands found for ':{command_key}'", title="Warning", severity="warning", timeout=3)

class TerminalView(RichLog):
    pass

class FolderTree(DirectoryTree):
    pass

class CodeEditor(Static):
    def load_new_path(self, path):
        try:
            with open(path, "r") as code_file:
                code_content: str = code_file.read()
            if not code_content:
                code_content = "Selected file is empty"
            self.update(code_content)
        except FileNotFoundError:
            self.update("Selected file does not exist.")
        except UnicodeDecodeError:
            self.update("Selected file is not a text based file and can not be viewed")

class HomeScreen(Screen):
    CSS = """
    .logo {
        color: #7aa2f7;
        text-align: center;
        margin-bottom: 3;
        width: auto;
    }
    .menu-container {
        width: 35;
    }
    .menu-item {
        color: #c0caf5;
        width: 100%;
        padding-bottom: 1;
    }
    #status {
        dock: bottom;
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield Static(LOGO, classes="logo")
            with Center():
                with Vertical(classes="menu-container"):
                    yield Static("📁 Find file                 [#ff9e64]f[/]", classes="menu-item")
                    yield Static("📋 List all boards           [#ff9e64]l[/]", classes="menu-item")
                    yield Static("📌 Version                   [#ff9e64]v[/]", classes="menu-item")
                    yield Static("💡 Help                      [#ff9e64]h[/]", classes="menu-item")
        yield Static("⚡ [#7aa2f7]ArduinoTUI loaded 0 plugins in 12.5ms[/]", id="status")

    def on_key(self, event: Key):
        if event.character == "f":
            self.app.switch_screen("editor")
        elif event.character == "v":
            self.check_arduino_version()
        elif event.character == "h":
            self.app.push_screen("help")
        elif event.character == "l":
            self.app.push_screen("boards")

    def check_arduino_version(self):
        try:
            result = subprocess.run(["arduino-cli", "version"], capture_output=True, text=True, check=True)
            message = f"✅ {result.stdout.strip()}"
            self.app.push_screen(VersionDialog(message))
        except (subprocess.CalledProcessError, FileNotFoundError):
            message = "❌ arduino-cli is not installed or not in PATH.\n\nPlease install it via your package manager to enable compiling."
            self.app.push_screen(VersionDialog(message))

class EditorScreen(Screen):
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

    def compose(self) -> ComposeResult:
        yield CodeEditor("Select a file to view code") 
        yield FolderTree("./")
        # Added an explicit ID so the worker thread can easily find it
        yield TerminalView(id="main-terminal")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        editor_widgets: CodeEditor = self.query_one(CodeEditor)
        editor_widgets.load_new_path(event.path)
        self.app.current_sketch_dir = str(event.path.parent)

class ArduinoTUI(App):
    CSS = """
    Screen {
        background: #1a1b26; 
    }
    CommandModeView {
        align: center middle; 
    }
    CommandModeView Input {
        width: 50%;
        border: round #4FC7FF;
    }
    VersionDialog, ManualBoardDialog {
        align: center middle;
    }
    #version-dialog, #manual-board-dialog {
        width: 60;
        height: auto;
        background: #24283b;
        border: round #7aa2f7;
        padding: 1 2;
    }
    #version-title, #manual-title {
        text-align: center;
        text-style: bold;
        color: #ff9e64;
        margin-bottom: 1;
    }
    #version-message, #manual-desc {
        text-align: center;
        margin-bottom: 1;
    }
    #version-hint, #manual-hint {
        text-align: center;
        color: #565f89;
    }
    """

    SCREENS = {"home": HomeScreen, "editor": EditorScreen, "help": HelpScreen, "boards": BoardListScreen}
    
    selected_fqbn = None
    selected_port = None
    selected_board_name = None
    current_sketch_dir = None

    def on_mount(self) -> None:
        self.push_screen("home")

    def on_key(self, event: Key):
        if event.character == ":":
           self.push_screen(CommandModeView())

    def write_to_terminal(self, message: str):
        try:
            # Explicitly target the editor screen and the exact widget ID
            terminal = self.get_screen("editor").query_one("#main-terminal", TerminalView)
            terminal.write(message)
        except Exception as e:
            # Now it will notify you if it fails to find the terminal!
            self.notify(f"Terminal error: {e}", severity="error")

    @work(thread=True)
    def run_arduino_command(self, action: str):
        if not self.selected_fqbn:
            self.call_from_thread(self.notify, "⚠️ Please select a board first ('l').", title="Missing Board", severity="error")
            return
        if not self.current_sketch_dir:
            self.call_from_thread(self.notify, "⚠️ Please select a file from the file tree first.", title="Missing File", severity="error")
            return

        self.call_from_thread(self.notify, f"Starting {action}...", title="Arduino-CLI")

        if action == "compile":
            cmd = ["arduino-cli", "compile", "--fqbn", self.selected_fqbn, self.current_sketch_dir]
            self.call_from_thread(self.write_to_terminal, f"[#ff9e64]🔨 Compiling sketch in {self.current_sketch_dir}...[/]")
        elif action == "upload":
            if not self.selected_port:
                self.call_from_thread(self.notify, "⚠️ Board port is missing.", severity="error")
                return
            cmd = ["arduino-cli", "upload", "-p", self.selected_port, "--fqbn", self.selected_fqbn, self.current_sketch_dir]
            self.call_from_thread(self.write_to_terminal, f"[#ff9e64]🚀 Uploading to {self.selected_port}...[/]")

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            for line in process.stdout:
                self.call_from_thread(self.write_to_terminal, line.rstrip())
            
            process.wait() 
            
            if process.returncode == 0:
                self.call_from_thread(self.write_to_terminal, f"[#7aa2f7]✅ {action.capitalize()} successful![/]\n")
            else:
                self.call_from_thread(self.write_to_terminal, f"[#F54927]❌ {action.capitalize()} failed with code {process.returncode}.[/]\n")
                
        except Exception as e:
            self.call_from_thread(self.write_to_terminal, f"[#F54927]❌ System Error: {e}[/]\n")
            self.call_from_thread(self.notify, f"System Error: {e}", severity="error")

if __name__ == "__main__":
    app: ArduinoTUI = ArduinoTUI()
    app.run()