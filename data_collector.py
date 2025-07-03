import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import json
import time
import random
from ai_website_scraper import get_ai_website_updates

def get_real_ai_updates() -> List[Dict[str, str]]:
    """Gather daily real-time AI content from high-quality sources (last 30 days only)."""
    all_updates = []
    
    # Use high-quality AI sources with 30-day freshness guarantee
    print("🔍 Scanning high-quality AI sources (last 30 days only)...")
    all_updates.extend(get_substack_updates())
    all_updates.extend(get_hackernews_updates()) 
    all_updates.extend(get_github_updates())
    all_updates.extend(get_ai_website_updates())  # High-quality AI research blogs and news
    
    # Final date validation - ensure no content is older than 30 days
    cutoff_date = datetime.now() - timedelta(days=30)
    filtered_updates = []
    
    for update in all_updates:
        try:
            # Parse the date from the update
            if 'date' in update and update['date']:
                update_date = datetime.strptime(update['date'], '%Y-%m-%d')
                if update_date >= cutoff_date:
                    filtered_updates.append(update)
                else:
                    print(f"⏰ Filtered out old content: {update.get('title', 'Unknown')} ({update['date']})")
            else:
                # If no date, assume it's current (like GitHub trending)
                filtered_updates.append(update)
        except Exception as e:
            # If date parsing fails, include it anyway (better safe than sorry)
            filtered_updates.append(update)
    
    print(f"✅ Final result: {len(filtered_updates)} updates (filtered {len(all_updates) - len(filtered_updates)} old items)")
    return filtered_updates

def get_substack_updates() -> List[Dict[str, str]]:
    """Fetch AI newsletter updates from Substack RSS feeds."""
    updates = []
    feeds = [
        ("Ben's Bites", "https://www.bensbites.co/rss"),
        ("Latent Space", "https://latent.space/feed.xml"), 
        ("Import AI", "https://jack-clark.net/index.xml"),
        ("The Rundown AI", "https://www.therundown.ai/rss"),
        ("AI Breakfast", "https://aibreakfast.beehiiv.com/feed")
    ]
    
    cutoff_date = datetime.now() - timedelta(days=30)  # Last 30 days only
    print(f"📅 Newsletter filtering: content newer than {cutoff_date.strftime('%Y-%m-%d')}")
    
    for newsletter_name, feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                # Parse publication date
                pub_date = datetime(*entry.published_parsed[:6])
                
                # Only include posts from the last 30 days
                if pub_date >= cutoff_date:
                    update = {
                        "source": newsletter_name,
                        "type": "newsletter",
                        "title": entry.title,
                        "summary": entry.get('summary', '')[:500],  # Limit summary length
                        "link": entry.link,
                        "date": pub_date.strftime("%Y-%m-%d")
                    }
                    updates.append(update)
        except Exception as e:
            print(f"Error fetching {newsletter_name}: {e}")
    
    return updates

def get_hackernews_updates() -> List[Dict[str, str]]:
    """Fetch AI-related posts from Hacker News."""
    updates = []
    
    try:
        # Get AI/ML posts from the last 30 days with better keywords
        cutoff_timestamp = int((datetime.now() - timedelta(days=30)).timestamp())
        print(f"📅 Hacker News filtering: posts newer than {datetime.fromtimestamp(cutoff_timestamp).strftime('%Y-%m-%d')}")
        url = f"https://hn.algolia.com/api/v1/search_by_date?query=AI OR machine learning OR LLM OR GPT OR CrewAI OR LangChain OR agent OR RAG&tags=story&numericFilters=created_at_i>{cutoff_timestamp}"
        
        response = requests.get(url)
        data = response.json()
        
        for hit in data.get('hits', []):
            # Parse the creation date
            created_at = datetime.fromisoformat(hit['created_at'].replace('Z', '+00:00'))
            
            update = {
                "source": "Hacker News",
                "type": "news",
                "title": hit['title'],
                "points": hit.get('points', 0),
                "link": hit.get('url', f"https://news.ycombinator.com/item?id={hit['objectID']}"),
                "date": created_at.strftime("%Y-%m-%d")
            }
            updates.append(update)
    except Exception as e:
        print(f"Error fetching Hacker News: {e}")
    
    return updates

def get_github_updates() -> List[Dict[str, str]]:
    """Scrape trending AI projects from GitHub (inherently recent - daily trending)."""
    updates = []
    print("📅 GitHub trending: fetching today's trending AI repos")
    ai_keywords = ['ai', 'llm', 'rag', 'agent', 'gpt', 'neural', 'machine learning', 'deep learning', 
                   'crewai', 'langchain', 'openai', 'anthropic', 'claude', 'transformer', 'vector', 'embedding']
    
    try:
        url = "https://github.com/trending?since=daily&spoken_language_code=en"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all repository articles
        repos = soup.find_all('article', class_='Box-row')
        
        for repo in repos:
            try:
                # Extract repository information
                h2 = repo.find('h2', class_='h3')
                if not h2:
                    continue
                    
                repo_link = h2.find('a')
                if not repo_link:
                    continue
                    
                repo_name = repo_link.get('href', '').strip('/')
                repo_url = f"https://github.com/{repo_name}"
                
                # Get description
                desc_p = repo.find('p', class_='col-9')
                description = desc_p.text.strip() if desc_p else ""
                
                # Check if it's AI-related
                desc_lower = description.lower()
                if any(keyword in desc_lower for keyword in ai_keywords):
                    # Get stars count
                    stars_span = repo.find('span', class_='d-inline-block float-sm-right')
                    stars = 0
                    if stars_span:
                        stars_text = stars_span.text.strip().replace(',', '')
                        try:
                            stars = int(stars_text.split()[0])
                        except:
                            stars = 0
                    
                    update = {
                        "source": "GitHub",
                        "type": "repo",
                        "name": repo_name,
                        "description": description,
                        "stars": stars,
                        "link": repo_url,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                    updates.append(update)
            except Exception as e:
                print(f"Error parsing repo: {e}")
                continue
    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
    
    return updates


if __name__ == "__main__":
    # Test the function
    updates = get_real_ai_updates()
    print(f"Found {len(updates)} updates")
    for update in updates[:5]:  # Print first 5
        print(json.dumps(update, indent=2))