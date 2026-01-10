#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok ms_token Extractor
Automatically extracts ms_token cookie from browser cookie databases
Supports Firefox, Chrome, and Edge browsers
"""

from argparse import ArgumentParser
from glob import glob
from os.path import expanduser, exists
from platform import system
from sqlite3 import OperationalError, connect
import sys

# Color output (simple ASCII for cross-platform compatibility)
GREEN = "[OK]"
RED = "[X]"
YELLOW = "[!]"
CYAN = "[*]"


def has_tiktok_cookies(cookiefile, is_firefox=True):
    """Check if a cookie file contains TikTok cookies (including msToken/ms_token)."""
    try:
        if is_firefox:
            conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
            try:
                # Try modern Firefox cookie schema first - check for msToken specifically
                result = conn.execute(
                    "SELECT COUNT(*) FROM moz_cookies WHERE (name='msToken' OR name='ms_token') AND (baseDomain='tiktok.com' OR baseDomain='.tiktok.com')"
                ).fetchone()
                if result and result[0] > 0:
                    return True
                # Fallback: check for any TikTok cookies
                result = conn.execute(
                    "SELECT COUNT(*) FROM moz_cookies WHERE baseDomain='tiktok.com' OR baseDomain='.tiktok.com'"
                ).fetchone()
                if result and result[0] > 0:
                    return True
            except OperationalError:
                # Fallback to host-based query
                result = conn.execute(
                    "SELECT COUNT(*) FROM moz_cookies WHERE (name='msToken' OR name='ms_token') AND host LIKE '%tiktok.com'"
                ).fetchone()
                if result and result[0] > 0:
                    return True
                result = conn.execute(
                    "SELECT COUNT(*) FROM moz_cookies WHERE host LIKE '%tiktok.com'"
                ).fetchone()
                if result and result[0] > 0:
                    return True
        else:
            # Chrome/Edge cookie schema
            conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
            result = conn.execute(
                "SELECT COUNT(*) FROM cookies WHERE (name='msToken' OR name='ms_token') AND host_key LIKE '%tiktok.com'"
            ).fetchone()
            if result and result[0] > 0:
                return True
            result = conn.execute(
                "SELECT COUNT(*) FROM cookies WHERE host_key LIKE '%tiktok.com'"
            ).fetchone()
            if result and result[0] > 0:
                return True
        conn.close()
    except Exception as e:
        # Silently fail - don't print warnings during discovery
        pass
    return False


def get_firefox_cookie_files():
    """Get Firefox cookie files, checking both regular Firefox and Firefox Developer Edition."""
    platform = system()
    
    # Define all possible Firefox profile locations
    if platform == "Windows":
        cookie_patterns = [
            "~/AppData/Roaming/Mozilla/Firefox/Profiles/*/cookies.sqlite",
            "~/AppData/Roaming/Mozilla/Firefox Developer Edition/Profiles/*/cookies.sqlite",
        ]
    elif platform == "Darwin":  # macOS
        cookie_patterns = [
            "~/Library/Application Support/Firefox/Profiles/*/cookies.sqlite",
            "~/Library/Application Support/Firefox Developer Edition/Profiles/*/cookies.sqlite",
        ]
    else:  # Linux
        cookie_patterns = [
            "~/.mozilla/firefox/*/cookies.sqlite",
            "~/.mozilla/firefox-developer-edition/*/cookies.sqlite",
        ]
    
    # Collect all cookie files from all locations
    all_cookiefiles = []
    for pattern in cookie_patterns:
        found_files = glob(expanduser(pattern))
        all_cookiefiles.extend(found_files)
    
    if not all_cookiefiles:
        return []
    
    # Prioritize cookie files that contain TikTok cookies
    prioritized = []
    others = []
    
    for cookiefile in all_cookiefiles:
        if has_tiktok_cookies(cookiefile, is_firefox=True):
            prioritized.append(cookiefile)
        else:
            others.append(cookiefile)
    
    return prioritized + others


def get_chrome_cookie_files():
    """Get Chrome cookie files from all profile directories."""
    platform = system()
    
    if platform == "Windows":
        base_paths = [
            "~/AppData/Local/Google/Chrome/User Data",
        ]
    elif platform == "Darwin":  # macOS
        base_paths = [
            "~/Library/Application Support/Google/Chrome",
        ]
    else:  # Linux
        base_paths = [
            "~/.config/google-chrome",
        ]
    
    cookie_files = []
    for base_path in base_paths:
        expanded_base = expanduser(base_path)
        if not exists(expanded_base):
            continue
        
        # Check Default profile first
        default_cookies = expanduser(f"{base_path}/Default/Cookies")
        if exists(default_cookies):
            cookie_files.append(default_cookies)
        
        # Check other profiles
        profile_pattern = expanduser(f"{base_path}/Profile */Cookies")
        cookie_files.extend(glob(profile_pattern))
        
        # Also check numbered profiles (Profile 1, Profile 2, etc.)
        numbered_pattern = expanduser(f"{base_path}/Profile [0-9]*/Cookies")
        cookie_files.extend(glob(numbered_pattern))
    
    # Prioritize files with TikTok cookies
    prioritized = []
    others = []
    
    for cookiefile in cookie_files:
        if exists(cookiefile) and has_tiktok_cookies(cookiefile, is_firefox=False):
            prioritized.append(cookiefile)
        elif exists(cookiefile):
            others.append(cookiefile)
    
    return prioritized + others


def get_edge_cookie_files():
    """Get Edge cookie files from all profile directories."""
    platform = system()
    
    if platform == "Windows":
        base_paths = [
            "~/AppData/Local/Microsoft/Edge/User Data",
        ]
    elif platform == "Darwin":  # macOS
        base_paths = [
            "~/Library/Application Support/Microsoft Edge",
        ]
    else:  # Linux
        base_paths = [
            "~/.config/microsoft-edge",
        ]
    
    cookie_files = []
    for base_path in base_paths:
        expanded_base = expanduser(base_path)
        if not exists(expanded_base):
            continue
        
        # Check Default profile first
        default_cookies = expanduser(f"{base_path}/Default/Cookies")
        if exists(default_cookies):
            cookie_files.append(default_cookies)
        
        # Check other profiles
        profile_pattern = expanduser(f"{base_path}/Profile */Cookies")
        cookie_files.extend(glob(profile_pattern))
        
        # Also check numbered profiles
        numbered_pattern = expanduser(f"{base_path}/Profile [0-9]*/Cookies")
        cookie_files.extend(glob(numbered_pattern))
    
    # Prioritize files with TikTok cookies
    prioritized = []
    others = []
    
    for cookiefile in cookie_files:
        if exists(cookiefile) and has_tiktok_cookies(cookiefile, is_firefox=False):
            prioritized.append(cookiefile)
        elif exists(cookiefile):
            others.append(cookiefile)
    
    return prioritized + others


def extract_ms_token_from_firefox(cookiefile):
    """Extract ms_token from Firefox cookie database.
    
    Note: TikTok uses 'msToken' (camelCase) not 'ms_token' (snake_case).
    """
    try:
        conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
        
        # Try multiple cookie name variations and query strategies
        # TikTok uses 'msToken' (camelCase) as the cookie name
        cookie_names = ['msToken', 'ms_token']  # Try both variations
        
        for cookie_name in cookie_names:
            queries = [
                # Try baseDomain first (modern Firefox schema)
                f"SELECT value FROM moz_cookies WHERE name='{cookie_name}' AND (baseDomain='tiktok.com' OR baseDomain='.tiktok.com')",
                # Fallback to host-based query
                f"SELECT value FROM moz_cookies WHERE name='{cookie_name}' AND (host='tiktok.com' OR host='.tiktok.com' OR host='www.tiktok.com' OR host LIKE '%.tiktok.com')",
                # Try with any TikTok domain
                f"SELECT value FROM moz_cookies WHERE name='{cookie_name}' AND host LIKE '%tiktok%'",
            ]
            
            for query in queries:
                try:
                    cursor = conn.execute(query)
                    result = cursor.fetchone()
                    if result and result[0]:
                        token_value = result[0]
                        if token_value and len(token_value.strip()) > 0:
                            conn.close()
                            return token_value.strip()
                except OperationalError:
                    continue
        
        conn.close()
        
        # Check if TikTok cookies exist at all (for better error message)
        try:
            conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
            try:
                check_cursor = conn.execute("SELECT COUNT(*) FROM moz_cookies WHERE host LIKE '%tiktok.com'")
            except OperationalError:
                check_cursor = conn.execute("SELECT COUNT(*) FROM moz_cookies WHERE host LIKE '%tiktok%'")
            tiktok_cookie_count = check_cursor.fetchone()[0]
            conn.close()
            
            if tiktok_cookie_count > 0:
                print(f"{YELLOW} Found {tiktok_cookie_count} TikTok cookies but no msToken/ms_token cookie")
                print(f"{YELLOW} Tip: Visit https://www.tiktok.com in Firefox and browse for a moment to generate the msToken cookie")
        except Exception:
            pass
            
    except Exception as e:
        print(f"{YELLOW} Warning: Could not extract from Firefox {cookiefile}: {e}")
    return None


def extract_ms_token_from_chrome_edge(cookiefile):
    """Extract ms_token from Chrome/Edge cookie database.
    
    Note: TikTok uses 'msToken' (camelCase) not 'ms_token' (snake_case).
    """
    try:
        # Try read-only access first
        conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
        
        # Try both cookie name variations: msToken (camelCase) and ms_token (snake_case)
        for cookie_name in ['msToken', 'ms_token']:
            queries = [
                f"SELECT value FROM cookies WHERE name='{cookie_name}' AND host_key LIKE '%tiktok.com'",
                f"SELECT value FROM cookies WHERE name='{cookie_name}' AND host_key LIKE '%.tiktok.com'",
                f"SELECT value FROM cookies WHERE name='{cookie_name}' AND host_key='www.tiktok.com'",
                f"SELECT value FROM cookies WHERE name='{cookie_name}' AND host_key LIKE '%tiktok%'",
            ]
            
            for query in queries:
                try:
                    cursor = conn.execute(query)
                    result = cursor.fetchone()
                    
                    if result and result[0]:
                        # Chrome/Edge may encrypt cookie values on Windows/macOS
                        # On Linux, values are usually plain text
                        cookie_value = result[0]
                        
                        # Check if value looks encrypted (starts with 'v10' or 'v11' for Chrome encryption)
                        # Or if it's a blob that needs decryption
                        if isinstance(cookie_value, bytes):
                            # Try to decode as UTF-8 (works on Linux and unencrypted cookies)
                            try:
                                decoded = cookie_value.decode('utf-8')
                                if decoded and decoded.strip() and not decoded.startswith('v1'):
                                    conn.close()
                                    return decoded.strip()
                            except UnicodeDecodeError:
                                pass
                            
                            # Value is encrypted, continue to next query/browser
                            print(f"{YELLOW} Warning: Cookie value appears encrypted in {cookiefile}")
                            print(f"{YELLOW} Tip: Close Chrome/Edge and try again, or use Firefox for automatic extraction")
                            continue
                        elif isinstance(cookie_value, str):
                            # Plain text value (Linux or unencrypted)
                            if cookie_value and cookie_value.strip() and not cookie_value.startswith('v1'):
                                conn.close()
                                return cookie_value.strip()
                except OperationalError:
                    continue
                except Exception:
                    continue
        
        conn.close()
            
    except OperationalError as e:
        if "database is locked" in str(e).lower():
            print(f"{YELLOW} Warning: {cookiefile} is locked (browser may be running)")
            print(f"{YELLOW} Tip: Close Chrome/Edge and try again, or use Firefox")
        else:
            print(f"{YELLOW} Warning: Could not read {cookiefile}: {e}")
    except Exception as e:
        print(f"{YELLOW} Warning: Could not extract from {cookiefile}: {e}")
    
    return None


def extract_ms_token(preferred_browser=None):
    """
    Extract ms_token from browser cookies.
    Tries browsers in order: Firefox (if preferred_browser is None or 'firefox'), then Chrome, then Edge.
    
    Args:
        preferred_browser: Optional browser preference ('firefox', 'chrome', 'edge')
    
    Returns:
        ms_token string if found, None otherwise
    """
    browsers_to_try = []
    
    if preferred_browser:
        preferred_browser = preferred_browser.lower()
        if preferred_browser == 'firefox':
            browsers_to_try = ['firefox']
        elif preferred_browser == 'chrome':
            browsers_to_try = ['chrome']
        elif preferred_browser == 'edge':
            browsers_to_try = ['edge']
    else:
        # Default order: Firefox first (no encryption), then Chrome, then Edge
        browsers_to_try = ['firefox', 'chrome', 'edge']
    
    for browser in browsers_to_try:
        print(f"{CYAN} Trying {browser.capitalize()}...")
        
        if browser == 'firefox':
            cookie_files = get_firefox_cookie_files()
            if not cookie_files:
                print(f"{YELLOW} No Firefox cookie files found")
                continue
            
            print(f"{CYAN} Found {len(cookie_files)} Firefox profile(s)")
            
            for cookiefile in cookie_files:
                print(f"{CYAN} Checking {cookiefile}...")
                ms_token = extract_ms_token_from_firefox(cookiefile)
                if ms_token:
                    print(f"{GREEN} Found ms_token in Firefox: {cookiefile}")
                    return ms_token
        
        elif browser == 'chrome':
            cookie_files = get_chrome_cookie_files()
            if not cookie_files:
                print(f"{YELLOW} No Chrome cookie files found")
                continue
            
            print(f"{CYAN} Found {len(cookie_files)} Chrome profile(s)")
            
            for cookiefile in cookie_files:
                print(f"{CYAN} Checking {cookiefile}...")
                ms_token = extract_ms_token_from_chrome_edge(cookiefile)
                if ms_token:
                    print(f"{GREEN} Found ms_token in Chrome: {cookiefile}")
                    return ms_token
        
        elif browser == 'edge':
            cookie_files = get_edge_cookie_files()
            if not cookie_files:
                print(f"{YELLOW} No Edge cookie files found")
                continue
            
            print(f"{CYAN} Found {len(cookie_files)} Edge profile(s)")
            
            for cookiefile in cookie_files:
                print(f"{CYAN} Checking {cookiefile}...")
                ms_token = extract_ms_token_from_chrome_edge(cookiefile)
                if ms_token:
                    print(f"{GREEN} Found ms_token in Edge: {cookiefile}")
                    return ms_token
    
    return None


def save_ms_token(token, output_file):
    """Save ms_token to a file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(token.strip())
        print(f"{GREEN} ms_token saved to: {output_file}")
        return True
    except Exception as e:
        print(f"{RED} Error saving ms_token to {output_file}: {e}")
        return False


if __name__ == "__main__":
    parser = ArgumentParser(description='Extract TikTok ms_token from browser cookies')
    parser.add_argument(
        "-b", "--browser",
        choices=['firefox', 'chrome', 'edge'],
        help="Preferred browser to extract from (default: try all in order)"
    )
    parser.add_argument(
        "-o", "--output",
        default="ms_token.txt",
        help="Output file path (default: ms_token.txt)"
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Output ms_token to stdout instead of file"
    )
    args = parser.parse_args()
    
    try:
        print(f"{CYAN} Extracting ms_token from browser cookies...")
        ms_token = extract_ms_token(args.browser)
        
        if ms_token:
            if args.stdout:
                print(ms_token)
            else:
                save_ms_token(ms_token, args.output)
            sys.exit(0)
        else:
            print(f"{RED} Error: Could not find ms_token in any browser")
            print(f"{YELLOW} Make sure you are logged into TikTok in your browser")
            print(f"{YELLOW} If using Chrome/Edge, try closing the browser first")
            print(f"{YELLOW} Or use Firefox for easier automatic extraction")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n{YELLOW} Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"{RED} Error: {e}")
        sys.exit(1)

