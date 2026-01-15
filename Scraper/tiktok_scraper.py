#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Scraper
Scrapes TikTok data (users, trending, hashtags, videos) and saves to JSON/CSV
"""

import sys
import json
import csv
import argparse
import os
import asyncio
from pathlib import Path
from datetime import datetime

try:
    from TikTokApi import TikTokApi
except ImportError as e:
    print("[X] Error: Missing required package: TikTokApi")
    print("[+] Please install requirements: uv pip install -e .")
    sys.exit(1)

# Color output (simple ASCII for cross-platform compatibility)
GREEN = "[OK]"
RED = "[X]"
YELLOW = "[!]"
CYAN = "[*]"


async def scrape_user(username: str, ms_token: str, output_format: str = 'json', output_file: str = None, limit: int = None):
    """
    Scrape user profile and videos
    
    Args:
        username: TikTok username to scrape
        ms_token: TikTok ms_token for authentication
        output_format: Output format ('json' or 'csv')
        output_file: Output file path (optional)
        limit: Maximum number of videos to scrape
    """
    try:
        print(f"{CYAN} Initializing TikTok API...")
        async with TikTokApi() as api:
            print(f"{CYAN} Creating session with ms_token...")
            await api.create_sessions(
                ms_tokens=[ms_token],
                num_sessions=1,
                sleep_after=3,
                browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            )
            
            print(f"{CYAN} Loading user profile: @{username}...")
            user = api.user(username)
            user_data = await user.info()
            print(f"{GREEN} Profile loaded: {user_data.get('nickname', 'N/A')} (@{user_data.get('uniqueId', username)})")
            print(f"{CYAN} Followers: {user_data.get('followerCount', 'N/A')}")
            print(f"{CYAN} Following: {user_data.get('followingCount', 'N/A')}")
            print(f"{CYAN} Videos: {user_data.get('videoCount', 'N/A')}")
            
            # Scrape user videos
            print(f"{CYAN} Extracting videos...")
            videos = []
            video_count = 0
            
            async for video in user.videos(count=limit if limit else 1000):
                video_dict = video.as_dict
                videos.append(video_dict)
                video_count += 1
                
                if video_count % 10 == 0:
                    print(f"{CYAN} Extracted {video_count} videos so far...")
                if limit and video_count >= limit:
                    print(f"{CYAN} Reached limit of {limit} videos. Stopping extraction.")
                    break
            
            # Prepare output data
            output_data = {
                "user": user_data,
                "videos": videos,
                "extracted_at": datetime.now().isoformat(),
                "total_videos": len(videos)
            }
            
            # Save output
            if not output_file:
                output_file = f"tiktok_user_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
            
            if output_format == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
            else:  # CSV
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Write user info as header
                    writer.writerow(['Type', 'Field', 'Value'])
                    writer.writerow(['User', 'username', user_data.get('uniqueId', '')])
                    writer.writerow(['User', 'nickname', user_data.get('nickname', '')])
                    writer.writerow(['User', 'followers', user_data.get('followerCount', '')])
                    writer.writerow(['User', 'following', user_data.get('followingCount', '')])
                    writer.writerow(['User', 'videos', user_data.get('videoCount', '')])
                    writer.writerow([])  # Empty row
                    # Write videos
                    writer.writerow(['Video ID', 'Description', 'Likes', 'Shares', 'Comments', 'Views', 'Created'])
                    for video in videos:
                        writer.writerow([
                            video.get('id', ''),
                            video.get('desc', '')[:100],  # Truncate description
                            video.get('stats', {}).get('diggCount', ''),
                            video.get('stats', {}).get('shareCount', ''),
                            video.get('stats', {}).get('commentCount', ''),
                            video.get('stats', {}).get('playCount', ''),
                            video.get('createTime', '')
                        ])
            
            print(f"{GREEN} Data saved to: {output_file}")
            print(f"{GREEN} Total videos extracted: {len(videos)}")
            
    except Exception as e:
        print(f"{RED} Error scraping user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def scrape_trending(ms_token: str, output_format: str = 'json', output_file: str = None, limit: int = None):
    """
    Scrape trending videos
    
    Args:
        ms_token: TikTok ms_token for authentication
        output_format: Output format ('json' or 'csv')
        output_file: Output file path (optional)
        limit: Maximum number of videos to scrape
    """
    try:
        print(f"{CYAN} Initializing TikTok API...")
        async with TikTokApi() as api:
            print(f"{CYAN} Creating session with ms_token...")
            await api.create_sessions(
                ms_tokens=[ms_token],
                num_sessions=1,
                sleep_after=3,
                browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            )
            
            print(f"{CYAN} Extracting trending videos...")
            videos = []
            video_count = 0
            
            async for video in api.trending.videos(count=limit if limit else 100):
                video_dict = video.as_dict
                videos.append(video_dict)
                video_count += 1
                
                if video_count % 10 == 0:
                    print(f"{CYAN} Extracted {video_count} videos so far...")
                if limit and video_count >= limit:
                    print(f"{CYAN} Reached limit of {limit} videos. Stopping extraction.")
                    break
            
            # Prepare output data
            output_data = {
                "videos": videos,
                "extracted_at": datetime.now().isoformat(),
                "total_videos": len(videos)
            }
            
            # Save output
            if not output_file:
                output_file = f"tiktok_trending_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
            
            if output_format == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
            else:  # CSV
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Video ID', 'Author', 'Description', 'Likes', 'Shares', 'Comments', 'Views', 'Created'])
                    for video in videos:
                        writer.writerow([
                            video.get('id', ''),
                            video.get('author', {}).get('uniqueId', ''),
                            video.get('desc', '')[:100],
                            video.get('stats', {}).get('diggCount', ''),
                            video.get('stats', {}).get('shareCount', ''),
                            video.get('stats', {}).get('commentCount', ''),
                            video.get('stats', {}).get('playCount', ''),
                            video.get('createTime', '')
                        ])
            
            print(f"{GREEN} Data saved to: {output_file}")
            print(f"{GREEN} Total videos extracted: {len(videos)}")
            
    except Exception as e:
        print(f"{RED} Error scraping trending: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def scrape_hashtag(hashtag: str, ms_token: str, output_format: str = 'json', output_file: str = None, limit: int = None):
    """
    Scrape videos by hashtag
    
    Args:
        hashtag: Hashtag name (without #)
        ms_token: TikTok ms_token for authentication
        output_format: Output format ('json' or 'csv')
        output_file: Output file path (optional)
        limit: Maximum number of videos to scrape
    """
    try:
        print(f"{CYAN} Initializing TikTok API...")
        async with TikTokApi() as api:
            print(f"{CYAN} Creating session with ms_token...")
            await api.create_sessions(
                ms_tokens=[ms_token],
                num_sessions=1,
                sleep_after=3,
                browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            )
            
            print(f"{CYAN} Loading hashtag: #{hashtag}...")
            tag = api.hashtag(name=hashtag)
            
            print(f"{CYAN} Extracting videos...")
            videos = []
            video_count = 0
            
            async for video in tag.videos(count=limit if limit else 100):
                video_dict = video.as_dict
                videos.append(video_dict)
                video_count += 1
                
                if video_count % 10 == 0:
                    print(f"{CYAN} Extracted {video_count} videos so far...")
                if limit and video_count >= limit:
                    print(f"{CYAN} Reached limit of {limit} videos. Stopping extraction.")
                    break
            
            # Prepare output data
            output_data = {
                "hashtag": hashtag,
                "videos": videos,
                "extracted_at": datetime.now().isoformat(),
                "total_videos": len(videos)
            }
            
            # Save output
            if not output_file:
                output_file = f"tiktok_hashtag_{hashtag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
            
            if output_format == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
            else:  # CSV
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Video ID', 'Author', 'Description', 'Likes', 'Shares', 'Comments', 'Views', 'Created'])
                    for video in videos:
                        writer.writerow([
                            video.get('id', ''),
                            video.get('author', {}).get('uniqueId', ''),
                            video.get('desc', '')[:100],
                            video.get('stats', {}).get('diggCount', ''),
                            video.get('stats', {}).get('shareCount', ''),
                            video.get('stats', {}).get('commentCount', ''),
                            video.get('stats', {}).get('playCount', ''),
                            video.get('createTime', '')
                        ])
            
            print(f"{GREEN} Data saved to: {output_file}")
            print(f"{GREEN} Total videos extracted: {len(videos)}")
            
    except Exception as e:
        print(f"{RED} Error scraping hashtag: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def scrape_video(video_id: str, ms_token: str, output_format: str = 'json', output_file: str = None, include_comments: bool = False, comment_limit: int = 30):
    """
    Scrape video details and optionally comments
    
    Args:
        video_id: TikTok video ID or URL
        ms_token: TikTok ms_token for authentication
        output_format: Output format ('json' or 'csv')
        output_file: Output file path (optional)
        include_comments: Whether to scrape comments
        comment_limit: Maximum number of comments to scrape
    """
    try:
        print(f"{CYAN} Initializing TikTok API...")
        async with TikTokApi() as api:
            print(f"{CYAN} Creating session with ms_token...")
            await api.create_sessions(
                ms_tokens=[ms_token],
                num_sessions=1,
                sleep_after=3,
                browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            )
            
            print(f"{CYAN} Loading video: {video_id}...")
            # Extract video ID from URL if needed
            if 'tiktok.com' in video_id:
                # Try to extract ID from URL
                video = api.video(url=video_id)
            else:
                video = api.video(id=video_id)
            
            video_info = await video.info()
            print(f"{GREEN} Video loaded: {video_info.get('desc', 'N/A')[:50]}...")
            
            # Get comments if requested
            comments = []
            if include_comments:
                print(f"{CYAN} Extracting comments...")
                comment_count = 0
                async for comment in video.comments(count=comment_limit):
                    comments.append(comment.as_dict)
                    comment_count += 1
                    if comment_count % 10 == 0:
                        print(f"{CYAN} Extracted {comment_count} comments so far...")
                print(f"{GREEN} Total comments extracted: {len(comments)}")
            
            # Prepare output data
            output_data = {
                "video": video_info,
                "extracted_at": datetime.now().isoformat()
            }
            if include_comments:
                output_data["comments"] = comments
                output_data["total_comments"] = len(comments)
            
            # Save output
            if not output_file:
                output_file = f"tiktok_video_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
            
            if output_format == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
            else:  # CSV
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Write video info
                    writer.writerow(['Type', 'Field', 'Value'])
                    writer.writerow(['Video', 'id', video_info.get('id', '')])
                    writer.writerow(['Video', 'description', video_info.get('desc', '')])
                    writer.writerow(['Video', 'author', video_info.get('author', {}).get('uniqueId', '')])
                    writer.writerow(['Video', 'likes', video_info.get('stats', {}).get('diggCount', '')])
                    writer.writerow(['Video', 'shares', video_info.get('stats', {}).get('shareCount', '')])
                    writer.writerow(['Video', 'comments', video_info.get('stats', {}).get('commentCount', '')])
                    writer.writerow(['Video', 'views', video_info.get('stats', {}).get('playCount', '')])
                    if include_comments and comments:
                        writer.writerow([])  # Empty row
                        writer.writerow(['Comment ID', 'Author', 'Text', 'Likes', 'Created'])
                        for comment in comments:
                            writer.writerow([
                                comment.get('id', ''),
                                comment.get('user', {}).get('uniqueId', ''),
                                comment.get('text', '')[:100],
                                comment.get('diggCount', ''),
                                comment.get('createTime', '')
                            ])
            
            print(f"{GREEN} Data saved to: {output_file}")
            
    except Exception as e:
        print(f"{RED} Error scraping video: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='TikTok Scraper - Extract data from TikTok')
    parser.add_argument('-m', '--mode', choices=['user', 'trending', 'hashtag', 'video'], required=True,
                        help='Scraping mode: user, trending, hashtag, or video')
    parser.add_argument('-t', '--target', required=True,
                        help='Target: username (for user), hashtag name (for hashtag), or video ID/URL (for video). Ignored for trending.')
    parser.add_argument('-s', '--session', required=True,
                        help='Path to file containing ms_token (or ms_token value itself)')
    parser.add_argument('-f', '--format', choices=['json', 'csv'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('-o', '--output', help='Output file path (optional, auto-generated if not provided)')
    parser.add_argument('-l', '--limit', type=int, help='Maximum number of items to scrape (videos/comments)')
    parser.add_argument('--comments', action='store_true', help='Include comments when scraping video (video mode only)')
    parser.add_argument('--comment-limit', type=int, default=30, help='Maximum number of comments to scrape (default: 30)')
    
    args = parser.parse_args()
    
    # Read ms_token from file or use directly
    ms_token = args.session
    if os.path.exists(args.session):
        with open(args.session, 'r') as f:
            ms_token = f.read().strip()
    
    # Run appropriate scraper function
    if args.mode == 'user':
        asyncio.run(scrape_user(args.target, ms_token, args.format, args.output, args.limit))
    elif args.mode == 'trending':
        asyncio.run(scrape_trending(ms_token, args.format, args.output, args.limit))
    elif args.mode == 'hashtag':
        asyncio.run(scrape_hashtag(args.target, ms_token, args.format, args.output, args.limit))
    elif args.mode == 'video':
        asyncio.run(scrape_video(args.target, ms_token, args.format, args.output, args.comments, args.comment_limit if args.comments else None))


if __name__ == '__main__':
    main()


