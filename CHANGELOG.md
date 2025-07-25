# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-07-25

### 🚀 Performance Improvements
- **Major performance optimization**: ~75% faster execution on average
- Replaced recursive directory traversal with iterative approach using deque
- Optimized file system operations using `os.scandir()` instead of `pathlib.iterdir()`
- Introduced lightweight `TreeNode` class with `__slots__` for memory efficiency
- Single-pass filtering and sorting reduces iterations through file lists

### 📊 Benchmark Results
- Small directories (50 files): **69.7% faster**
- Medium directories (500 files): **78.4% faster**  
- Large directories (2000 files): **82.6% faster**
- Wide directories (1000 files): **68.6% faster**
- Deep directories: **73.7% faster**

### 🔧 Technical Changes
- Iterative tree-to-lines conversion eliminates recursion overhead
- Better scalability for large directory structures
- Maintained identical functionality and output format
- No memory overhead despite significant speed improvements

## [0.1.0] - 2025-07-25

### ✨ Initial Release
- Export directory structures as ASCII trees
- Copy to clipboard by default (using pyperclip)
- Save to file with `-f` option
- Print to stdout with `-p` option
- Depth limiting with `-d` option
- Include hidden files with `-a` option
- Cross-platform support (Windows, macOS, Linux)
- Proper error handling for permissions and invalid paths