# 🚀 Notepad PRO


<img src="images/Notepad AI Sample Initial.png" alt="Alt text" width="400">


A **production-level**, AI-powered professional text editor that enhances your writing with intelligent features. Built with Python and wxPython, Notepad PRO integrates local AI models through Ollama to provide contextual writing assistance without sending your data to the cloud.

## ✨ Features

### 🎨 Modern Professional Interface
- **6 Professional Themes**: Light, Dark, Monokai, Solarized Dark, Nord, and Dracula
- **Real-time Status Bar**: Live word count, character count, line/column position, and AI status
- **Professional Splash Screen**: Branded startup with loading animation
- **Tabbed Interface**: Work with multiple documents simultaneously
- **Rich Text Editing**: Support for bold, italic, headers, and bullet points
- **Context Menus**: Quick access to common operations with right-click
- **Comprehensive Settings**: Tabbed settings dialog with appearance, editor, AI, and behavior options

### 🔍 Advanced Text Editor Features
- **Advanced Find & Replace**: Regex support, case sensitivity, whole word matching
- **Cursor Position Tracking**: Real-time line and column display
- **Session Persistence**: Automatically restore tabs on restart
- **Recent Files**: Quick access to recently opened documents
- **Keyboard Shortcuts**: Efficient workflow with hotkeys
- **Auto-save Prompts**: Never lose your work

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- Gemma 3:1b model (or modify `ai.py` to use another model)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AnuragRoque/AI-Notepad.git
   cd AI-Notepad
   ```

2. **Install dependencies**
   ```bash
   pip install wxPython ollama
   ```

3. **Install Ollama and pull the model**
   ```bash
   # Install Ollama from https://ollama.ai/
   # Then pull the model
   ollama pull gemma3:1b
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## 📖 Usage

### Basic Editing
- Create a new tab: `Ctrl+N`
- Open file: `Ctrl+O`
- Save: `Ctrl+S`
- Save As: `Ctrl+Shift+S`
- Close tab: `Ctrl+W`
- Find: `Ctrl+F`

### Tab Navigation
- Next tab: `Ctrl+Tab`
- Previous tab: `Ctrl+Shift+Tab`
- Right-click on tabs for more options

### AI Features
1. **Select text** (or use entire document if no selection)
2. Click the **✨ AI button** or right-click for AI options
3. Choose your desired operation:
   - **Write**: Continue your text
   - **Rewrite**: Improve clarity
   - **Summarise**: Create a brief summary
   - **Make shorter/longer**: Adjust length
   - **Change tone**: Adjust formality/style
   - **Change format**: Convert to different formats

### Formatting
- **Bold**: Select text and click `B`
- **Italic**: Select text and click `I`
- **Header**: Select text and click `H1`
- **Bullets**: Click `•` to add bullet points

### Keyboard Shortcuts
| Action | Shortcut |
|--------|----------|
| New Tab | `Ctrl+N` |
| Open File | `Ctrl+O` |
| Save | `Ctrl+S` |
| Save As | `Ctrl+Shift+S` |
| Close Tab | `Ctrl+W` |
| Find | `Ctrl+F` |
| AI Rewrite | `Ctrl+Shift+R` |
| Cut | `Ctrl+X` |
| Copy | `Ctrl+C` |
| Paste | `Ctrl+V` |
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Y` |
| Select All | `Ctrl+A` |

## 🏗️ Project Structure

```
08-AI-Notepad/
│
├── main.py              # Application entry point
├── ui.py                # Main UI and frame logic
├── ai.py                # AI integration with Ollama
├── settings.py          # Settings dialog
├── file_history.py      # Recent files management
├── tab_manager.py       # Tab session management
├── images/              # Application icons and screenshots
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🔌 AI Integration

AI Notepad uses [Ollama](https://ollama.ai/) to run local AI models. By default, it uses the Gemma 3:1b model, which provides a good balance between performance and quality.

### Changing the AI Model

Edit `ai.py` to use a different model:

```python
response = ollama.generate(
    model="your-model-name",  # Change this line
    prompt=prompt,
    stream=False,
    system="..."
)
```

Popular alternatives:
- `llama2:7b` - Meta's Llama 2
- `mistral:7b` - Mistral AI model
- `codellama:7b` - Code-focused model

## 🎨 Themes

Switch between light and dark themes through the settings (⚙ button):
- **Light Theme**: Clean, bright interface
- **Dark Theme**: Easy on the eyes for extended writing sessions

## 💾 Session Management

AI Notepad automatically saves your session:
- **Tab state**: All open tabs are restored on restart
- **Unsaved content**: Preserved even if files aren't saved
- **File paths**: Quick access to your documents

Session data is stored in:
- Windows: `%LOCALAPPDATA%\NotepadAI\`
- Linux/Mac: `~/.local/share/notepad-ai/`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with [wxPython](https://wxpython.org/)
- AI powered by [Ollama](https://ollama.ai/)
- Uses the [Gemma](https://ai.google.dev/gemma) model family
- Icons from various open source projects

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This application runs AI models locally on your machine. No data is sent to external servers, ensuring your privacy and security.