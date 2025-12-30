#!/usr/bin/env python3
"""
Direct test of collaborative agents handoff
"""
import sys
sys.path.insert(0, '/Users/brianmanda/PycharmProjects/library')

from examples.collaborative_agents_example import create_file_search_agent, create_triage_agent, create_web_search_agent
from ollama_agents import LogLevel, set_global_log_level

set_global_log_level(LogLevel.INFO)

print("=" * 80)
print("TESTING COLLABORATIVE AGENTS - FULL RESPONSE CHAIN")
print("=" * 80)
print()

# Create agents
print("Creating agents...")
file_agent = create_file_search_agent()
web_agent = create_web_search_agent()
triage_agent = create_triage_agent(file_agent, web_agent)
print("✅ Agents created")
print()

# Test query that will trigger file search (which will fail if qdrant not installed)
query = "Search for information about TFG job shadowing program"
print(f"Query: {query}")
print()
print("Processing...")
print()

response = triage_agent.chat(query)

print("=" * 80)
print("FINAL RESPONSE TO USER:")
print("=" * 80)
print(response['content'])
print()
print("=" * 80)
