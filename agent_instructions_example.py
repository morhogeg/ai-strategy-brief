# Example of controlling agent instructions in CrewAI

from crewai import Agent, Task, Crew
from llm_config import get_openrouter_llm

# Method 1: Control through Agent parameters
# ==========================================

signal_hunter = Agent(
    role="Signal Hunter",  # Short role name
    
    goal="Identify the top 5 most significant AI updates from today's real data",  # What they should achieve
    
    backstory="""You are an expert AI analyst with 10 years of experience tracking emerging technologies.
    You have a keen eye for distinguishing genuine breakthroughs from hype. You focus on:
    - Technical innovations that push boundaries
    - Practical tools developers can use today
    - Industry shifts that affect AI builders
    - Research with immediate applications
    You ignore: marketing fluff, minor updates, and purely theoretical work.""",  # Detailed personality/approach
    
    verbose=True,
    allow_delegation=False,
    llm=get_openrouter_llm(),
    
    # Additional parameters you can use:
    max_iter=3,  # Maximum iterations for the agent to refine its answer
    memory=True,  # Enable memory for the agent
    tools=[],  # Add specific tools the agent can use
    system_template="""You are a specialized AI analyst. Always:
    - Be concise and factual
    - Focus on technical merit over hype
    - Prioritize actionable insights""",  # System-level instructions
    
    execution_style="sequential",  # How the agent executes tasks
)

# Method 2: Control through Task descriptions
# ===========================================

task1 = Task(
    description="""Analyze the following real AI updates and select EXACTLY 5 updates.
    
    STRICT REQUIREMENTS:
    1. Only select updates that are genuinely significant (not just popular)
    2. Each selection must include:
       - Original title (exactly as provided)
       - Source name
       - A 15-20 word explanation of impact
    3. Prioritize in this order:
       - Tools/libraries developers can use immediately (40% weight)
       - Major model/algorithm breakthroughs (30% weight)
       - Industry trends affecting AI builders (20% weight)
       - Significant research findings (10% weight)
    
    FORMAT YOUR OUTPUT EXACTLY LIKE THIS:
    1. [Title]
       Source: [Source Name]
       Impact: [15-20 word explanation]
    
    Real updates to analyze:
    {context_text}
    
    Remember: Quality over popularity. A 3-point HN post about a new RAG technique
    beats a 100-point post about AI replacing jobs.""",
    
    expected_output="List of exactly 5 significant AI updates with title, source, and impact explanation",
    
    agent=signal_hunter,
    
    # Additional task parameters:
    async_execution=False,  # Run synchronously
    context=[],  # Previous tasks to use as context
    tools=[],  # Specific tools for this task
    output_json=None,  # Expected JSON schema for structured output
    output_file=None,  # Save output to file
    human_input=False,  # Require human input
    
    # You can also add callbacks:
    callback=None,  # Function to call when task completes
)

# Method 3: Control through Crew configuration
# ============================================

crew = Crew(
    agents=[signal_hunter, relevance_scorer, action_generator, editor],
    tasks=[task1, task2, task3, task4],
    
    # Crew-level controls:
    process="sequential",  # or "hierarchical"
    verbose=True,
    memory=True,  # Enable crew memory
    cache=True,  # Cache results
    max_rpm=100,  # Rate limiting
    share_crew=False,  # Share crew performance data
    
    # Advanced: Custom prompts for the whole crew
    manager_llm=get_openrouter_llm(),  # For hierarchical process
    function_calling_llm=get_openrouter_llm(),  # For tool calls
    
    # Callbacks for monitoring
    task_callback=None,  # Called after each task
    step_callback=None,  # Called after each step
)

# Method 4: Dynamic instruction injection
# =======================================

def create_contextual_agent(user_preferences):
    """Create an agent with dynamic instructions based on user preferences"""
    
    focus_areas = user_preferences.get('focus_areas', ['agents', 'rag', 'llms'])
    time_budget = user_preferences.get('time_budget', 60)
    
    return Agent(
        role="Personalized Action Generator",
        goal=f"Generate actions that take less than {time_budget} minutes",
        backstory=f"""You create actions specifically for someone interested in: {', '.join(focus_areas)}.
        You understand their time constraints and learning style.
        Every suggestion must be immediately actionable and high-impact.""",
        llm=get_openrouter_llm()
    )

# Method 5: Using system prompts and templates
# ============================================

relevance_scorer_with_rubric = Agent(
    role="Relevance Scorer",
    goal="Score updates based on a strict rubric",
    backstory="You are a systematic evaluator who follows precise scoring criteria.",
    
    # Add a detailed system template
    system_template="""You are a Relevance Scorer. Use this EXACT scoring rubric:

    10 points: Directly applicable to current project, can implement today
    8-9 points: Highly relevant tool/technique, worth exploring this week  
    6-7 points: Interesting approach that could influence future decisions
    4-5 points: Good to know, but not immediately actionable
    2-3 points: Tangentially related, bookmark for later
    1 point: Not relevant to our tech stack or goals
    
    ALWAYS justify your score with specific reasons tied to:
    - Technical fit with our stack
    - Time to implement
    - Potential impact
    - Learning value""",
    
    llm=get_openrouter_llm()
)

# Method 6: Pre and post-processing instructions
# ==============================================

class CustomSignalHunter(Agent):
    """Extend Agent class for more control"""
    
    def execute_task(self, task, context=None, tools=None):
        # Pre-process the task
        task.description = self._add_timestamp_requirement(task.description)
        
        # Execute normally
        result = super().execute_task(task, context, tools)
        
        # Post-process the result
        return self._format_result(result)
    
    def _add_timestamp_requirement(self, description):
        return description + "\n\nIMPORTANT: Include the current timestamp in your response."
    
    def _format_result(self, result):
        # Ensure consistent formatting
        return result.strip()

# Method 7: Using callbacks for dynamic control
# =============================================

def task_completion_callback(task_output):
    """Adjust next agent's instructions based on previous output"""
    if "no significant updates" in task_output.raw_output.lower():
        # Modify next task's description
        task_output.task.crew.tasks[1].description += "\n\nNOTE: Few significant updates today. Be more lenient with scoring."
    return task_output

task_with_callback = Task(
    description="Find significant updates",
    expected_output="List of updates",
    agent=signal_hunter,
    callback=task_completion_callback
)

# Method 8: Environment variables for instructions
# ================================================

import os

# Set environment variables for different modes
os.environ['AI_BRIEF_MODE'] = 'detailed'  # or 'summary'
os.environ['AI_BRIEF_FOCUS'] = 'security,agents,rag'

# Agents can read these in their backstory
dynamic_agent = Agent(
    role="Adaptive Analyst",
    goal="Analyze based on current configuration",
    backstory=f"""You adapt your analysis based on the mode: {os.getenv('AI_BRIEF_MODE', 'standard')}.
    Current focus areas: {os.getenv('AI_BRIEF_FOCUS', 'general')}.""",
    llm=get_openrouter_llm()
)

# Example: Putting it all together
# ================================

if __name__ == "__main__":
    # You can test individual agents
    test_task = Task(
        description="Test the signal hunter with sample data",
        expected_output="5 selected signals",
        agent=signal_hunter
    )
    
    # Or run specific instructions
    result = signal_hunter.execute(
        task="Find the top AI coding tool from today's updates",
        context="Focus only on tools that generate code"
    )
    
    print(result)