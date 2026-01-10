#!/bin/bash
# Setup script for creating a virtual environment for tiktok-api using uv
# This isolates tiktok-api dependencies from your system Python packages

echo "🔧 Setting up virtual environment for tiktok-api using uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed or not in PATH"
    echo ""
    echo "Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  # Or visit: https://github.com/astral-sh/uv"
    exit 1
fi

echo "✅ Found uv: $(uv --version)"

# Create virtual environment using uv (creates .venv by default)
echo "📦 Creating virtual environment..."
uv venv

# Install TikTokApi package and dependencies using uv
echo "📥 Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt

echo "📥 Installing TikTokApi from PyPI..."
uv pip install TikTokApi

# Install playwright browsers
echo "🌐 Installing playwright browsers..."
uv run playwright install chromium

echo "✅ Virtual environment setup complete!"
echo ""
echo "The virtual environment is located at: .venv/"
echo ""
echo "To use the virtual environment:"
echo "  source .venv/bin/activate"
echo ""
echo "Or use uv run to execute commands in the venv:"
echo "  uv run python Scraper/tiktok_scraper.py ..."
echo ""
echo "To deactivate:"
echo "  deactivate"

