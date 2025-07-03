import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import time
import random

def get_ai_website_updates() -> List[Dict[str, str]]:
    """
    Scrape high-quality AI content from top AI research blogs and news sites.
    Focus on RSS feeds and easily accessible content.
    """
    all_updates = []
    
    print("🚀 Fetching from top AI research blogs and news sites...")
    
    # Get updates from RSS feeds (most reliable)
    all_updates.extend(get_ai_rss_feeds())
    
    # Get updates from specific high-quality sites
    all_updates.extend(get_research_blog_updates())
    
    print(f"📊 Collected {len(all_updates)} high-quality AI updates")
    return all_updates

def get_ai_rss_feeds() -> List[Dict[str, str]]:
    """Fetch from top AI RSS feeds that are reliable and high-quality."""
    updates = []
    
    # Top AI RSS feeds with proven track records + AI thinker blogs
    rss_feeds = [
        # Major AI Research Labs
        ("Google AI Blog", "https://ai.googleblog.com/feeds/posts/default"),
        ("OpenAI Blog", "https://openai.com/blog/rss.xml"), 
        ("DeepMind Blog", "https://deepmind.com/blog/feed/basic"),
        ("Berkeley AI Research", "https://bair.berkeley.edu/blog/feed.xml"),
        ("Meta AI Blog", "https://ai.meta.com/blog/feed/"),
        ("AWS Machine Learning", "https://aws.amazon.com/blogs/machine-learning/feed/"),
        ("Microsoft Research AI", "https://www.microsoft.com/en-us/research/feed/?post-type=msr-blog-post&research-area=artificial-intelligence"),
        
        # AI News & Analysis Sites
        ("MarkTechPost", "https://www.marktechpost.com/feed/"),
        ("Analytics India Magazine", "https://analyticsindiamag.com/feed/"),
        ("Machine Learning Mastery", "https://machinelearningmastery.com/feed/"),
        
        # Famous AI Thinkers & Practitioners (Personal Blogs)
        ("Andrej Karpathy Blog", "https://karpathy.bearblog.dev/feed/"),
        ("Swyx (AI Engineer)", "https://www.swyx.io/rss.xml"),
        ("Benedict Evans", "https://www.ben-evans.com/feed"),
        ("Elad Gil Blog", "https://blog.eladgil.com/feeds/posts/default"),
        ("Sebastian Raschka", "https://sebastianraschka.com/rss.xml"),
        ("Chip Huyen", "https://huyenchip.com/feed.xml"),
        ("Eugene Yan", "https://eugeneyan.com/feed.xml"),
        ("Lilian Weng", "https://lilianweng.github.io/feed.xml"),
        ("Jay Alammar", "https://jalammar.github.io/feed.xml"),
        ("Christopher Olah", "https://colah.github.io/rss.xml"),
        ("Distill AI", "https://distill.pub/rss.xml"),
        ("Papers With Code", "https://paperswithcode.com/latest.rss"),
        ("AI Alignment Forum", "https://www.alignmentforum.org/feed.xml")
    ]
    
    cutoff_date = datetime.now() - timedelta(days=30)  # Last 30 days only
    print(f"📅 Filtering for content newer than {cutoff_date.strftime('%Y-%m-%d')}")
    
    for source_name, feed_url in rss_feeds:
        try:
            print(f"📡 Fetching from {source_name}...")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:3]:  # Top 3 posts per source
                try:
                    # Parse publication date
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()  # Default to now if no date
                    
                    # Only include posts from last 30 days
                    if pub_date >= cutoff_date:
                        # Clean and extract content
                        title = entry.title if hasattr(entry, 'title') else "No title"
                        summary = ""
                        if hasattr(entry, 'summary'):
                            summary = BeautifulSoup(entry.summary, 'html.parser').get_text()[:300]
                        elif hasattr(entry, 'description'):
                            summary = BeautifulSoup(entry.description, 'html.parser').get_text()[:300]
                        
                        link = entry.link if hasattr(entry, 'link') else feed_url
                        
                        # Filter for AI/ML relevant content
                        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 
                                     'neural network', 'llm', 'gpt', 'transformer', 'agent', 'rag',
                                     'generative', 'chatgpt', 'claude', 'model', 'algorithm']
                        
                        content_text = f"{title} {summary}".lower()
                        if any(keyword in content_text for keyword in ai_keywords):
                            update = {
                                "source": source_name,
                                "type": "ai_blog",
                                "title": title,
                                "summary": summary,
                                "link": link,
                                "date": pub_date.strftime("%Y-%m-%d"),
                                "content_type": "research_blog"
                            }
                            updates.append(update)
                            
                except Exception as e:
                    print(f"  ⚠️ Error parsing entry from {source_name}: {e}")
                    continue
                    
            # Small delay between feeds
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ Failed to fetch {source_name}: {e}")
            continue
    
    return updates

def get_research_blog_updates() -> List[Dict[str, str]]:
    """Scrape specific high-quality AI research and news sites."""
    updates = []
    
    # High-quality sites with structured content
    sites = [
        {
            "name": "Towards Data Science", 
            "url": "https://towardsdatascience.com/feed",
            "type": "rss"
        },
        {
            "name": "The Gradient", 
            "url": "https://thegradient.pub/rss/",
            "type": "rss" 
        },
        {
            "name": "AI Research Blog",
            "url": "https://ai.googleblog.com/",
            "type": "web"
        },
        {
            "name": "Neptune AI Blog",
            "url": "https://neptune.ai/blog/rss.xml",
            "type": "rss"
        },
        {
            "name": "MLOps Community",
            "url": "https://mlops.community/feed/",
            "type": "rss"
        },
        {
            "name": "Weights & Biases Blog",
            "url": "https://wandb.ai/site/rss.xml",
            "type": "rss"
        },
        {
            "name": "AssemblyAI Blog",
            "url": "https://www.assemblyai.com/blog/rss.xml",
            "type": "rss"
        }
    ]
    
    for site in sites:
        try:
            if site["type"] == "rss":
                # Handle RSS feeds
                print(f"📡 Fetching RSS from {site['name']}...")
                feed = feedparser.parse(site["url"])
                
                for entry in feed.entries[:2]:  # Top 2 posts per site
                    try:
                        title = getattr(entry, 'title', 'No title')
                        summary = ""
                        if hasattr(entry, 'summary'):
                            summary = BeautifulSoup(entry.summary, 'html.parser').get_text()[:200]
                        
                        # Filter for AI content
                        ai_keywords = ['ai', 'machine learning', 'deep learning', 'neural', 'llm', 'gpt', 'agent']
                        if any(keyword in f"{title} {summary}".lower() for keyword in ai_keywords):
                            update = {
                                "source": site["name"],
                                "type": "ai_research",
                                "title": title,
                                "summary": summary,
                                "link": getattr(entry, 'link', site["url"]),
                                "date": datetime.now().strftime("%Y-%m-%d"),
                                "content_type": "research_article"
                            }
                            updates.append(update)
                    except Exception as e:
                        continue
                        
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"  ❌ Failed to fetch {site['name']}: {e}")
            continue
    
    return updates

def get_ai_news_aggregators() -> List[Dict[str, str]]:
    """Get AI news from aggregator sites."""
    updates = []
    
    try:
        # AI-specific Hacker News stories from last 30 days
        print("📰 Fetching AI stories from Hacker News...")
        cutoff_timestamp = int((datetime.now() - timedelta(days=30)).timestamp())
        url = f"https://hn.algolia.com/api/v1/search_by_date?query=AI OR machine learning OR LLM OR GPT&tags=story&numericFilters=created_at_i>{cutoff_timestamp}"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        for hit in data.get('hits', [])[:5]:  # Top 5 AI stories
            try:
                created_at = datetime.fromisoformat(hit['created_at'].replace('Z', '+00:00'))
                
                update = {
                    "source": "Hacker News AI",
                    "type": "ai_news",
                    "title": hit['title'],
                    "summary": f"HN discussion with {hit.get('points', 0)} points",
                    "link": hit.get('url', f"https://news.ycombinator.com/item?id={hit['objectID']}"),
                    "date": created_at.strftime("%Y-%m-%d"),
                    "content_type": "news_discussion"
                }
                updates.append(update)
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"  ❌ Failed to fetch AI news: {e}")
    
    return updates

if __name__ == "__main__":
    # Test the scraper
    updates = get_ai_website_updates()
    print(f"\n📊 Collected {len(updates)} AI updates")
    
    for i, update in enumerate(updates[:5], 1):
        print(f"\n--- Update {i} ---")
        print(f"Source: {update['source']}")
        print(f"Title: {update['title']}")
        print(f"Type: {update['content_type']}")
        print(f"Link: {update['link']}")
        print(f"Date: {update['date']}")