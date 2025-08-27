# 🗂️ Zipor - ZIP Archive File Manager

A powerful Python tool for creating, viewing, editing files and symbolic links inside ZIP archives without extracting them.

## ✨ Features

- **📄 File Management**: Create, view, and edit files directly inside ZIP archives
- **🔗 Symbolic Links**: Create and manage symbolic links within ZIP files
- **📁 Directory Listing**: Browse ZIP contents with file types and sizes
- **⚡ Interactive Mode**: User-friendly interactive interface for ZIP management
- **🛠️ Command Line**: Full CLI support with extensive options
- **✏️ External Editors**: Edit files using your preferred text editor (vim, nano, code, etc.)
- **🔄 Safe Operations**: Temporary file handling prevents corruption

## 🚀 Installation

### Prerequisites

- Python 3.6 or higher
- Standard Python libraries (zipfile, os, argparse, tempfile, subprocess, pathlib)

### Quick Install

1. Clone or download the repository:
```bash
git clone <repository-url>
cd zipor
```

## 📖 Usage

### Interactive Mode (Recommended for beginners)

```bash
python3 app.py --interactive
```

This launches a user-friendly menu system where you can:
- Browse ZIP contents
- Create new files
- View existing files
- Edit files with external editors
- Create symbolic links

### Command Line Interface

#### Create a New File
```bash
# Create file with inline content
python3 app.py archive.zip docs/readme.md "# My Project\nThis is a readme file"

# Create file from external file
python3 app.py archive.zip config/settings.json --file settings.json

# Overwrite existing files
python3 app.py archive.zip docs/readme.md "New content" --overwrite
```

#### View Files
```bash
# View file contents
python3 app.py archive.zip docs/readme.md --view

# List all ZIP contents
python3 app.py archive.zip --list
```

#### Edit Files
```bash
# Edit with external editor (vim, nano, code, etc.)
python3 app.py archive.zip config/settings.json --edit

# Edit with inline mode
python3 app.py archive.zip config/settings.json --edit --inline
```

#### Create Symbolic Links
```bash
# Create symlink to system file
python3 app.py archive.zip media/passwd_link --symlink /etc/passwd

# Create relative symlink
python3 app.py archive.zip config/settings_link --symlink ../settings.json
```

## 🎯 Use Cases

### Development & Deployment
- Modify configuration files in deployment archives
- Add missing files to existing ZIP packages
- Create shortcuts and links within archive structures

### System Administration
- Patch ZIP-based applications without full extraction
- Add configuration overrides to packaged applications
- Create symbolic links for path redirection

### Archive Management
- Organize files within ZIP archives
- Add documentation to existing packages
- Create structured directory layouts

## 🛡️ Safety Features

- **Backup Creation**: Original ZIP files are preserved during operations
- **Validation**: Checks for valid ZIP format before modifications
- **Error Handling**: Comprehensive error reporting and recovery
- **Overwrite Protection**: Prevents accidental file replacement without explicit permission

## 📋 Command Reference

### Main Commands
| Command | Description |
|---------|-------------|
| `python3 app.py <zip> <path> <content>` | Create file with content |
| `python3 app.py <zip> <path> --view` | View file contents |
| `python3 app.py <zip> <path> --edit` | Edit file |
| `python3 app.py <zip> --list` | List ZIP contents |
| `python3 app.py --interactive` | Launch interactive mode |

### Options
| Option | Description |
|--------|-------------|
| `--file, -f` | Read content from external file |
| `--overwrite` | Overwrite existing files |
| `--symlink, -s` | Create symbolic link |
| `--inline` | Use inline editing mode |
| `--list, -l` | List ZIP contents |
| `--interactive, -i` | Interactive mode |

## 🔧 Examples

### Basic File Operations
```bash
# Create a configuration file
python3 app.py app.zip config/app.conf "debug=true\nport=8080"

# Add documentation
python3 app.py package.zip docs/API.md --file API.md

# View log file
python3 app.py backup.zip logs/application.log --view
```

### Advanced Operations
```bash
# Create symbolic link for configuration
python3 app.py deploy.zip config/current --symlink /etc/myapp/config

# Edit with specific options
python3 app.py archive.zip src/main.py --edit --inline

# List contents with details
python3 app.py large-archive.zip --list
```

## 🐛 Troubleshooting

### Common Issues

**"No suitable text editor found"**
- Install a text editor: `sudo apt install nano` or `brew install nano`
- Set EDITOR environment variable: `export EDITOR=nano`

**"Not a valid ZIP file"**
- Verify the file is a proper ZIP archive
- Check file permissions and corruption

**"File already exists"**
- Use `--overwrite` flag to replace existing files
- Check exact file path in ZIP structure

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is open source. Please check the license file for details.

## 🔍 Technical Details

- **Python Version**: 3.6+
- **Dependencies**: Standard library only
- **Platform**: Cross-platform (Linux, macOS, Windows)
- **ZIP Standard**: Full ZIP format support including symbolic links
- **File Encoding**: UTF-8 with fallback handling

---

**Made with ❤️ for efficient ZIP archive management**
