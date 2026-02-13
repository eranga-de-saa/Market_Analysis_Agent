from langgraph.graph import StateGraph, END

from src.classes.state import MarketAnalysisState
from src.nodes.context_research import context_research_node
from src.nodes.data_cleaning import data_cleaning_node
from src.nodes.market_data_collection import market_data_collection_node
from src.nodes.report_generation_node import report_generation_node
from src.nodes.statistical_analysis import statistical_analysis_node
from src.nodes.planner import analysis_planner_node


def build_graph():
    """
    Build and compile the LangGraph application.
    """
    graph = StateGraph(MarketAnalysisState)

    graph.add_node("planner", analysis_planner_node)
    graph.add_node("data", market_data_collection_node)
    graph.add_node("context", context_research_node)
    graph.add_node("cleaning", data_cleaning_node)
    graph.add_node("analysis", statistical_analysis_node)
    graph.add_node("report", report_generation_node)

    # Join node as synchronization barrier
    graph.add_node("join", lambda state: {})

    graph.set_entry_point("planner")

    graph.add_edge("planner", "data")
    graph.add_edge("planner", "context")

    graph.add_edge("data", "join")
    graph.add_edge("context", "join")
    graph.add_edge("join", "cleaning")

    graph.add_edge("cleaning", "analysis")
    graph.add_edge("analysis", "report")
    graph.add_edge("report", END)

    return graph.compile()


