from crewai import Agent, Task, Crew
from llm_config import get_openrouter_llm
from data_collector import get_real_ai_updates
from notion_integration import push_to_notion
from datetime import datetime
import json

# Initialize OpenRouter LLM
try:
    openrouter_llm = get_openrouter_llm()
    print("✅ OpenRouter LLM initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize OpenRouter LLM: {e}")
    exit(1)

# Fetch real AI updates
print("Fetching real AI updates...")
real_updates = get_real_ai_updates()
print(f"Found {len(real_updates)} updates")

# Limit to top 15 updates to keep context manageable
real_updates = real_updates[:15]
print(f"Using top {len(real_updates)} updates for analysis")

# Format updates into context text for Signal Hunter
context_text = "Here are today's top AI updates from various sources:\n\n"
for i, update in enumerate(real_updates, 1):
    # Handle different title fields for different types  
    title = update.get('title', update.get('name', 'No title'))
    context_text += f"{i}. [{update['type'].upper()}] {update['source']}: {title}\n"
    if update['type'] == 'newsletter' and 'summary' in update:
        context_text += f"   Summary: {update['summary'][:150]}...\n"
    elif update['type'] == 'news' and 'points' in update:
        context_text += f"   Points: {update['points']}\n"
    elif update['type'] == 'repo' and 'description' in update:
        context_text += f"   Description: {update['description'][:150]}...\n"
        if 'stars' in update:
            context_text += f"   Stars: {update['stars']}\n"
    context_text += f"   Link: {update['link']}\n\n"

# Define agents
signal_hunter = Agent(
    role="Signal Hunter",
    goal="Find the top 5 AI updates specifically about agentic systems, multi-agent frameworks, RAG implementations, and tools I can build with today",
    backstory="""You are a developer-focused AI analyst who prioritizes ACTIONABLE updates about agent systems and RAG.
    You specifically look for:
    - Multi-agent frameworks and orchestration tools (like CrewAI, AutoGen, LangGraph)
    - RAG systems and vector database implementations
    - Agent memory systems and tool-use patterns
    - Real code examples and tutorials for building agents
    - Claude, GPT, and LLM integration patterns
    You IGNORE: general AI news, funding announcements, opinion pieces, or anything without code/implementation details.
    You love: GitHub repos with working examples, new agent libraries, practical tutorials, and tools that can be installed today.
    CRITICAL: You NEVER make up or invent URLs. You only report what actually exists in the data provided to you.""",
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm
)

relevance_scorer = Agent(
    role="Relevance Scorer",
    goal="Score updates based on how well they help me build agent systems, learn CrewAI/LangChain, and create practical AI tools",
    backstory="""You evaluate AI updates through the lens of a hands-on builder who uses Claude Code daily and wants to master agentic systems.
    
    Your scoring criteria (1-10):
    10: CrewAI/LangChain tutorial or template I can build TODAY
    9: Multi-agent system with code I can fork and modify
    8: RAG implementation or vector DB setup I can replicate
    7: Agent tool/memory pattern I can add to my projects
    6: Claude/LLM integration technique worth trying
    5: Interesting agent architecture to study later
    3-4: General AI tool that might be useful someday
    1-2: Theory without practical implementation
    
    You VALUE: working code, step-by-step tutorials, agent design patterns, integration examples
    You PENALIZE: vague announcements, closed-source tools, purely theoretical papers""",
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm
)

action_generator = Agent(
    role="Action Generator",
    goal="Create hands-on learning tasks where I build something practical using the new agent/RAG concepts discovered today",
    backstory="""You're a learn-by-doing coach who ALWAYS suggests building projects, not just reading.
    
    You understand that I:
    - Learn best by building things I'll actually use
    - Already use Claude Code extensively  
    - Want to master CrewAI, LangChain, and agent orchestration
    - Prefer practical tools over theoretical knowledge
    
    Your actions MUST be:
    - BUILD something specific (not just "explore" or "read")
    - Include exact commands to run (git clone, pip install, etc.)
    - Result in working code I can extend
    - Connect to my daily workflow (enhance Claude Code usage, automate tasks, build useful agents)
    - Take 30-60 minutes of hands-on coding
    
    Good action: "Build a CrewAI agent that summarizes your GitHub notifications"
    Bad action: "Read about agent architectures"
    
    Always frame learning as building something I'll use tomorrow.""",
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm
)

editor = Agent(
    role="Brief Editor",
    goal="Compile a daily brief focused on building agent systems, with clear next steps for hands-on learning",
    backstory="""You're a technical editor who understands developers learn by doing.
    
    You structure the brief to be:
    - Scannable in 2 minutes over morning coffee
    - Focused on BUILDABLE agent/RAG projects
    - Clear about what I'll create today
    - Honest about time investment (30-60 min sessions)
    
    You emphasize:
    - Working code and git repos I can clone
    - How each update relates to CrewAI/LangChain/Claude
    - Practical outcomes ("You'll have a working X that does Y")
    - Connection to my interests (agent systems, RAG, automation)
    
    You skip fluff and get straight to "here's what you can build today".
    CRITICAL: You NEVER modify URLs - you copy them EXACTLY as provided by other agents.""",
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm
)

# Define tasks with real data context
task1 = Task(
    description=f"""Find UP TO 5 MOST BUILDABLE agent/RAG updates from today's data.
    
    CRITICAL RULES:
    - Only report updates that ACTUALLY EXIST in the provided data below
    - If fewer than 5 updates meet the criteria, report only the ones that do
    - NEVER create fake entries or URLs that don't exist in the source data
    - Every link must be copied EXACTLY from the source data
    
    STRICT CRITERIA - Only select updates that have:
    1. Working code or GitHub repo I can clone
    2. Focus on agent systems, CrewAI, LangChain, or RAG
    3. Something I can build/run in under 60 minutes
    4. Practical application (not just demos)
    
    PRIORITIZE (in order):
    1. CrewAI/LangChain tutorials or templates (40%)
    2. Multi-agent system examples with code (30%)
    3. RAG implementations I can adapt (20%)
    4. Claude/LLM integration patterns (10%)
    
    For each selection provide:
    - Title and source  
    - One line: "Build a [WHAT] that [DOES WHAT]"
    - Link: USE THE EXACT ORIGINAL LINK from the context data above
    - Has code: Yes/No
    
    Real updates to analyze:
    {context_text}
    
    Remember: I want to BUILD, not just read. If it doesn't have code, it's not worth selecting.
    IMPORTANT: You MUST use the exact original links provided in the context data above - do NOT create or modify any URLs.""",
    expected_output="5 buildable agent/RAG projects with implementation details",
    agent=signal_hunter
)

task2 = Task(
    description="""Score each update based on how it helps me BUILD agent systems and level up my CrewAI/LangChain skills.
    
    USE THIS EXACT SCORING:
    10: CrewAI multi-agent template I can customize today
    9: LangChain agent with tools/memory I can fork
    8: RAG system with vector DB I can deploy
    7: Agent coordination pattern I can implement
    6: Claude API integration I haven't tried
    5: Useful utility for agent development
    4: Interesting architecture to study
    3: General AI tool (not agent-focused)
    1-2: No practical building opportunity
    
    For each update:
    - Score: [1-10]
    - Why this score: "Can build [SPECIFIC THING] to [ACHIEVE WHAT]"
    - Learning tags: [crewai] [langchain] [rag] [agents] [memory] [tools] [claude]
    - Time to first working version: [X minutes]""",
    expected_output="Scored list focused on buildable learning opportunities",
    agent=relevance_scorer,
    context=[task1]
)

task3 = Task(
    description="""Create 1-2 BUILD projects that teach me agent/RAG concepts through hands-on coding.
    
    REQUIREMENTS for each project:
    1. Must result in WORKING CODE I'll use again
    2. Teaches CrewAI, LangChain, or RAG patterns
    3. Enhances my Claude Code workflow OR automates a daily task
    4. Can reach "v1 working" in 45-60 minutes
    
    FORMAT each project as:
    
    Project: "Build a [SPECIFIC TOOL]"
    What you'll build: [2-3 sentences about the working system]
    What you'll learn: [Specific CrewAI/LangChain concepts]
    
    Step 1: Clone/Install
    ```bash
    git clone [repo] OR pip install [packages]
    ```
    
    Step 2: Quick customization
    - Change X to do Y for your use case
    - Add your API keys to .env
    
    Step 3: Run it
    ```bash
    python [script.py]
    ```
    
    Time: [X minutes to working version]
    Next steps: [How to extend it tomorrow]
    
    GOOD: "Build a CrewAI team that reviews your code PRs"
    BAD: "Learn about agent architectures"
    
    Remember: I learn by BUILDING things I'll USE.""",
    expected_output="1-2 concrete build projects with step-by-step instructions",
    agent=action_generator,
    context=[task1, task2]
)

task4 = Task(
    description=f"""Create a final strategy brief following this EXACT template:

# AI Strategy Brief

🗓️ Date: {datetime.now().strftime('%Y-%m-%d')}

⸻

*A curated daily snapshot of real-world AI signals and actions — personalized for a fast-learning founder.*

⸻

## 🔍 **Signal Hunter**
*Scanning real-world AI sources to surface the most significant updates of the day.*

### 📌 Top 5 AI Signals

1. **[Title]**
   • Source: [source name]
   • Why it matters: [1-line explanation]
   • Link: [original URL or resource]

2. **[Title]**
   • Source: [source name]
   • Why it matters: [1-line explanation]
   • Link: [original URL or resource]

3. **[Title]**
   • Source: [source name]
   • Why it matters: [1-line explanation]
   • Link: [original URL or resource]

4. **[Title]**
   • Source: [source name]
   • Why it matters: [1-line explanation]
   • Link: [original URL or resource]

5. **[Title]**
   • Source: [source name]
   • Why it matters: [1-line explanation]
   • Link: [original URL or resource]

⸻

## 🎯 **Relevance Scorer**
*Evaluating how useful each signal is to a fast-learning AI product founder.*

### 🎯 Relevance Summary

**[Title 1]**
• Relevance Score: [1–10]
• Tags: [tag1], [tag2]
• Explanation: [1–2 sentences]

**[Title 2]**
• Relevance Score: [1–10]
• Tags: [tag1], [tag2]
• Explanation: [1–2 sentences]

**[Title 3]**
• Relevance Score: [1–10]
• Tags: [tag1], [tag2]
• Explanation: [1–2 sentences]

**[Title 4]**
• Relevance Score: [1–10]
• Tags: [tag1], [tag2]
• Explanation: [1–2 sentences]

**[Title 5]**
• Relevance Score: [1–10]
• Tags: [tag1], [tag2]
• Explanation: [1–2 sentences]

⸻

## 🛠️ **Action Generator**
*Translating insights into specific, focused, actionable steps.*

### ✅ Today's Suggested Actions

✅ **[Action Title 1]**
• Time Estimate: [xx minutes]
• Expected Outcome: [what I'll learn or achieve]
• Link: [formatted as clickable Markdown link](url)
• Description: [concise instruction or guidance]

✅ **[Action Title 2]**
• Time Estimate: [xx minutes]
• Expected Outcome: [what I'll learn or achieve]
• Link: [formatted as clickable Markdown link](url)
• Description: [concise instruction or guidance]

⸻

## 📊 **Source Tracker**
*Showing which platforms were scanned and how much content was pulled from each.*

### 📊 Update Sources
• Newsletters processed: {len([u for u in real_updates if u['type'] == 'newsletter'])}
• Hacker News posts reviewed: {len([u for u in real_updates if u['type'] == 'news'])}
• GitHub repos reviewed: {len([u for u in real_updates if u['type'] == 'repo'])}

⸻

IMPORTANT: 
- Replace ALL placeholders like [Title], [source name], etc. with actual data
- Use EXACT URLs from the Signal Hunter - do NOT modify or create new URLs
- Format links as clickable Markdown: [link text](url) 
- Use bold for titles, bullet points for details
- NO TABLES, only clean formatted text
- EVERY signal MUST have its original link preserved exactly as provided""",
    expected_output="Polished markdown strategy brief ready for publication",
    agent=editor,
    context=[task1, task2, task3]
)

# Create crew
crew = Crew(
    agents=[signal_hunter, relevance_scorer, action_generator, editor],
    tasks=[task1, task2, task3, task4],
    verbose=True
)

# Run the crew
if __name__ == "__main__":
    print("\nStarting AI Strategy Brief generation...")
    print(f"Processing {len(real_updates)} real updates from today\n")
    
    try:
        result = crew.kickoff()
        
        # Save the result
        with open("strategy_brief.md", "w") as f:
            f.write(str(result))
        
        print("\n✅ Strategy brief saved to strategy_brief.md")
        
        # Push to Notion
        print("\n📤 Pushing to Notion...")
        push_to_notion()
        
    except Exception as e:
        print(f"\n❌ Error during crew execution: {e}")
        print("Check your OpenRouter API key and internet connection")
        
        # Create a fallback brief with the raw data
        fallback_brief = f"""# AI Strategy Brief
🗓️ Date: {datetime.now().strftime('%Y-%m-%d')}

## ⚠️ Note
This brief was generated from raw data due to LLM processing issues.

## 📊 Raw Updates Found Today
Total updates: {len(real_updates)}

{context_text}

---
*Generated by AI Strategy Brief System*
"""
        
        with open("strategy_brief_fallback.md", "w") as f:
            f.write(fallback_brief)
        
        print("📄 Fallback brief saved to strategy_brief_fallback.md")