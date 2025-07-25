#!/bin/bash
# benchmark.sh - Easy benchmark runner

set -e

echo "🚀 Setting up Tree Export Benchmark..."

# Check if we're in a Rye project
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this from your Rye project directory"
    exit 1
fi

# Install psutil for memory monitoring
echo "📦 Installing benchmark dependencies..."
rye add --dev psutil

# Run the benchmark
echo "🏃 Running benchmark suite..."
python3 benchmark.py

echo "✅ Benchmark complete!"
echo ""
echo "💡 Tips:"
echo "  - Run multiple times for more accurate results"
echo "  - Close other applications to reduce noise"
echo "  - Try different directory structures with real data"