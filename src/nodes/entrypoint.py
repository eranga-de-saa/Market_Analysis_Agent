# entrypoint.py
#from state import MarketAnalysisState


def initialize_state(user_prompt: str) -> dict:
    """
    Entry point for the entire graph.
    Initializes shared state with safe defaults.
    """

    return {
        "user_prompt": user_prompt,
        "progress": ["Workflow started"]
    }
