# Folder Tree Exporter

A Python command-line tool to export directory structures as ASCII trees to clipboard or file.

## Installation

# macOS/Linux

curl -L https://github.com/armandParser/folder-tree-exporter/releases/latest/download/tree-export-macos -o tree-export
chmod +x tree-export
sudo mv tree-export /usr/local/bin/

# Windows 

- Option 1: Powershell

Invoke-WebRequest -Uri "https://github.com/armandParser/folder-tree-exporter/releases/latest/download/tree-export-windows.exe" -OutFile "tree-export.exe"

- Option 2: Command Prompt

Download using curl (available in Windows 10+)
curl -L https://github.com/armandParser/folder-tree-exporter/releases/latest/download/tree-export-windows.exe -o tree-export.exe

Optional: Move to PATH directory (requires admin)
move tree-export.exe C:\Windows\System32\

- Option 3: Manual

Download: https://github.com/armandParser/folder-tree-exporter/releases/latest/download/tree-export-windows.exe
Rename to tree-export.exe

Either:
Run from current directory: .\tree-export.exe C:\path\to\folder
Add to PATH for system-wide access

## Usage

After installation, you can use the `tree-export` command:

```bash
# Copy folder structure to clipboard
tree-export /path/to/folder

# Save to file
tree-export /path/to/folder -f structure.txt

# Limit depth and show hidden files
tree-export /path/to/folder -d 3 -a

# Print to terminal
tree-export /path/to/folder --print
```

## Example Output

```
my-project/
├── src/
│   ├── components/
│   │   ├── Header.js
│   │   └── Footer.js
│   └── utils/
│       └── helpers.js
├── docs/
│   └── README.md
└── package.json
```

## Options

- `-f, --file`: Output to file instead of clipboard
- `-d, --depth`: Maximum depth to traverse
- `-a, --all`: Include hidden files and directories
- `-p, --print`: Print to stdout instead of clipboard