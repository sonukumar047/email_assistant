"""
Enhanced LangGraph workflow with parallel processing
"""
from langgraph.graph import StateGraph, END
from state import EmailState
from nodes import (
    classify_and_analyze_parallel,
    summarize_node,
    memory_node,
    generate_reply_node,
    decision_node
)
import logging

logger = logging.getLogger(__name__)

def create_email_workflow():
    """
    Create the enhanced LangGraph workflow with parallel processing
    
    Flow:
    1. classify_and_analyze (parallel: intent + sentiment)
    2. summarize (parallel with memory)
    3. memory (parallel with summarize)
    4. generate_reply (sequential, needs summary + memory)
    5. decision (sequential, needs all context)
    """
    # Initialize the graph
    workflow = StateGraph(EmailState)
    
    # Add nodes
    workflow.add_node("classify_and_analyze", classify_and_analyze_parallel)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("memory", memory_node)
    workflow.add_node("generate_reply", generate_reply_node)
    workflow.add_node("decision", decision_node)
    
    # Define the flow with parallel execution
    workflow.set_entry_point("classify_and_analyze")
    
    # After classification, run summarize and memory in parallel
    workflow.add_edge("classify_and_analyze", "summarize")
    workflow.add_edge("classify_and_analyze", "memory")
    
    # Both summarize and memory must complete before reply generation
    workflow.add_edge("summarize", "generate_reply")
    workflow.add_edge("memory", "generate_reply")
    
    # Decision is final step
    workflow.add_edge("generate_reply", "decision")
    workflow.add_edge("decision", END)
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("✓ Email workflow graph compiled with parallel execution")
    return app
