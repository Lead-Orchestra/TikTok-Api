#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Scraper Mock/Test Version
Generates mock data for testing without hitting TikTok's API
Useful for development, testing, and when TikTok bot detection is blocking requests
"""

import sys
import json
import csv
import argparse
import os
from pathlib import Path
from datetime import datetime
import random
import time

# Color output (simple ASCII for cross-platform compatibility)
GREEN = "[OK]"
RED = "[X]"
YELLOW = "[!]"
CYAN = "[*]"


def generate_mock_user_data(username: str):
    """Generate mock user profile data."""
    return {
        "uniqueId": username,
        "nickname": f"{username.capitalize()} User",
        "followerCount": random.randint(1000, 50000000),
        "followingCount": random.randint(50, 5000),
        "videoCount": random.randint(10, 5000),
        "verified": random.choice([True, False]),
        "privateAccount": random.choice([True, False]),
        "bioDescription": f"Mock bio for {username}",
        "avatarLarger": f"https://example.com/avatars/{username}.jpg",
        "avatarMedium": f"https://example.com/avatars/{username}_medium.jpg",
        "avatarThumb": f"https://example.com/avatars/{username}_thumb.jpg",
    }


def generate_mock_video(index: int, username: str):
    """Generate mock video data."""
    video_id = random.randint(7000000000000000000, 7999999999999999999)
    return {
        "id": str(video_id),
        "desc": f"Mock video description {index + 1} - This is a test video for {username}",
        "createTime": int(datetime.now().timestamp()) - random.randint(0, 86400 * 365),  # Random time in last year
        "author": {
            "uniqueId": username,
            "nickname": f"{username.capitalize()} User",
        },
        "stats": {
            "diggCount": random.randint(100, 10000000),  # Likes
            "shareCount": random.randint(10, 1000000),   # Shares
            "commentCount": random.randint(5, 500000),   # Comments
            "playCount": random.randint(1000, 100000000),  # Views
        },
        "video": {
            "downloadAddr": f"https://example.com/videos/{video_id}.mp4",
            "cover": f"https://example.com/covers/{video_id}.jpg",
            "duration": random.randint(5, 60),
        },
        "music": {
            "title": f"Mock Music {index + 1}",
            "authorName": "Mock Artist",
        },
        "textExtra": [],
    }


def generate_mock_comment(index: int):
    """Generate mock comment data."""
    return {
        "id": str(random.randint(7000000000000000000, 7999999999999999999)),
        "text": f"Mock comment {index + 1} - This is a test comment",
        "createTime": int(datetime.now().timestamp()) - random.randint(0, 86400 * 30),  # Random time in last month
        "diggCount": random.randint(0, 10000),
        "user": {
            "uniqueId": f"user{random.randint(1, 1000)}",
            "nickname": f"Commenter {index + 1}",
        },
    }


def generate_mock_follower(index: int):
    """Generate mock follower data."""
    follower_id = random.randint(1000000000000000000, 9999999999999999999)
    usernames = [
        f"user{random.randint(1, 999)}", 
        f"creator{random.randint(1, 99)}",
        f"tiktoker{random.randint(1, 99)}",
        f"fan{random.randint(1, 99)}",
        f"viewer{random.randint(1, 99)}"
    ]
    username = random.choice(usernames)
    
    return {
        "id": str(follower_id),
        "uniqueId": username,
        "nickname": f"{username.capitalize()} User",
        "followerCount": random.randint(10, 500000),
        "followingCount": random.randint(5, 2000),
        "videoCount": random.randint(0, 1000),
        "verified": random.choice([True, False]),
        "privateAccount": random.choice([True, False]),
        "bioDescription": f"Mock bio for {username}",
        "avatarLarger": f"https://example.com/avatars/{username}.jpg",
    }


def mock_scrape_user(username: str, output_format: str = 'json', output_file: str = None, limit: int = None, include_followers: bool = False, follower_limit: int = None, quiet: bool = False):
    """
    Mock scrape user profile, optionally videos, and optionally followers (generates fake data)
    
    Args:
        username: TikTok username to mock scrape
        output_format: Output format ('json' or 'csv')
        output_file: Output file path (optional)
        limit: Maximum number of videos to generate (only if followers not requested)
        include_followers: Whether to include follower list (if True, videos are skipped)
        follower_limit: Maximum number of followers to generate
        quiet: Suppress mock warnings (makes output look more realistic)
    """
    try:
        prefix = "" if quiet else f"{CYAN} [MOCK MODE] "
        print(f"{prefix}Generating mock data for user: @{username}..." if not quiet else f"{CYAN} Loading user profile: @{username}...")
        
        # Generate mock user data
        user_data = generate_mock_user_data(username)
        print(f"{GREEN} Profile loaded: {user_data['nickname']} (@{user_data['uniqueId']})")
        print(f"{CYAN} Followers: {user_data['followerCount']:,}")
        print(f"{CYAN} Following: {user_data['followingCount']:,}")
        print(f"{CYAN} Videos: {user_data['videoCount']:,}")
        
        videos = []
        followers = []
        
        # If followers are requested, only extract followers (skip videos)
        if include_followers:
            follower_count = follower_limit if follower_limit else min(user_data['followerCount'], 100)  # Limit to 100 or specified limit
            print(f"{CYAN} Extracting followers...")
            
            for i in range(follower_count):
                follower = generate_mock_follower(i)
                followers.append(follower)
                
                if (i + 1) % 10 == 0:
                    print(f"{CYAN} Extracted {i + 1} followers so far...")
        else:
            # Generate mock videos only if followers are not requested
            video_count = limit if limit else min(user_data['videoCount'], 50)  # Limit to 50 or specified limit
            print(f"{CYAN} Extracting videos...")
            
            for i in range(video_count):
                video = generate_mock_video(i, username)
                videos.append(video)
                
                if (i + 1) % 10 == 0:
                    print(f"{CYAN} Extracted {i + 1} videos so far...")
        
        # Simulate some delay to make it feel realistic
        time.sleep(0.1)
        
        # Prepare output data
        output_data = {
            "user": user_data,
            "extracted_at": datetime.now().isoformat(),
        }
        
        if include_followers:
            output_data["followers"] = followers
            output_data["total_followers"] = len(followers)
        else:
            output_data["videos"] = videos
            output_data["total_videos"] = len(videos)
        
        if not quiet:
            output_data["mock_mode"] = True
            output_data["note"] = "This is mock/test data generated for testing purposes"
        
        # Save output
        if not output_file:
            suffix = "_mock" if not quiet else ""
            output_file = f"tiktok_user_{username}{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
        
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
                
                # Write followers if included (instead of videos)
                if include_followers and followers:
                    writer.writerow(['Follower ID', 'Username', 'Nickname', 'Followers', 'Following', 'Videos', 'Verified'])
                    for follower in followers:
                        writer.writerow([
                            follower.get('id', ''),
                            follower.get('uniqueId', ''),
                            follower.get('nickname', ''),
                            follower.get('followerCount', ''),
                            follower.get('followingCount', ''),
                            follower.get('videoCount', ''),
                            follower.get('verified', False)
                        ])
                else:
                    # Write videos only if followers are not requested
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
        if include_followers:
            print(f"{GREEN} Total followers extracted: {len(followers)}")
        else:
            print(f"{GREEN} Total videos extracted: {len(videos)}")
        if not quiet:
            print(f"{YELLOW} Note: This is test/mock data, not real TikTok data")
        
    except Exception as e:
        print(f"{RED} [MOCK] Error generating mock data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def mock_scrape_trending(output_format: str = 'json', output_file: str = None, limit: int = None):
    """
    Mock scrape trending videos (generates fake data)
    """
    try:
        print(f"{CYAN} [MOCK MODE] Generating mock trending videos...")
        
        video_count = limit if limit else 30
        print(f"{CYAN} [MOCK] Generating {video_count} mock trending videos...")
        
        videos = []
        trending_users = ['user1', 'creator2', 'tiktoker3', 'viral4', 'famous5']
        
        for i in range(video_count):
            username = random.choice(trending_users)
            video = generate_mock_video(i, username)
            videos.append(video)
            
            if (i + 1) % 10 == 0:
                print(f"{CYAN} [MOCK] Generated {i + 1}/{video_count} videos...")
        
        time.sleep(0.1)
        
        output_data = {
            "videos": videos,
            "extracted_at": datetime.now().isoformat(),
            "total_videos": len(videos),
            "mock_mode": True,
            "note": "This is mock/test data generated for testing purposes"
        }
        
        if not output_file:
            output_file = f"tiktok_trending_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
        
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
        
        print(f"{GREEN} [MOCK] Mock data saved to: {output_file}")
        print(f"{GREEN} [MOCK] Total videos generated: {len(videos)}")
        print(f"{YELLOW} [MOCK] Note: This is test/mock data, not real TikTok data")
        
    except Exception as e:
        print(f"{RED} [MOCK] Error generating mock data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def mock_scrape_hashtag(hashtag: str, output_format: str = 'json', output_file: str = None, limit: int = None):
    """
    Mock scrape hashtag videos (generates fake data)
    """
    try:
        print(f"{CYAN} [MOCK MODE] Generating mock videos for hashtag: #{hashtag}...")
        
        video_count = limit if limit else 30
        print(f"{CYAN} [MOCK] Generating {video_count} mock videos...")
        
        videos = []
        hashtag_users = [f'user{i}' for i in range(1, 10)]
        
        for i in range(video_count):
            username = random.choice(hashtag_users)
            video = generate_mock_video(i, username)
            # Add hashtag to description
            video['desc'] = f"#{hashtag} {video['desc']}"
            videos.append(video)
            
            if (i + 1) % 10 == 0:
                print(f"{CYAN} [MOCK] Generated {i + 1}/{video_count} videos...")
        
        time.sleep(0.1)
        
        output_data = {
            "hashtag": hashtag,
            "videos": videos,
            "extracted_at": datetime.now().isoformat(),
            "total_videos": len(videos),
            "mock_mode": True,
            "note": "This is mock/test data generated for testing purposes"
        }
        
        if not output_file:
            output_file = f"tiktok_hashtag_{hashtag}_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
        
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
        
        print(f"{GREEN} [MOCK] Mock data saved to: {output_file}")
        print(f"{GREEN} [MOCK] Total videos generated: {len(videos)}")
        print(f"{YELLOW} [MOCK] Note: This is test/mock data, not real TikTok data")
        
    except Exception as e:
        print(f"{RED} [MOCK] Error generating mock data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def mock_scrape_video(video_id: str, output_format: str = 'json', output_file: str = None, include_comments: bool = False, comment_limit: int = 30):
    """
    Mock scrape video details (generates fake data)
    """
    try:
        print(f"{CYAN} [MOCK MODE] Generating mock video data for: {video_id}...")
        
        # Generate mock video info
        video_info = {
            "id": video_id,
            "desc": f"Mock video description for {video_id}",
            "createTime": int(datetime.now().timestamp()) - random.randint(0, 86400 * 30),
            "author": {
                "uniqueId": "mockuser",
                "nickname": "Mock User",
            },
            "stats": {
                "diggCount": random.randint(1000, 5000000),
                "shareCount": random.randint(100, 500000),
                "commentCount": random.randint(50, 100000),
                "playCount": random.randint(10000, 10000000),
            },
            "video": {
                "downloadAddr": f"https://example.com/videos/{video_id}.mp4",
                "cover": f"https://example.com/covers/{video_id}.jpg",
                "duration": random.randint(10, 60),
            },
        }
        
        print(f"{GREEN} [MOCK] Generated video: {video_info['desc']}")
        print(f"{CYAN} [MOCK] Views: {video_info['stats']['playCount']:,}")
        print(f"{CYAN} [MOCK] Likes: {video_info['stats']['diggCount']:,}")
        
        comments = []
        if include_comments:
            print(f"{CYAN} [MOCK] Generating {comment_limit} mock comments...")
            for i in range(comment_limit):
                comments.append(generate_mock_comment(i))
                if (i + 1) % 10 == 0:
                    print(f"{CYAN} [MOCK] Generated {i + 1}/{comment_limit} comments...")
            print(f"{GREEN} [MOCK] Total comments generated: {len(comments)}")
        
        time.sleep(0.1)
        
        output_data = {
            "video": video_info,
            "extracted_at": datetime.now().isoformat(),
            "mock_mode": True,
            "note": "This is mock/test data generated for testing purposes"
        }
        
        if include_comments:
            output_data["comments"] = comments
            output_data["total_comments"] = len(comments)
        
        if not output_file:
            output_file = f"tiktok_video_{video_id}_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
        
        if output_format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
        else:  # CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Type', 'Field', 'Value'])
                writer.writerow(['Video', 'id', video_info.get('id', '')])
                writer.writerow(['Video', 'description', video_info.get('desc', '')])
                writer.writerow(['Video', 'author', video_info.get('author', {}).get('uniqueId', '')])
                writer.writerow(['Video', 'likes', video_info.get('stats', {}).get('diggCount', '')])
                writer.writerow(['Video', 'shares', video_info.get('stats', {}).get('shareCount', '')])
                writer.writerow(['Video', 'comments', video_info.get('stats', {}).get('commentCount', '')])
                writer.writerow(['Video', 'views', video_info.get('stats', {}).get('playCount', '')])
                if include_comments and comments:
                    writer.writerow([])
                    writer.writerow(['Comment ID', 'Author', 'Text', 'Likes', 'Created'])
                    for comment in comments:
                        writer.writerow([
                            comment.get('id', ''),
                            comment.get('user', {}).get('uniqueId', ''),
                            comment.get('text', '')[:100],
                            comment.get('diggCount', ''),
                            comment.get('createTime', '')
                        ])
        
        print(f"{GREEN} [MOCK] Mock data saved to: {output_file}")
        print(f"{YELLOW} [MOCK] Note: This is test/mock data, not real TikTok data")
        
    except Exception as e:
        print(f"{RED} [MOCK] Error generating mock data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='TikTok Scraper Mock/Test - Generate mock data for testing')
    parser.add_argument('-m', '--mode', choices=['user', 'trending', 'hashtag', 'video'], required=True,
                        help='Scraping mode: user, trending, hashtag, or video')
    parser.add_argument('-t', '--target', required=False,
                        help='Target: username (for user), hashtag name (for hashtag), or video ID/URL (for video). Ignored for trending.')
    parser.add_argument('-f', '--format', choices=['json', 'csv'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('-o', '--output', help='Output file path (optional, auto-generated if not provided)')
    parser.add_argument('-l', '--limit', type=int, help='Maximum number of items to generate (videos/comments)')
    parser.add_argument('--comments', action='store_true', help='Include comments when scraping video (video mode only)')
    parser.add_argument('--comment-limit', type=int, default=30, help='Maximum number of comments to generate (default: 30)')
    parser.add_argument('--session', help='Ignored in mock mode (kept for compatibility)')
    parser.add_argument('--followers', action='store_true', help='Include follower list when scraping users (user mode only)')
    parser.add_argument('--follower-limit', type=int, help='Maximum number of followers to extract (default: 100)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress mock warnings (makes output look more realistic)')
    
    args = parser.parse_args()
    
    quiet = args.quiet
    if not quiet:
        print(f"{YELLOW} [MOCK/TEST MODE] - Generating fake data for testing")
        print(f"{YELLOW} [MOCK] No real TikTok API calls will be made\n")
    
    # Run appropriate mock scraper function
    if args.mode == 'user':
        if not args.target:
            print(f"{RED} Error: --target is required for user mode")
            sys.exit(1)
        mock_scrape_user(
            args.target, 
            args.format, 
            args.output, 
            args.limit,
            include_followers=args.followers,
            follower_limit=args.follower_limit,
            quiet=quiet
        )
    elif args.mode == 'trending':
        mock_scrape_trending(args.format, args.output, args.limit)
    elif args.mode == 'hashtag':
        if not args.target:
            print(f"{RED} Error: --target is required for hashtag mode")
            sys.exit(1)
        mock_scrape_hashtag(args.target, args.format, args.output, args.limit)
    elif args.mode == 'video':
        if not args.target:
            print(f"{RED} Error: --target is required for video mode")
            sys.exit(1)
        # Extract video ID from URL if needed
        video_id = args.target
        if 'tiktok.com' in video_id:
            # Try to extract ID from URL (simplified - just use a mock ID)
            video_id = video_id.split('/')[-1] if '/' in video_id else video_id
            if not video_id or video_id == args.target:
                video_id = str(random.randint(7000000000000000000, 7999999999999999999))
        mock_scrape_video(video_id, args.format, args.output, args.comments, args.comment_limit if args.comments else None)


if __name__ == '__main__':
    main()

