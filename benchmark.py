#!/usr/bin/env python3
"""
Benchmark suite for comparing original vs optimized tree export implementations
"""

import os
import time
import tempfile
import shutil
import random
import string
import sys
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

# Import both implementations
# Original implementation
def generate_tree_original(directory, max_depth=None, show_hidden=False, current_depth=0):
    """Original recursive implementation"""
    if max_depth is not None and current_depth > max_depth:
        return []
    
    lines = []
    path = Path(directory)
    
    if not path.exists():
        return [f"Error: Directory '{directory}' does not exist"]
    
    if not path.is_dir():
        return [f"Error: '{directory}' is not a directory"]
    
    try:
        items = list(path.iterdir())
        
        if not show_hidden:
            items = [item for item in items if not item.name.startswith('.')]
        
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            
            if is_last:
                prefix = "└── "
                child_prefix = "    "
            else:
                prefix = "├── "
                child_prefix = "│   "
            
            item_name = item.name
            if item.is_dir():
                item_name += "/"
            
            lines.append(prefix + item_name)
            
            if item.is_dir():
                sub_lines = generate_tree_original(
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

# Optimized implementation (simplified version for benchmark)
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

class TreeNode:
    __slots__ = ['name', 'is_dir', 'children', 'depth']
    
    def __init__(self, name: str, is_dir: bool, depth: int = 0):
        self.name = name
        self.is_dir = is_dir
        self.children = []
        self.depth = depth

def scan_directory_optimized(directory: Path, max_depth=None, show_hidden=False):
    root = TreeNode(directory.name, True, 0)
    queue = deque([(directory, root, 0)])
    
    while queue:
        current_path, current_node, current_depth = queue.popleft()
        
        if max_depth is not None and current_depth >= max_depth:
            continue
            
        try:
            with os.scandir(current_path) as entries:
                items = []
                for entry in entries:
                    if not show_hidden and entry.name.startswith('.'):
                        continue
                    items.append((entry.name, entry.is_dir()))
                
                items.sort(key=lambda x: (not x[1], x[0].lower()))
                
                for name, is_dir in items:
                    node = TreeNode(name, is_dir, current_depth + 1)
                    current_node.children.append(node)
                    
                    if is_dir:
                        queue.append((current_path / name, node, current_depth + 1))
                        
        except (PermissionError, OSError):
            error_node = TreeNode("[Permission Denied]", False, current_depth + 1)
            current_node.children.append(error_node)
    
    return root

def tree_to_lines_optimized(root: TreeNode) -> List[str]:
    if not root.children:
        return []
    
    lines = []
    stack = []
    
    for i, child in enumerate(reversed(root.children)):
        is_last = i == 0
        stack.append((child, "", is_last))
    
    while stack:
        node, parent_prefix, is_last = stack.pop()
        
        if is_last:
            current_prefix = "└── "
            child_prefix = parent_prefix + "    "
        else:
            current_prefix = "├── "
            child_prefix = parent_prefix + "│   "
        
        item_name = node.name
        if node.is_dir and not item_name.startswith('['):
            item_name += "/"
        
        lines.append(parent_prefix + current_prefix + item_name)
        
        if node.children:
            for i, child in enumerate(reversed(node.children)):
                is_child_last = i == 0
                stack.append((child, child_prefix, is_child_last))
    
    return lines

def generate_tree_optimized(directory, max_depth=None, show_hidden=False):
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

@dataclass
class BenchmarkResult:
    name: str
    execution_time: float
    memory_peak: float
    memory_average: float
    lines_generated: int
    files_processed: int
    success: bool
    error_message: str = ""

class MemoryMonitor:
    def __init__(self):
        self.peak_memory = 0
        self.memory_samples = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start(self):
        self.monitoring = True
        self.peak_memory = 0
        self.memory_samples = []
        self.monitor_thread = threading.Thread(target=self._monitor)
        self.monitor_thread.start()
    
    def stop(self):
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        return self.peak_memory, sum(self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0
    
    def _monitor(self):
        process = psutil.Process()
        while self.monitoring:
            try:
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.memory_samples.append(memory_mb)
                self.peak_memory = max(self.peak_memory, memory_mb)
                time.sleep(0.01)  # Sample every 10ms
            except:
                break

@contextmanager
def memory_monitor():
    monitor = MemoryMonitor()
    monitor.start()
    try:
        yield monitor
    finally:
        monitor.stop()

def create_test_directory(base_path: Path, structure: Dict) -> Tuple[int, int]:
    """
    Create test directory structure
    Returns (total_files, total_dirs)
    """
    total_files = 0
    total_dirs = 0
    
    for name, config in structure.items():
        if config['type'] == 'dir':
            dir_path = base_path / name
            dir_path.mkdir(exist_ok=True)
            total_dirs += 1
            
            # Create files in this directory
            for i in range(config.get('files', 0)):
                file_path = dir_path / f"file_{i:04d}.txt"
                file_path.write_text(f"Content of file {i}")
                total_files += 1
            
            # Create subdirectories recursively
            if 'subdirs' in config:
                sub_files, sub_dirs = create_test_directory(dir_path, config['subdirs'])
                total_files += sub_files
                total_dirs += sub_dirs
    
    return total_files, total_dirs

def run_benchmark(func, directory: Path, max_depth=None, show_hidden=False) -> BenchmarkResult:
    """Run a single benchmark test"""
    
    # Count files for reporting
    total_files = sum(1 for _ in directory.rglob('*') if _.is_file())
    
    monitor = MemoryMonitor()
    monitor.start()
    
    try:
        start_time = time.perf_counter()
        result = func(str(directory), max_depth=max_depth, show_hidden=show_hidden)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        success = True
        error_message = ""
        
    except Exception as e:
        execution_time = 0
        result = []
        success = False
        error_message = str(e)
    finally:
        peak_memory, avg_memory = monitor.stop()
    
    return BenchmarkResult(
        name=func.__name__,
        execution_time=execution_time,
        memory_peak=peak_memory,
        memory_average=avg_memory,
        lines_generated=len(result),
        files_processed=total_files,
        success=success,
        error_message=error_message
    )

def print_results(results: List[BenchmarkResult], test_name: str):
    """Print benchmark results in a nice format"""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: {test_name}")
    print(f"{'='*60}")
    
    if not results:
        print("No results to display")
        return
    
    # Table header
    print(f"{'Implementation':<20} {'Time (s)':<10} {'Peak RAM':<12} {'Lines':<8} {'Files':<8} {'Status':<10}")
    print("-" * 80)
    
    # Results
    for result in results:
        status = "✓ OK" if result.success else "✗ FAIL"
        print(f"{result.name:<20} {result.execution_time:<10.4f} {result.memory_peak:<12.1f}MB {result.lines_generated:<8} {result.files_processed:<8} {status}")
        
        if not result.success:
            print(f"    Error: {result.error_message}")
    
    # Performance comparison
    if len(results) == 2 and all(r.success for r in results):
        original, optimized = results[0], results[1]
        time_improvement = (original.execution_time - optimized.execution_time) / original.execution_time * 100
        memory_improvement = (original.memory_peak - optimized.memory_peak) / original.memory_peak * 100
        
        print(f"\nPERFORMANCE IMPROVEMENT:")
        print(f"  Time: {time_improvement:+.1f}% ({'faster' if time_improvement > 0 else 'slower'})")
        print(f"  Memory: {memory_improvement:+.1f}% ({'less' if memory_improvement > 0 else 'more'})")

def main():
    print("🚀 Tree Export Benchmark Suite")
    print("=" * 60)
    
    # Create temporary directory for tests
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Small Directory (50 files, 2 levels)",
                "structure": {
                    "src": {"type": "dir", "files": 20, "subdirs": {
                        "components": {"type": "dir", "files": 15},
                        "utils": {"type": "dir", "files": 15}
                    }},
                },
                "max_depth": None
            },
            {
                "name": "Medium Directory (500 files, 3 levels)",
                "structure": {
                    f"dir_{i}": {"type": "dir", "files": 25, "subdirs": {
                        f"subdir_{j}": {"type": "dir", "files": 20}
                        for j in range(5)
                    }}
                    for i in range(4)
                },
                "max_depth": None
            },
            {
                "name": "Large Directory (2000 files, 4 levels)",
                "structure": {
                    f"level1_{i}": {"type": "dir", "files": 10, "subdirs": {
                        f"level2_{j}": {"type": "dir", "files": 15, "subdirs": {
                            f"level3_{k}": {"type": "dir", "files": 25}
                            for k in range(3)
                        }}
                        for j in range(5)
                    }}
                    for i in range(3)
                },
                "max_depth": None
            },
            {
                "name": "Wide Directory (1000 files, 2 levels)",
                "structure": {
                    f"folder_{i:03d}": {"type": "dir", "files": 10}
                    for i in range(100)
                },
                "max_depth": None
            },
            {
                "name": "Deep Directory (100 files, 10 levels) - Depth Limited to 5",
                "structure": create_deep_structure(10, 10),
                "max_depth": 5
            }
        ]
        
        all_results = []
        
        for scenario in test_scenarios:
            print(f"\n🧪 Testing: {scenario['name']}")
            
            # Create test directory
            test_dir = temp_path / "test_scenario"
            if test_dir.exists():
                shutil.rmtree(test_dir)
            test_dir.mkdir()
            
            total_files, total_dirs = create_test_directory(test_dir, scenario['structure'])
            print(f"   Created: {total_files} files, {total_dirs} directories")
            
            # Run benchmarks
            results = []
            
            # Original implementation
            print("   Running original implementation...")
            result_orig = run_benchmark(
                generate_tree_original, 
                test_dir, 
                max_depth=scenario['max_depth']
            )
            results.append(result_orig)
            
            # Optimized implementation
            print("   Running optimized implementation...")
            result_opt = run_benchmark(
                generate_tree_optimized, 
                test_dir, 
                max_depth=scenario['max_depth']
            )
            results.append(result_opt)
            
            # Store results
            all_results.append((scenario['name'], results))
            
            # Print individual results
            print_results(results, scenario['name'])
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        
        improvements = []
        for test_name, results in all_results:
            if len(results) == 2 and all(r.success for r in results):
                original, optimized = results[0], results[1]
                time_improvement = (original.execution_time - optimized.execution_time) / original.execution_time * 100
                memory_improvement = (original.memory_peak - optimized.memory_peak) / original.memory_peak * 100
                improvements.append((test_name, time_improvement, memory_improvement))
        
        if improvements:
            print(f"{'Test Case':<40} {'Time Δ':<12} {'Memory Δ'}")
            print("-" * 65)
            for test_name, time_imp, mem_imp in improvements:
                print(f"{test_name:<40} {time_imp:+6.1f}%     {mem_imp:+6.1f}%")
            
            # Overall averages
            avg_time = sum(x[1] for x in improvements) / len(improvements)
            avg_memory = sum(x[2] for x in improvements) / len(improvements)
            print("-" * 65)
            print(f"{'AVERAGE':<40} {avg_time:+6.1f}%     {avg_memory:+6.1f}%")

def create_deep_structure(levels: int, files_per_level: int) -> Dict:
    """Create a deeply nested directory structure"""
    if levels <= 0:
        return {}
    
    return {
        f"level_{levels}": {
            "type": "dir",
            "files": files_per_level,
            "subdirs": create_deep_structure(levels - 1, files_per_level)
        }
    }

if __name__ == "__main__":
    # Check if psutil is available
    try:
        import psutil
    except ImportError:
        print("❌ psutil is required for memory monitoring")
        print("Install with: pip install psutil")
        sys.exit(1)
    
    main()