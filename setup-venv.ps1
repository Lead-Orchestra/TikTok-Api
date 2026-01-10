# PowerShell script for setting up virtual environment on Windows using uv
# This isolates tiktok-api dependencies from your system Python packages

Write-Host "🔧 Setting up virtual environment for tiktok-api using uv..." -ForegroundColor Cyan

# Check if uv is installed
try {
    $uvVersion = uv --version 2>&1
    Write-Host "✅ Found uv: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: uv is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install uv first:" -ForegroundColor Yellow
    Write-Host "  powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`""
    Write-Host "  # Or visit: https://github.com/astral-sh/uv"
    exit 1
}

# Create virtual environment using uv (creates .venv by default)
Write-Host "📦 Creating virtual environment..." -ForegroundColor Cyan
uv venv

# Install TikTokApi package and dependencies using uv
Write-Host "📥 Installing dependencies from requirements.txt..." -ForegroundColor Cyan
uv pip install -r requirements.txt

Write-Host "📥 Installing TikTokApi from PyPI..." -ForegroundColor Cyan
uv pip install TikTokApi

# Install playwright browsers
Write-Host "🌐 Installing playwright browsers..." -ForegroundColor Cyan
uv run playwright install chromium

Write-Host "✅ Virtual environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "The virtual environment is located at: .venv\" -ForegroundColor Yellow
Write-Host ""
Write-Host "To use the virtual environment:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Or use uv run to execute commands in the venv:" -ForegroundColor Yellow
Write-Host "  uv run python Scraper/tiktok_scraper.py ..."
Write-Host ""
Write-Host "To deactivate:" -ForegroundColor Yellow
Write-Host "  deactivate"

