#!/usr/bin/env python3
"""
PSAI_1 - Culture Current Lite: Data Harvesting Module
Purpose: Collect data from RSS, Reddit, and YouTube sources with deduplication
Last Modified: 2024-12-19 | By: AI Assistant | Completeness: 85/100
"""

import os
import sys
import json
import hashlib
import requests
import feedparser
import praw
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from loguru import logger
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class HarvestedItem:
    """Standardized data structure for harvested content"""
    url: str
    title: str
    content: str
    source: str
    source_type: str  # 'rss', 'reddit', 'youtube'
    published_date: str
    author: Optional[str] = None
    tags: List[str] = None
    url_hash: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.url_hash is None:
            self.url_hash = hashlib.md5(self.url.encode()).hexdigest()
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

class DataHarvester:
    """Main harvesting class supporting multiple data sources"""
    
    def __init__(self, config_path: str = "config/harvest_config.json"):
        self.config = self._load_config(config_path)
        self.harvested_items: List[HarvestedItem] = []
        self.duplicate_cache: set = set()
        
        # Initialize APIs
        self._setup_reddit()
        self._setup_youtube()
        
        logger.info(f"DataHarvester initialized with {len(self.config.get('sources', {}))} sources")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load harvesting configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default configuration for testing"""
        return {
            "sources": {
                "rss": [
                    "https://feeds.bbci.co.uk/news/technology/rss.xml",
                    "https://rss.cnn.com/rss/edition_technology.rss"
                ],
                "reddit": {
                    "subreddits": ["technology", "programming", "MachineLearning"],
                    "limit": 10
                },
                "youtube": {
                    "channels": ["UCBJycsmduvYEL83R_U4JriQ"],  # Marques Brownlee
                    "max_results": 5
                }
            },
            "deduplication": {
                "enabled": True,
                "cache_file": "data/url_cache.json"
            }
    }
    
    def _setup_reddit(self):
        """Initialize Reddit API client"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent='PSAI_1_Culture_Current/1.0'
            )
            logger.info("Reddit API initialized successfully")
        except Exception as e:
            logger.warning(f"Reddit API setup failed: {e}")
            self.reddit = None
    
    def _setup_youtube(self):
        """Initialize YouTube API client"""
        try:
            from googleapiclient.discovery import build
            self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
            logger.info("YouTube API initialized successfully")
        except Exception as e:
            logger.warning(f"YouTube API setup failed: {e}")
            self.youtube = None
    
    def harvest_all_sources(self) -> List[HarvestedItem]:
        """Harvest from all configured sources"""
        logger.info("Starting comprehensive data harvest")
        
        # Load existing cache to avoid duplicates
        self._load_duplicate_cache()
        
        # Harvest from each source type
        if 'rss' in self.config.get('sources', {}):
            self._harvest_rss()
        
        if 'reddit' in self.config.get('sources', {}) and self.reddit:
            self._harvest_reddit()
        
        if 'youtube' in self.config.get('sources', {}) and self.youtube:
            self._harvest_youtube()
        
        # Save cache and return results
        self._save_duplicate_cache()
        logger.info(f"Harvest complete: {len(self.harvested_items)} items collected")
        
        return self.harvested_items
    
    def _harvest_rss(self):
        """Harvest from RSS feeds"""
        logger.info("Harvesting RSS feeds")
        
        for feed_url in self.config['sources']['rss']:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Limit to 10 per feed
                    item = HarvestedItem(
                        url=entry.link,
                        title=entry.title,
                        content=getattr(entry, 'summary', ''),
                        source=feed_url,
                        source_type='rss',
                        published_date=entry.get('published', ''),
                        author=getattr(entry, 'author', None),
                        tags=[tag.term for tag in getattr(entry, 'tags', [])]
                    )
                    
                    if self._is_new_item(item):
                        self.harvested_items.append(item)
                        self.duplicate_cache.add(item.url_hash)
                
                logger.info(f"RSS harvest from {feed_url}: {len(feed.entries)} entries processed")
                
            except Exception as e:
                logger.error(f"RSS harvest failed for {feed_url}: {e}")
    
    def _harvest_reddit(self):
        """Harvest from Reddit subreddits"""
        logger.info("Harvesting Reddit content")
        
        reddit_config = self.config['sources']['reddit']
        
        for subreddit_name in reddit_config['subreddits']:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                for submission in subreddit.hot(limit=reddit_config['limit']):
                    item = HarvestedItem(
                        url=f"https://reddit.com{submission.permalink}",
                        title=submission.title,
                        content=submission.selftext or submission.url,
                        source=f"r/{subreddit_name}",
                        source_type='reddit',
                        published_date=datetime.fromtimestamp(submission.created_utc).isoformat(),
                        author=str(submission.author) if submission.author else None,
                        tags=[subreddit_name],
                        metadata={
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'upvote_ratio': submission.upvote_ratio
                        }
                    )
                    
                    if self._is_new_item(item):
                        self.harvested_items.append(item)
                        self.duplicate_cache.add(item.url_hash)
                
                logger.info(f"Reddit harvest from r/{subreddit_name}: {reddit_config['limit']} posts processed")
                
            except Exception as e:
                logger.error(f"Reddit harvest failed for r/{subreddit_name}: {e}")
    
    def _harvest_youtube(self):
        """Harvest from YouTube channels"""
        logger.info("Harvesting YouTube content")
        
        youtube_config = self.config['sources']['youtube']
        
        for channel_id in youtube_config['channels']:
            try:
                # Get channel info
                channel_response = self.youtube.channels().list(
                    part='snippet',
                    id=channel_id
                ).execute()
                
                if not channel_response['items']:
                    continue
                
                channel_name = channel_response['items'][0]['snippet']['title']
                
                # Get recent videos
                search_response = self.youtube.search().list(
                    part='snippet',
                    channelId=channel_id,
                    maxResults=youtube_config['max_results'],
                    order='date',
                    type='video'
                ).execute()
                
                for video in search_response['items']:
                    item = HarvestedItem(
                        url=f"https://youtube.com/watch?v={video['id']['videoId']}",
                        title=video['snippet']['title'],
                        content=video['snippet']['description'],
                        source=channel_name,
                        source_type='youtube',
                        published_date=video['snippet']['publishedAt'],
                        author=channel_name,
                        tags=[video['snippet']['channelTitle']],
                        metadata={
                            'video_id': video['id']['videoId'],
                            'thumbnail': video['snippet']['thumbnails']['default']['url']
                        }
                    )
                    
                    if self._is_new_item(item):
                        self.harvested_items.append(item)
                        self.duplicate_cache.add(item.url_hash)
                
                logger.info(f"YouTube harvest from {channel_name}: {len(search_response['items'])} videos processed")
                
            except Exception as e:
                logger.error(f"YouTube harvest failed for channel {channel_id}: {e}")
    
    def _is_new_item(self, item: HarvestedItem) -> bool:
        """Check if item is new (not in cache)"""
        if not self.config.get('deduplication', {}).get('enabled', True):
            return True
        
        return item.url_hash not in self.duplicate_cache
    
    def _load_duplicate_cache(self):
        """Load existing URL cache to avoid duplicates"""
        cache_file = self.config.get('deduplication', {}).get('cache_file', 'data/url_cache.json')
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                self.duplicate_cache = set(cache_data.get('url_hashes', []))
                logger.info(f"Loaded {len(self.duplicate_cache)} cached URLs")
        except FileNotFoundError:
            logger.info("No existing cache found, starting fresh")
            self.duplicate_cache = set()
    
    def _save_duplicate_cache(self):
        """Save URL cache to avoid future duplicates"""
        cache_file = self.config.get('deduplication', {}).get('cache_file', 'data/url_cache.json')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        
        cache_data = {
            'last_updated': datetime.now().isoformat(),
            'url_hashes': list(self.duplicate_cache)
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        logger.info(f"Saved {len(self.duplicate_cache)} URLs to cache")
    
    def save_to_google_sheets(self, sheet_name: str = "PSAI_Harvest"):
        """Save harvested data to Google Sheets"""
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            # Setup credentials
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file(
                os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE'), scopes=scope)
            gc = gspread.authorize(creds)
            
            # Open or create sheet
            try:
                sheet = gc.open(sheet_name).sheet1
            except gspread.SpreadsheetNotFound:
                sheet = gc.create(sheet_name).sheet1
            
            # Prepare data
            data = [asdict(item) for item in self.harvested_items]
            df = pd.DataFrame(data)
            
            # Clear and update sheet
            sheet.clear()
            sheet.update([df.columns.values.tolist()] + df.values.tolist())
            
            logger.info(f"Saved {len(self.harvested_items)} items to Google Sheets")
            
        except Exception as e:
            logger.error(f"Google Sheets save failed: {e}")
    
    def save_to_json(self, filename: str = None):
        """Save harvested data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/harvest_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        data = {
            'harvest_timestamp': datetime.now().isoformat(),
            'total_items': len(self.harvested_items),
            'items': [asdict(item) for item in self.harvested_items]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved harvest data to {filename}")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PSAI_1 Data Harvester')
    parser.add_argument('--source', choices=['rss', 'reddit', 'youtube', 'all'], 
                       default='all', help='Source type to harvest')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--sheets', action='store_true', help='Save to Google Sheets')
    
    args = parser.parse_args()
    
    # Setup logging
    logger.add("logs/harvest.log", rotation="1 week", retention="1 month")
    
    # Initialize harvester
    harvester = DataHarvester()
    
    if args.test:
        logger.info("Running in test mode with limited data")
        # Modify config for testing
        harvester.config['sources']['rss'] = harvester.config['sources']['rss'][:1]
        harvester.config['sources']['reddit']['limit'] = 2
        harvester.config['sources']['youtube']['max_results'] = 2
    
    # Harvest data
    items = harvester.harvest_all_sources()
    
    # Save results
    if args.sheets:
        harvester.save_to_google_sheets()
    
    if args.output:
        harvester.save_to_json(args.output)
    else:
        harvester.save_to_json()
    
    print(f"Harvest complete: {len(items)} items collected")
    logger.info(f"Harvest complete: {len(items)} items collected")

if __name__ == "__main__":
    main()
