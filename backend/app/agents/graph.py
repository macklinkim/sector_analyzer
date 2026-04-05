# backend/app/agents/graph.py
from langgraph.graph import StateGraph, END

from app.agents.state import MarketAnalysisState
from app.agents.data_agent import data_agent_node
from app.agents.news_agent import news_agent_node
from app.agents.analyst_agent import analyst_agent_node


def build_graph():
    """Build the LangGraph pipeline: Data Agent -> News Agent -> Analyst Agent."""
    graph = StateGraph(MarketAnalysisState)

    graph.add_node("data_agent", data_agent_node)
    graph.add_node("news_agent", news_agent_node)
    graph.add_node("analyst_agent", analyst_agent_node)

    graph.set_entry_point("data_agent")
    graph.add_edge("data_agent", "news_agent")
    graph.add_edge("news_agent", "analyst_agent")
    graph.add_edge("analyst_agent", END)

    return graph.compile()
