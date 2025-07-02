# AI Strategy Brief Generator

A multi-agent system using CrewAI that generates personalized daily AI strategy briefs by scanning real-world AI sources and pushing curated insights to Notion.

## Overview

This system creates a daily AI strategy brief by:
1. **Fetching real AI updates** from multiple sources (Substack RSS feeds, Hacker News, GitHub Trending)
2. **Processing through specialized agents**:
   - **Signal Hunter**: Finds buildable agent/RAG projects with working code
   - **Relevance Scorer**: Scores updates based on practical building opportunities
   - **Action Generator**: Creates hands-on learning projects
   - **Brief Editor**: Compiles a polished strategy brief
3. **Pushing to Notion** with full page content for each signal

## Features

- 🔍 Real-time scanning of AI news and repositories
- 🤖 Multi-agent orchestration with CrewAI
- 🎯 Personalized scoring based on your interests (agent systems, RAG, CrewAI/LangChain)
- 🛠️ Actionable build projects, not just reading material
- 📊 Automatic Notion integration with formatted pages
- 🔗 Direct links to all sources for further reading

## Setup

### Prerequisites

- Python 3.8+
- OpenRouter API account
- Notion API integration

### Installation

1. Clone this repository:
```bash
git clone https://github.com/morhogeg/AIBrief.git
cd AIBrief
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENROUTER_API_KEY=your_openrouter_api_key
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
```

### Notion Setup

1. Create a new Notion integration at https://www.notion.so/my-integrations
2. Create a new database in Notion with at least these properties:
   - Name (title)
   - Date (date)
3. Share the database with your integration
4. Copy the database ID from the URL and add to `.env`

## Usage

Run the strategy brief generator:
```bash
python crew_strategy_brief.py
```

The system will:
1. Fetch the latest AI updates
2. Process them through the multi-agent system
3. Generate a markdown brief
4. Push to your Notion database with full page content

## Project Structure

```
ai-strategy-brief/
├── crew_strategy_brief.py    # Main orchestrator with CrewAI agents
├── data_collector.py          # Fetches updates from multiple sources
├── llm_config.py             # OpenRouter LLM configuration
├── notion_integration.py      # Pushes formatted briefs to Notion
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables (not in repo)
```

## Customization

### Agent Personalities

Modify agent backstories and goals in `crew_strategy_brief.py` to match your interests:
- Signal Hunter: Focus areas for finding updates
- Relevance Scorer: Scoring criteria for relevance
- Action Generator: Types of projects to create
- Brief Editor: Formatting preferences

### Data Sources

Add or modify sources in `data_collector.py`:
- RSS feeds: Add to `substack_feeds` list
- Hacker News: Adjust search keywords
- GitHub: Modify trending parameters

## Troubleshooting

### OpenRouter Rate Limits
Free tier allows 50 requests/day. Add credits ($10 for 1000 requests) if you hit limits.

### Missing Links
The system only uses real URLs from source data. If links are missing, check that the source actually provided them.

### Notion Errors
- Ensure your database ID is correct (not a page ID)
- Verify the integration has access to your database
- Check that required properties exist in your database

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.