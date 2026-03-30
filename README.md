# ⚡ ArduinoTUI

A lightning-fast, terminal-based User Interface for Arduino development, heavily inspired by the aesthetics of LazyVim. Built with Python and Textual.

## ✨ Features
* **LazyVim Dashboard:** A clean, keyboard-centric home screen.
* **Live File Tree:** Navigate your sketch directories directly in the terminal.
* **Built-in Editor Viewer:** Instantly view `.ino` and `.cpp` files.
* **Board Management:** Detect and lets the user select Arduino board.
* **Real-time Compilation & Uploading:** Streams `arduino-cli` output directly into the TUI without freezing the app.
* **Vim-style Command Palette:** Use `:` to trigger actions seamlessly.

## 🛠️ Prerequisites
1. **Python 3.8+**
2. **[arduino-cli](https://arduino.github.io/arduino-cli/latest/)**: Must be installed and available in your system's PATH.

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Harinandan-K/ArduinoTUI.git
   cd ArduinoTUI
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python main.py
   ```

## ⌨️ Hotkeys
| Key | Action |
| :--- | :--- |
| `f` | Open Editor / Find file |
| `l` | List all connected boards |
| `v` | Show Arduino CLI version |
| `h` | Show Help screen |
| `:` | Open Command Palette |

### Command Palette Commands
* `:c` - Compile the current sketch
* `:u` - Upload the current sketch to the selected board
* `:h` - Return to the home screen
* `:q` - Quit the application




