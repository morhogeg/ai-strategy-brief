# AI Strategy Brief Generator

A modular, multi-agent system powered by CrewAI that delivers daily AI strategy briefs optimized for hands-on builders and agentic system designers.

> ⚠️ **Note**: This system is personalized for my workflow as an AI founder. Please feel free to learn from the code, but avoid forking it directly — it's tuned specifically for my use case.

## Overview

CrewAI coordinates 4 tightly scoped agents in a sequential pipeline:
• **Signal Hunter**: collects relevant updates
• **Relevance Scorer**: filters and ranks based on buildability  
• **Action Generator**: suggests 30–60 min hands-on projects
• **Brief Editor**: compiles a clean, readable brief

**What it does:**
• Scans 40+ curated AI sources (labs, blogs, newsletters, GitHub, Hacker News)
• Filters and scores updates using 4 specialized agents
• Publishes full daily briefs to Notion with actionable project suggestions
• Focuses only on buildable, hands-on content (not just news)
• Filters to content from the last 30 days

**Example Output:**
```
🔹 Build a CrewAI chatbot that summarizes your GitHub PRs
• Source: Hacker News discussion
• Why it matters: Uses RAG + CrewAI to create real-time engineering context
• Relevance Score: 9/10
• Time to build: 45 minutes
• Link: [View Repo](https://github.com/example/crewai-pr-summary)
```

## 💡 Why It Matters

This isn't another AI news scraper. It's a personal intelligence tool that shows what's worth building, not just reading.

- 🔍 **40+ Premium Sources**: Research labs, AI thinkers' blogs, newsletters, trending repos
- 🤖 **Sequential Agent Pipeline**: 4 specialized agents working in a defined workflow
- 🎯 **Builder-focused Scoring**: Prioritizes agent systems, RAG, and practical implementations
- 🛠️ **Actionable Projects**: 30-60 minute builds with step-by-step instructions
- ⏰ **Fresh Content Only**: 30-day filter ensures everything is current
- 📊 **Notion Integration**: Full pages with formatted briefs and project details
- 🎖️ **Relevance Engine**: Scores what you can actually build today vs. just read about

## 🚀 Setup

### Prerequisites

- Python 3.8+
- OpenRouter API account
- Notion API integration

### Installation

1. Clone this repository:
```bash
git clone https://github.com/morhogeg/ai-strategy-brief.git
cd ai-strategy-brief
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
   • Name (must be the title column)
   • Date (type: Date)
3. Share the database with your integration
4. Copy the database ID from the URL and add to `.env`

## 🏃 Usage

Run the strategy brief generator:
```bash
python crew_strategy_brief.py
```

The system will:
1. Fetch the latest AI updates
2. Process them through the multi-agent system
3. Generate a markdown brief
4. Push to your Notion database with full page content

## 📁 Project Structure

```
ai-strategy-brief/
├── crew_strategy_brief.py     # Main orchestrator with CrewAI agents
├── ai_website_scraper.py      # Scrapes 23 high-quality AI sources (research labs + thinkers)
├── data_collector.py          # Aggregates updates from all sources with 30-day filtering
├── llm_config.py             # OpenRouter LLM configuration (Mistral)
├── notion_integration.py      # Pushes formatted briefs to Notion with full pages
├── crew_linkedin_only.py      # Alternative LinkedIn-focused workflow (deprecated)
├── linkedin_scraper.py        # LinkedIn post scraper (deprecated due to blocking)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── .env                      # Environment variables (not in repo)
```

## ⚙️ Customization

### Agent Personalities

Modify agent backstories and goals in `crew_strategy_brief.py` to match your interests:
- Signal Hunter: Focus areas for finding updates
- Relevance Scorer: Scoring criteria for relevance
- Action Generator: Types of projects to create
- Brief Editor: Formatting preferences

### Data Sources

The system aggregates from multiple sources:
- **AI Research Blogs**: `ai_website_scraper.py` contains 23 high-quality sources
- **Newsletters**: `data_collector.py` includes top AI newsletters  
- **Social/Community**: Hacker News AI discussions and GitHub trending
- **Famous AI Thinkers**: Personal blogs from Andrej Karpathy, Swyx, Benedict Evans, and others

To modify sources, edit the respective files based on your interests.

## 🔧 Troubleshooting

### OpenRouter Configuration
- Uses `mistralai/mistral-small-3.2-24b-instruct:free` model
- Free tier has rate limits - add credits if you hit limits
- Ensure your API key is configured for the specific model you want to use
- Some free models require adding provider-specific API keys

### Missing Links
The system only uses real URLs from source data. If links are missing, check that the source actually provided them.

### Notion Errors
- Ensure your database ID is correct (not a page ID)
- Verify the integration has access to your database
- Check that required properties exist in your database

## 📄 License

MIT License - see LICENSE file for details

## 📚 Learning & Inspiration

This project demonstrates several key concepts:
- **Multi-agent orchestration** with CrewAI
- **Real-time data aggregation** from diverse sources
- **Intelligent content filtering** and relevance scoring
- **Production-ready error handling** and fallbacks
- **API integration** (OpenRouter, Notion, GitHub, RSS)

Feel free to study the code and build your own version tailored to your specific needs and interests!

## 🤝 Contributing

While I kindly ask not to fork this specific repository, I'm happy to discuss the architecture and implementation details. Feel free to reach out if you're building something similar!