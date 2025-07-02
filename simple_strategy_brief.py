#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv
from data_collector import get_real_ai_updates
from datetime import datetime

load_dotenv()

class SimpleAIAgent:
    def __init__(self, role, goal, backstory):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
    def call_llm(self, prompt):
        """Call OpenRouter API directly"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = f"You are a {self.role}. {self.backstory}\n\nGoal: {self.goal}"
        
        data = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Connection error: {e}"

def main():
    print("🚀 Starting AI Strategy Brief generation...")
    
    # Fetch real AI updates
    print("📡 Fetching real AI updates...")
    real_updates = get_real_ai_updates()
    print(f"Found {len(real_updates)} updates")
    
    # Limit to top 10 updates for manageable processing
    real_updates = real_updates[:10]
    print(f"Using top {len(real_updates)} updates for analysis")
    
    # Format updates for analysis
    context_text = "Here are today's top AI updates:\n\n"
    for i, update in enumerate(real_updates, 1):
        title = update.get('title', update.get('name', 'No title'))
        context_text += f"{i}. [{update['type'].upper()}] {update['source']}: {title}\n"
        if update['type'] == 'newsletter' and 'summary' in update:
            context_text += f"   Summary: {update['summary'][:150]}...\n"
        elif update['type'] == 'news' and 'points' in update:
            context_text += f"   Points: {update['points']}\n"
        elif update['type'] == 'repo' and 'description' in update:
            context_text += f"   Description: {update['description'][:150]}...\n"
        context_text += f"   Link: {update['link']}\n\n"
    
    # Create agents
    signal_hunter = SimpleAIAgent(
        role="Signal Hunter",
        goal="Identify the top 5 most significant AI updates from today's data",
        backstory="You are an expert AI analyst who identifies breakthrough technologies, industry shifts, and practical advances in AI agents, RAG systems, and LLMs."
    )
    
    relevance_scorer = SimpleAIAgent(
        role="Relevance Scorer", 
        goal="Score updates based on relevance to a founder focused on AI agents, RAG, and LLM workflows",
        backstory="You understand what matters to technical founders building AI products. You score based on applicability, learning value, and competitive advantage."
    )
    
    action_generator = SimpleAIAgent(
        role="Action Generator",
        goal="Generate 1-2 specific actionable steps based on the most relevant updates", 
        backstory="You translate AI developments into concrete 15-60 minute actions that provide real value."
    )
    
    editor = SimpleAIAgent(
        role="Brief Editor",
        goal="Compile insights into a clean, well-formatted strategy brief",
        backstory="You create concise, scannable briefs that highlight what matters most for busy founders."
    )
    
    # Step 1: Signal Hunter - Find top 5 updates
    print("🔍 Step 1: Signal Hunter analyzing updates...")
    hunter_prompt = f"""Analyze these AI updates and select the 5 most significant ones.
For each, provide:
- Original title and source
- One-line explanation of why it matters

{context_text}

Focus on breakthrough technologies, industry shifts, and advances in AI agents/RAG/LLMs."""
    
    top_signals = signal_hunter.call_llm(hunter_prompt)
    print("✅ Top signals identified")
    
    # Step 2: Relevance Scorer - Score the updates
    print("📊 Step 2: Relevance Scorer evaluating...")
    scorer_prompt = f"""Score these 5 selected updates on relevance (1-10 scale) for a founder focused on:
- AI agents and multi-agent systems
- RAG implementations  
- LLM workflows and prompt engineering
- Fast learning and staying ahead

For each update provide:
- Relevance score (1-10)
- 1-2 sentence explanation
- Tags: [agents] [rag] [llm] [tooling] [research] [business]

Here are the selected updates:
{top_signals}"""
    
    relevance_scores = relevance_scorer.call_llm(scorer_prompt)
    print("✅ Relevance scoring completed")
    
    # Step 3: Action Generator - Create actionable steps
    print("⚡ Step 3: Action Generator creating actions...")
    action_prompt = f"""Based on these scored updates, suggest 1-2 specific actions for this week.

Actions should be:
- Concrete and specific (not "stay informed" but "read X paper" or "try Y tool")
- Achievable in 15-60 minutes
- Directly related to the highest-scoring updates
- Focused on learning, experimenting, or implementing

Format each action as:
- Action title
- Time estimate  
- Expected outcome
- Link to resource

Scored updates:
{relevance_scores}"""
    
    suggested_actions = action_generator.call_llm(action_prompt)
    print("✅ Actions generated")
    
    # Step 4: Editor - Create final brief
    print("📝 Step 4: Editor compiling final brief...")
    editor_prompt = f"""Create a final strategy brief in clean Markdown format with these sections:

# AI Strategy Brief
🗓️ Date: {datetime.now().strftime('%Y-%m-%d')}

## 📌 Top 5 AI Signals
[List the 5 updates with sources and why they matter]

## 🎯 Relevance Summary  
[Show scores, explanations, and tags in a clean format]

## 🛠️ Suggested Actions
[Present the 1-2 actions with all details]

## 📊 Update Sources
- Total updates analyzed: {len(real_updates)}
- Newsletters: {len([u for u in real_updates if u['type'] == 'newsletter'])}
- HN posts: {len([u for u in real_updates if u['type'] == 'news'])}
- GitHub repos: {len([u for u in real_updates if u['type'] == 'repo'])}

Make it clean, scannable, and actionable.

Content to compile:

TOP SIGNALS:
{top_signals}

RELEVANCE SCORES:
{relevance_scores}

SUGGESTED ACTIONS:
{suggested_actions}"""
    
    final_brief = editor.call_llm(editor_prompt)
    print("✅ Final brief compiled")
    
    # Save the result
    with open("strategy_brief.md", "w") as f:
        f.write(final_brief)
    
    print(f"\n🎉 Strategy brief saved to strategy_brief.md")
    print(f"📊 Processed {len(real_updates)} updates through 4-agent pipeline")

if __name__ == "__main__":
    main()