# MCP Client

A modern client application for interacting with MCP servers and local LLM models using Ollama.

## Features

- Modern, dark-themed UI
- Local LLM integration with Ollama
- Automatic MCP server discovery
- Real-time chat interface
- Cross-platform support (Windows, macOS)

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running
- (For development) PyInstaller
- (For Windows installer) Inno Setup
- (For Mac installer) create-dmg

## Installation

### Windows

1. Download the `MCP_Client_Setup.exe` from the releases page
2. Double-click the installer
3. Follow the installation wizard
4. Launch the application from the Start menu or desktop shortcut

### macOS

1. Download the `MCP_Client.dmg` from the releases page
2. Double-click the DMG file
3. Drag the application to your Applications folder
4. Launch the application from your Applications folder

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mcp-client.git
cd mcp-client
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python Py_MCP_Client.py
```

## Building from Source

1. Install build dependencies:
```bash
pip install pyinstaller
```

2. For Windows, install Inno Setup
3. For macOS, install create-dmg:
```bash
brew install create-dmg
```

4. Run the build script:
```bash
python build.py
```

The installers will be created in the `installer` directory.

## Usage

1. Launch the application
2. Configure Ollama settings if needed (Settings button)
3. Select an LLM model from the dropdown
4. Use the "Discover Servers" button to find MCP servers
5. Start chatting with the selected LLM model

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 