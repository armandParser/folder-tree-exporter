"""
folder_tree_exporter/cli.py - Optimized version
Main CLI module for the folder tree exporter with performance optimizations
"""

import os
import sys
import argparse
from pathlib import Path
from collections import deque
from typing import List, Optional

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

class TreeNode:
    """Lightweight node for building tree structure"""
    __slots__ = ['name', 'is_dir', 'children', 'depth']
    
    def __init__(self, name: str, is_dir: bool, depth: int = 0):
        self.name = name
        self.is_dir = is_dir
        self.children = []
        self.depth = depth

def scan_directory_optimized(directory: Path, max_depth: Optional[int] = None, 
                           show_hidden: bool = False) -> TreeNode:
    """
    Optimized directory scanning using iterative approach with deque
    Avoids deep recursion and provides better memory usage for wide directories
    """
    root = TreeNode(directory.name, True, 0)
    
    # Use deque for BFS-like traversal (better for wide directories)
    queue = deque([(directory, root, 0)])
    
    while queue:
        current_path, current_node, current_depth = queue.popleft()
        
        if max_depth is not None and current_depth >= max_depth:
            continue
            
        try:
            # Get directory entries efficiently
            with os.scandir(current_path) as entries:
                # Filter and sort in one pass
                items = []
                for entry in entries:
                    if not show_hidden and entry.name.startswith('.'):
                        continue
                    items.append((entry.name, entry.is_dir()))
                
                # Sort: directories first, then files, both alphabetically
                items.sort(key=lambda x: (not x[1], x[0].lower()))
                
                # Create nodes and add to queue
                for name, is_dir in items:
                    node = TreeNode(name, is_dir, current_depth + 1)
                    current_node.children.append(node)
                    
                    if is_dir:
                        queue.append((current_path / name, node, current_depth + 1))
                        
        except (PermissionError, OSError):
            # Add permission denied node
            error_node = TreeNode("[Permission Denied]", False, current_depth + 1)
            current_node.children.append(error_node)
    
    return root

def tree_to_lines_optimized(root: TreeNode) -> List[str]:
    """
    Convert tree structure to lines using iterative approach
    More memory efficient than recursive approach
    """
    if not root.children:
        return []
    
    lines = []
    # Stack contains (node, prefix, is_last)
    stack = []
    
    # Initialize stack with root children in reverse order (for correct processing)
    for i, child in enumerate(reversed(root.children)):
        is_last = i == 0  # Last child (since we reversed)
        stack.append((child, "", is_last))
    
    while stack:
        node, parent_prefix, is_last = stack.pop()
        
        # Choose the appropriate tree characters
        if is_last:
            current_prefix = "└── "
            child_prefix = parent_prefix + "    "
        else:
            current_prefix = "├── "
            child_prefix = parent_prefix + "│   "
        
        # Add current item
        item_name = node.name
        if node.is_dir and not item_name.startswith('['):
            item_name += "/"
        
        lines.append(parent_prefix + current_prefix + item_name)
        
        # Add children to stack (in reverse order for correct processing)
        if node.children:
            for i, child in enumerate(reversed(node.children)):
                is_child_last = i == 0  # Last child (since we reversed)
                stack.append((child, child_prefix, is_child_last))
    
    return lines

def generate_tree(directory, max_depth=None, show_hidden=False, current_depth=0):
    """
    Fast tree generation with algorithm optimizations
    Note: current_depth parameter kept for compatibility but not used
    """
    path = Path(directory)
    
    if not path.exists():
        return [f"Error: Directory '{directory}' does not exist"]
    
    if not path.is_dir():
        return [f"Error: '{directory}' is not a directory"]
    
    try:
        root = scan_directory_optimized(path, max_depth, show_hidden)
        return tree_to_lines_optimized(root)
        
    except Exception as e:
        return [f"Error scanning directory: {e}"]

def format_output(directory, tree_lines):
    """Format the complete output with header"""
    path = Path(directory).resolve()
    output = [f"{path.name}/"]
    output.extend(tree_lines)
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(
        description="Export directory structure as ASCII tree (Optimized version)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tree-export /path/to/folder                    # Copy to clipboard
  tree-export /path/to/folder -f output.txt     # Save to file
  tree-export /path/to/folder -d 2              # Limit depth to 2 levels
  tree-export /path/to/folder -a                # Include hidden files
        """
    )
    
    parser.add_argument(
        'directory',
        help='Directory to export'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Output file (default: copy to clipboard)'
    )
    
    parser.add_argument(
        '-d', '--depth',
        type=int,
        help='Maximum depth to traverse'
    )
    
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='Include hidden files and directories'
    )
    
    parser.add_argument(
        '-p', '--print',
        action='store_true',
        help='Print to stdout instead of clipboard'
    )
    
    args = parser.parse_args()
    
    # Validate directory
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory", file=sys.stderr)
        sys.exit(1)
    
    # Generate tree
    print("Generating folder structure...", file=sys.stderr)
    tree_lines = generate_tree(
        args.directory,
        max_depth=args.depth,
        show_hidden=args.all
    )
    
    # Format output
    output = format_output(args.directory, tree_lines)
    
    # Handle output
    if args.file:
        # Write to file
        try:
            with open(args.file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Tree structure saved to '{args.file}'", file=sys.stderr)
        except Exception as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.print:
        # Print to stdout
        print(output)
    
    else:
        # Copy to clipboard
        if not CLIPBOARD_AVAILABLE:
            print("Error: pyperclip not installed. Use --print or --file instead.", file=sys.stderr)
            print("Install with: rye add pyperclip", file=sys.stderr)
            sys.exit(1)
        
        try:
            pyperclip.copy(output)
            lines_count = len(tree_lines)
            print(f"Tree structure copied to clipboard! ({lines_count} items)", file=sys.stderr)
        except Exception as e:
            print(f"Error copying to clipboard: {e}", file=sys.stderr)
            print("Falling back to print:")
            print(output)

if __name__ == "__main__":
    main()