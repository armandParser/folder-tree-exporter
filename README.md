# Folder Tree Exporter

A Python command-line tool to export directory structures as ASCII trees to clipboard or file.

## Installation

```bash
# Clone/create project
rye init folder-tree-exporter
cd folder-tree-exporter

# Install dependencies
rye sync
```

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

## Development

```bash
# Install in development mode
rye sync

# Run directly
rye run tree-export /path/to/folder
```# folder-tree-exporter

Describe your project here.






# Download and make executable
curl -L https://github.com/yourusername/tree-export/releases/latest/download/tree-export-macos -o tree-export
chmod +x tree-export

# Optional: Install system-wide
sudo mv tree-export /usr/local/bin/