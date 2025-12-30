"""
Examples of using advanced orchestration patterns.
"""

from ollama_agents import Agent, orchestrate, OrchestrationPattern, AgentOrchestrator

# Create some specialized agents
researcher = Agent(
    name="researcher",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a research expert. Provide detailed, well-researched information."
)

analyst = Agent(
    name="analyst",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are an analyst. Analyze information critically and provide insights."
)

writer = Agent(
    name="writer",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a creative writer. Transform information into engaging content."
)

# Example 1: Sequential orchestration
print("=" * 80)
print("Example 1: Sequential Orchestration")
print("=" * 80)

result = orchestrate(
    agents=[researcher, analyst, writer],
    query="What are the benefits of AI?",
    pattern=OrchestrationPattern.SEQUENTIAL
)

print(f"\nFinal result:\n{result.final_result}\n")
print(f"Metadata: {result.metadata}")

# Example 2: Parallel orchestration
print("\n" + "=" * 80)
print("Example 2: Parallel Orchestration")
print("=" * 80)

result = orchestrate(
    agents=[researcher, analyst, writer],
    query="Explain quantum computing in simple terms",
    pattern=OrchestrationPattern.PARALLEL
)

print(f"\nAggregated result:\n{result.final_result}\n")
print(f"Metadata: {result.metadata}")

# Example 3: Hierarchical orchestration
print("\n" + "=" * 80)
print("Example 3: Hierarchical Orchestration")
print("=" * 80)

coordinator = Agent(
    name="coordinator",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You coordinate other agents. Delegate tasks and synthesize results."
)

orchestrator = AgentOrchestrator([coordinator, researcher, analyst])

result = orchestrator.hierarchical(
    query="Create a comprehensive report on renewable energy",
    coordinator_name="coordinator",
    worker_names=["researcher", "analyst"]
)

print(f"\nFinal result:\n{result.final_result}\n")
print(f"Metadata: {result.metadata}")

# Example 4: Consensus orchestration
print("\n" + "=" * 80)
print("Example 4: Consensus Orchestration")
print("=" * 80)

# Create multiple agents with same task
agent1 = Agent(name="agent1", model="qwen2.5-coder:3b-instruct-q8_0", instructions="Answer questions accurately.")
agent2 = Agent(name="agent2", model="qwen2.5-coder:3b-instruct-q8_0", instructions="Answer questions accurately.")
agent3 = Agent(name="agent3", model="qwen2.5-coder:3b-instruct-q8_0", instructions="Answer questions accurately.")

orchestrator = AgentOrchestrator([agent1, agent2, agent3])

result = orchestrator.consensus(
    query="What is 2 + 2?",
    threshold=0.6
)

print(f"\nConsensus result:\n{result.final_result}\n")
print(f"Metadata: {result.metadata}")

# Example 5: Debate orchestration
print("\n" + "=" * 80)
print("Example 5: Debate Orchestration")
print("=" * 80)

optimist = Agent(
    name="optimist",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are optimistic and see the positive side of everything."
)

pessimist = Agent(
    name="pessimist",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are skeptical and see potential problems."
)

orchestrator = AgentOrchestrator([optimist, pessimist])

result = orchestrator.debate(
    query="Should companies adopt AI extensively?",
    rounds=2
)

print(f"\nDebate result:\n{result.final_result}\n")
print(f"Metadata: {result.metadata}")

# Example 6: Pipeline orchestration
print("\n" + "=" * 80)
print("Example 6: Pipeline Orchestration")
print("=" * 80)

# Define pipeline with transformations
pipeline = [
    {"agent": "researcher", "transform": lambda x: x[:500]},  # Truncate to 500 chars
    {"agent": "analyst", "transform": None},
    {"agent": "writer", "transform": lambda x: x.upper()}  # Convert to uppercase
]

orchestrator = AgentOrchestrator([researcher, analyst, writer])

result = orchestrator.pipeline(
    query="Explain machine learning",
    pipeline=pipeline
)

print(f"\nPipeline result:\n{result.final_result}\n")
print(f"Metadata: {result.metadata}")

print("\n" + "=" * 80)
print("✅ Orchestration examples complete!")
print("=" * 80)
