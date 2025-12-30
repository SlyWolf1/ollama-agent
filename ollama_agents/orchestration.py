"""
Advanced agent orchestration patterns.
Provides reusable patterns for agent coordination.
"""

from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
from .agent import Agent
from .logger import get_logger

logger = get_logger()


class OrchestrationPattern(Enum):
    """Types of orchestration patterns"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    CONSENSUS = "consensus"
    DEBATE = "debate"
    PIPELINE = "pipeline"


@dataclass
class OrchestrationResult:
    """Result from orchestration"""
    pattern: OrchestrationPattern
    results: List[Dict[str, Any]]
    final_result: Optional[str] = None
    metadata: Dict[str, Any] = None


class AgentOrchestrator:
    """Orchestrates multiple agents using various patterns"""
    
    def __init__(self, agents: List[Agent]):
        self.agents = agents
        logger.info(f"🎭 Orchestrator created with {len(agents)} agents")
    
    def sequential(self, query: str, agent_order: Optional[List[str]] = None) -> OrchestrationResult:
        """
        Execute agents sequentially, passing output to next agent.
        
        Args:
            query: Initial query
            agent_order: Optional list of agent names in order
        """
        logger.info(f"🔄 Sequential orchestration: {query[:50]}...")
        
        agents = self._order_agents(agent_order) if agent_order else self.agents
        results = []
        current_input = query
        
        for agent in agents:
            logger.debug(f"  → Running {agent.name}")
            response = agent.chat(current_input)
            results.append({
                "agent": agent.name,
                "input": current_input,
                "output": response.get("content", "")
            })
            current_input = response.get("content", "")
        
        return OrchestrationResult(
            pattern=OrchestrationPattern.SEQUENTIAL,
            results=results,
            final_result=current_input,
            metadata={"agent_count": len(agents)}
        )
    
    def parallel(self, query: str, aggregator: Optional[Callable] = None) -> OrchestrationResult:
        """
        Execute all agents in parallel and aggregate results.
        
        Args:
            query: Query to send to all agents
            aggregator: Optional function to aggregate results
        """
        logger.info(f"⚡ Parallel orchestration: {query[:50]}...")
        
        results = []
        for agent in self.agents:
            logger.debug(f"  → Running {agent.name}")
            response = agent.chat(query)
            results.append({
                "agent": agent.name,
                "input": query,
                "output": response.get("content", "")
            })
        
        # Aggregate results
        if aggregator:
            final_result = aggregator(results)
        else:
            final_result = self._default_aggregator(results)
        
        return OrchestrationResult(
            pattern=OrchestrationPattern.PARALLEL,
            results=results,
            final_result=final_result,
            metadata={"agent_count": len(self.agents)}
        )
    
    def hierarchical(
        self,
        query: str,
        coordinator_name: str,
        worker_names: List[str]
    ) -> OrchestrationResult:
        """
        Hierarchical pattern: coordinator delegates to workers.
        
        Args:
            query: Initial query
            coordinator_name: Name of coordinator agent
            worker_names: Names of worker agents
        """
        logger.info(f"🏛️ Hierarchical orchestration: {query[:50]}...")
        
        coordinator = self._get_agent(coordinator_name)
        workers = [self._get_agent(name) for name in worker_names]
        
        # Coordinator plans the work
        planning_prompt = f"""
        Task: {query}
        
        Available workers: {', '.join(worker_names)}
        
        Decide which workers should handle which parts of the task.
        Respond with a JSON list of tasks for each worker.
        """
        
        plan_response = coordinator.chat(planning_prompt)
        logger.debug(f"  📋 Plan: {plan_response.get('content', '')[:100]}...")
        
        # Workers execute
        results = [{"agent": coordinator_name, "role": "coordinator", "output": plan_response.get("content", "")}]
        
        for worker in workers:
            worker_response = worker.chat(f"Based on this plan, complete your part: {plan_response.get('content', '')}")
            results.append({
                "agent": worker.name,
                "role": "worker",
                "output": worker_response.get("content", "")
            })
        
        # Coordinator synthesizes
        synthesis_prompt = f"Synthesize these results into a final answer: {results}"
        final_response = coordinator.chat(synthesis_prompt)
        
        return OrchestrationResult(
            pattern=OrchestrationPattern.HIERARCHICAL,
            results=results,
            final_result=final_response.get("content", ""),
            metadata={"coordinator": coordinator_name, "workers": worker_names}
        )
    
    def consensus(self, query: str, threshold: float = 0.5) -> OrchestrationResult:
        """
        Agents vote on the answer, consensus is reached by majority.
        
        Args:
            query: Query for all agents
            threshold: Consensus threshold (0.0 to 1.0)
        """
        logger.info(f"🗳️ Consensus orchestration: {query[:50]}...")
        
        results = []
        answers = []
        
        for agent in self.agents:
            response = agent.chat(query)
            answer = response.get("content", "")
            results.append({
                "agent": agent.name,
                "answer": answer
            })
            answers.append(answer)
        
        # Simple consensus: most common answer
        from collections import Counter
        answer_counts = Counter(answers)
        most_common = answer_counts.most_common(1)[0]
        consensus_reached = most_common[1] / len(answers) >= threshold
        
        final_result = most_common[0] if consensus_reached else "No consensus reached"
        
        return OrchestrationResult(
            pattern=OrchestrationPattern.CONSENSUS,
            results=results,
            final_result=final_result,
            metadata={
                "consensus_reached": consensus_reached,
                "vote_distribution": dict(answer_counts)
            }
        )
    
    def debate(self, query: str, rounds: int = 2) -> OrchestrationResult:
        """
        Agents debate to reach best answer through argumentation.
        
        Args:
            query: Topic to debate
            rounds: Number of debate rounds
        """
        logger.info(f"💬 Debate orchestration: {query[:50]}... ({rounds} rounds)")
        
        results = []
        conversation = []
        
        for round_num in range(rounds):
            logger.debug(f"  🔄 Round {round_num + 1}")
            
            for agent in self.agents:
                # Agent sees previous conversation
                context = f"Query: {query}\n\nPrevious arguments:\n" + "\n".join(conversation[-6:])
                response = agent.chat(context)
                argument = response.get("content", "")
                
                conversation.append(f"{agent.name}: {argument}")
                results.append({
                    "agent": agent.name,
                    "round": round_num + 1,
                    "argument": argument
                })
        
        # Final synthesis by first agent
        synthesis_prompt = f"After this debate, what is the best answer?\n\n{chr(10).join(conversation)}"
        final_response = self.agents[0].chat(synthesis_prompt)
        
        return OrchestrationResult(
            pattern=OrchestrationPattern.DEBATE,
            results=results,
            final_result=final_response.get("content", ""),
            metadata={"rounds": rounds, "total_arguments": len(results)}
        )
    
    def pipeline(self, query: str, pipeline: List[Dict[str, Any]]) -> OrchestrationResult:
        """
        Execute agents in a pipeline with transformations.
        
        Args:
            query: Initial input
            pipeline: List of pipeline stages [{"agent": name, "transform": fn}, ...]
        """
        logger.info(f"🔧 Pipeline orchestration: {len(pipeline)} stages")
        
        results = []
        current_input = query
        
        for stage in pipeline:
            agent_name = stage.get("agent")
            transform = stage.get("transform")
            
            agent = self._get_agent(agent_name)
            response = agent.chat(current_input)
            output = response.get("content", "")
            
            if transform:
                output = transform(output)
            
            results.append({
                "agent": agent_name,
                "input": current_input,
                "output": output,
                "transformed": transform is not None
            })
            
            current_input = output
        
        return OrchestrationResult(
            pattern=OrchestrationPattern.PIPELINE,
            results=results,
            final_result=current_input,
            metadata={"stages": len(pipeline)}
        )
    
    # Helper methods
    def _order_agents(self, order: List[str]) -> List[Agent]:
        """Order agents by name list"""
        ordered = []
        for name in order:
            agent = self._get_agent(name)
            if agent:
                ordered.append(agent)
        return ordered
    
    def _get_agent(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    
    def _default_aggregator(self, results: List[Dict]) -> str:
        """Default aggregation: concatenate all results"""
        return "\n\n".join([
            f"**{r['agent']}**: {r['output']}"
            for r in results
        ])


# Convenience function
def orchestrate(
    agents: List[Agent],
    query: str,
    pattern: OrchestrationPattern = OrchestrationPattern.SEQUENTIAL,
    **kwargs
) -> OrchestrationResult:
    """
    Orchestrate agents with a specific pattern.
    
    Args:
        agents: List of agents
        query: Query or task
        pattern: Orchestration pattern to use
        **kwargs: Pattern-specific arguments
    """
    orchestrator = AgentOrchestrator(agents)
    
    if pattern == OrchestrationPattern.SEQUENTIAL:
        return orchestrator.sequential(query, **kwargs)
    elif pattern == OrchestrationPattern.PARALLEL:
        return orchestrator.parallel(query, **kwargs)
    elif pattern == OrchestrationPattern.HIERARCHICAL:
        return orchestrator.hierarchical(query, **kwargs)
    elif pattern == OrchestrationPattern.CONSENSUS:
        return orchestrator.consensus(query, **kwargs)
    elif pattern == OrchestrationPattern.DEBATE:
        return orchestrator.debate(query, **kwargs)
    elif pattern == OrchestrationPattern.PIPELINE:
        return orchestrator.pipeline(query, **kwargs)
    else:
        raise ValueError(f"Unknown pattern: {pattern}")
