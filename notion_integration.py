import os
import re
from datetime import datetime
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

def extract_section_content(markdown_text, header):
    """Extract content between a specific header and the next header."""
    lines = markdown_text.split('\n')
    in_section = False
    content = []
    
    for line in lines:
        if header in line:
            in_section = True
            continue
        elif (line.startswith('##') or line.startswith('###')) and in_section:
            break
        elif line.startswith('⸻') and in_section:
            break
        elif in_section:
            content.append(line)
    
    return '\n'.join(content).strip()

def parse_articles_from_brief(markdown_text):
    """Parse the brief and extract article information grouped by source."""
    articles = []
    
    # Extract the three main sections
    top_signals = extract_section_content(markdown_text, '📌 Top 5 AI Signals')
    relevance_summary = extract_section_content(markdown_text, '🎯 Relevance Summary') 
    suggested_actions = extract_section_content(markdown_text, '✅ Today\'s Suggested Actions')
    
    # Parse signals (numbered list)
    signal_articles = parse_signal_entries(top_signals)
    
    # Parse relevance data 
    relevance_data = parse_relevance_data(relevance_summary)
    
    # Parse actions
    actions = parse_action_entries(suggested_actions)
    
    print(f"🔍 Debug: Found {len(signal_articles)} signals, {len(relevance_data)} relevance entries, {len(actions)} actions")
    
    # Since the titles don't match between sections, we'll use order-based matching
    # The agents are working on the same top 5 articles in the same order
    
    relevance_list = list(relevance_data.values())
    
    for i, signal in enumerate(signal_articles):
        article = {
            'title': signal.get('title', 'Unknown'),
            'source': signal.get('source', 'Unknown'),
            'why_matters': signal.get('why_matters', ''),
            'link': signal.get('link', ''),
            'relevance_score': 'N/A',
            'tags': 'N/A',
            'explanation': 'N/A',
            'action': None
        }
        
        # Match relevance data by order (index)
        if i < len(relevance_list):
            rel_data = relevance_list[i]
            article['relevance_score'] = rel_data.get('relevance_score', 'N/A')
            article['tags'] = rel_data.get('tags', 'N/A') 
            article['explanation'] = rel_data.get('explanation', 'N/A')
            print(f"✅ Matched signal #{i+1} with relevance data: score={article['relevance_score']}")
        else:
            print(f"⚠️  No relevance data for signal #{i+1}: {article['title']}")
        
        # Match action by order (index)
        if i < len(actions):
            article['action'] = actions[i]
            print(f"✅ Matched signal #{i+1} with action")
        else:
            print(f"⚠️  No action for signal #{i+1}: {article['title']}")
        
        articles.append(article)
    
    return articles

def parse_signal_entries(signals_text):
    """Parse numbered signal entries."""
    entries = []
    current_entry = {}
    
    for line in signals_text.split('\n'):
        line = line.strip()
        if re.match(r'^\d+\.\s*\*\*(.+?)\*\*', line):
            # Save previous entry
            if current_entry:
                entries.append(current_entry)
            # Start new entry
            title_match = re.search(r'\*\*(.+?)\*\*', line)
            current_entry = {'title': title_match.group(1) if title_match else 'Unknown'}
        elif line.startswith('• Source:'):
            current_entry['source'] = line.replace('• Source:', '').strip()
        elif line.startswith('• Why it matters:'):
            current_entry['why_matters'] = line.replace('• Why it matters:', '').strip()
        elif line.startswith('• Link:'):
            # Extract link - could be markdown format [text](url) or plain URL
            link_text = line.replace('• Link:', '').strip()
            # Extract URL from markdown format if present
            markdown_link = re.search(r'\[.*?\]\((.*?)\)', link_text)
            if markdown_link:
                current_entry['link'] = markdown_link.group(1)
            else:
                current_entry['link'] = link_text
    
    # Don't forget the last entry
    if current_entry:
        entries.append(current_entry)
    
    return entries

def parse_relevance_data(relevance_text):
    """Parse relevance summary data."""
    relevance_data = {}
    current_title = None
    current_data = {}
    
    for line in relevance_text.split('\n'):
        line = line.strip()
        if line.startswith('**') and line.endswith('**'):
            # Save previous entry
            if current_title and current_data:
                relevance_data[current_title] = current_data
            # Start new entry
            current_title = line.strip('*').strip()
            current_data = {}
        elif current_title and line:
            if line.startswith('• Relevance Score:'):
                score = re.search(r'(\d+)', line)
                current_data['relevance_score'] = score.group(1) if score else 'N/A'
            elif line.startswith('• Tags:'):
                current_data['tags'] = line.replace('• Tags:', '').strip()
            elif line.startswith('• Explanation:'):
                current_data['explanation'] = line.replace('• Explanation:', '').strip()
            elif line.startswith('• Time to first working version:'):
                current_data['time_estimate'] = line.replace('• Time to first working version:', '').strip()
    
    # Don't forget the last entry
    if current_title and current_data:
        relevance_data[current_title] = current_data
    
    return relevance_data

def parse_action_entries(actions_text):
    """Parse suggested action entries."""
    actions = []
    current_action = []
    
    for line in actions_text.split('\n'):
        if line.startswith('✅'):
            if current_action:
                actions.append('\n'.join(current_action))
            current_action = [line]
        elif current_action and line.strip():
            current_action.append(line)
    
    if current_action:
        actions.append('\n'.join(current_action))
    
    return actions

def format_grouped_content(articles):
    """Format articles into grouped content blocks."""
    content_blocks = []
    
    for article in articles:
        block = f"""⸻

🔹 **{article['title']}**

Source: {article['source']}
Why it matters: {article['why_matters']}
Relevance Score: {article['relevance_score']}
Tags: {article['tags']}"""
        
        # Add explanation if available
        if article['explanation'] != 'N/A' and article['explanation']:
            block += f"\nExplanation: {article['explanation']}"
        
        # Always add the source link for further reading
        if article['link']:
            block += f"\n🔗 Read more: {article['link']}"
        
        # Add action if available
        if article['action']:
            block += f"\n\nAction:\n{article['action']}"
        else:
            # Add a note if no specific action was generated for this article
            block += f"\n\nAction: No specific action generated - bookmark for future reference."
        
        content_blocks.append(block)
    
    return '\n\n'.join(content_blocks) + '\n\n⸻'

def create_notion_blocks(content):
    """Convert markdown content to Notion blocks."""
    blocks = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        elif line == '⸻':
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        elif line.startswith('🔹 **') and line.endswith('**'):
            # Title
            title_text = line.replace('🔹 **', '').replace('**', '')
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"🔹 {title_text}"}
                        }
                    ]
                }
            })
        elif line.startswith(('Source:', 'Why it matters:', 'Relevance Score:', 'Tags:', 'Action:')):
            # Property line
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": line},
                            "annotations": {"bold": True}
                        }
                    ]
                }
            })
        else:
            # Regular paragraph
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": line}
                        }
                    ]
                }
            })
    
    return blocks

def push_to_notion():
    """Push the daily strategy brief to Notion database with a full page."""
    try:
        # Load environment variables
        notion_token = os.getenv("NOTION_TOKEN")
        database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not notion_token or not database_id:
            print("❌ Missing NOTION_TOKEN or NOTION_DATABASE_ID in .env file")
            return False
        
        # Read the markdown file
        try:
            with open("strategy_brief.md", "r", encoding="utf-8") as f:
                markdown_text = f.read()
        except FileNotFoundError:
            print("❌ strategy_brief.md not found")
            return False
        
        # Parse articles from the brief
        articles = parse_articles_from_brief(markdown_text)
        
        # Format into grouped content
        formatted_content = format_grouped_content(articles)
        
        # Initialize Notion client
        notion = Client(auth=notion_token)
        
        # Get today's date
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Step 1: Create database row
        database_row = {
            "parent": {
                "type": "database_id",
                "database_id": database_id
            },
            "properties": {
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"AI Brief – {today_date}"
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": today_date
                    }
                }
            }
        }
        
        # Create the database row
        row_response = notion.pages.create(**database_row)
        row_page_id = row_response['id']
        
        print(f"✅ Database row created: {row_response['url']}")
        
        # Step 2: Create full content page as child of the row
        content_blocks = create_notion_blocks(formatted_content)
        
        # Add title block at the beginning
        title_block = {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": f"AI Strategy Brief - {today_date}"}
                    }
                ]
            }
        }
        
        # Add all blocks to the page
        all_blocks = [title_block] + content_blocks
        
        # Notion has a limit on blocks per request, so we'll add them in chunks
        for i in range(0, len(all_blocks), 100):  # Process in chunks of 100
            chunk = all_blocks[i:i+100]
            notion.blocks.children.append(
                block_id=row_page_id,
                children=chunk
            )
        
        print("✅ AI Brief successfully pushed to Notion page")
        print(f"📄 View full brief at: {row_response['url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error pushing to Notion: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the function
    push_to_notion()