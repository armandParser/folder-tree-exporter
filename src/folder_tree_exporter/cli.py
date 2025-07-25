"""
folder_tree_exporter/cli.py
Main CLI module for the folder tree exporter
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

def generate_tree(directory, max_depth=None, show_hidden=False, current_depth=0):
    """
    Generate ASCII tree representation of directory structure
    """
    if max_depth is not None and current_depth > max_depth:
        return []
    
    lines = []
    path = Path(directory)
    
    if not path.exists():
        return [f"Error: Directory '{directory}' does not exist"]
    
    if not path.is_dir():
        return [f"Error: '{directory}' is not a directory"]
    
    try:
        # Get all items in directory
        items = list(path.iterdir())
        
        # Filter hidden files if requested
        if not show_hidden:
            items = [item for item in items if not item.name.startswith('.')]
        
        # Sort: directories first, then files, both alphabetically
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            
            # Choose the appropriate tree characters
            if is_last:
                prefix = "└── "
                child_prefix = "    "
            else:
                prefix = "├── "
                child_prefix = "│   "
            
            # Add current item
            item_name = item.name
            if item.is_dir():
                item_name += "/"
            
            lines.append(prefix + item_name)
            
            # Recursively add subdirectories
            if item.is_dir():
                sub_lines = generate_tree(
                    item, 
                    max_depth=max_depth, 
                    show_hidden=show_hidden,
                    current_depth=current_depth + 1
                )
                for sub_line in sub_lines:
                    lines.append(child_prefix + sub_line)
    
    except PermissionError:
        lines.append("├── [Permission Denied]")
    
    return lines

def format_output(directory, tree_lines):
    """Format the complete output with header"""
    path = Path(directory).resolve()
    output = [f"{path.name}/"]
    output.extend(tree_lines)
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(
        description="Export directory structure as ASCII tree",
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
