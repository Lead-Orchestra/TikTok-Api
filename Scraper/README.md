# TikTok Scraper

This directory contains the Python scraper script for extracting TikTok data.

## Script

- `tiktok_scraper.py` - Main scraper script with support for:
  - User profile and video scraping
  - Trending video scraping
  - Hashtag video scraping
  - Video details and comments scraping

## Automatic Token Extraction

The scraper includes an automatic token extraction script that extracts the `msToken` cookie from your browser:

```bash
# Extract msToken automatically (recommended)
cd submodules/tiktok-api
uv run python Scraper/extract_ms_token.py

# Or specify a browser
uv run python Scraper/extract_ms_token.py --browser firefox
```

**Note:** TikTok uses `msToken` (camelCase) as the cookie name. The script automatically checks for both `msToken` and `ms_token` variations for compatibility.

## Usage

See the main documentation at `docs/TIKTOK_SCRAPER.md` for detailed setup and usage instructions.

### Quick Start

```bash
# From the backend root directory
cd submodules/tiktok-api

# Set up virtual environment (if not already done)
uv venv
uv pip install -e .
uv run playwright install chromium

# Run the scraper
uv run python Scraper/tiktok_scraper.py --mode user --target therock --session ms_token.txt
```

## Command-Line Options

```
-m, --mode <mode>            Scraping mode: user, trending, hashtag, or video (required)
-t, --target <target>         Target: username (user), hashtag (hashtag), or video ID/URL (video)
-s, --session <file>          Path to file containing ms_token or ms_token value itself (required)
-f, --format <format>         Output format: json or csv (default: json)
-o, --output <file>           Output file path (optional, auto-generated if not provided)
-l, --limit <number>          Maximum number of items to scrape (videos/comments)
--comments                    Include comments when scraping video (video mode only)
--comment-limit <number>      Maximum number of comments to scrape (default: 30)
```

## Examples

```bash
# Scrape user videos
python Scraper/tiktok_scraper.py -m user -t therock -s ms_token.txt

# Scrape trending videos (limit 50)
python Scraper/tiktok_scraper.py -m trending -s ms_token.txt -l 50

# Scrape hashtag videos
python Scraper/tiktok_scraper.py -m hashtag -t funny -s ms_token.txt

# Scrape video with comments
python Scraper/tiktok_scraper.py -m video -t <video_id> -s ms_token.txt --comments --comment-limit 100
```

