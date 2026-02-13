# tools/context_research.py
from ddgs import DDGS
from langchain_openai import ChatOpenAI
from langsmith import traceable


llm = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0
)

@traceable(run_type="llm")
def generate_symbol_topic(
    global_topic: str,
    symbol: str,
    market: str
) -> str:
    response = llm.invoke(
        f"""
        You are refining a financial research topic.

        Global topic:
        "{global_topic}"

        Asset:
        {symbol}

        Market:
        {market}

        Produce a single, focused research topic specific to this asset.
        Do not introduce new themes.
        One sentence only.
        """
    )

    return response.content.strip()

@traceable(run_type="llm")
def research_market_context_for_symbol(
    topic: str,
    symbol: str,
    time_phrase: str
) -> str:
    """
    Search and summarize qualitative context for a single symbol.
    """

    query = " ".join([symbol, topic, time_phrase])

    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=5):
            if r.get("body"):
                results.append(r["body"])

    if not results:
        return "No significant qualitative market context found."

    joined_text = "\n".join(results)

    summary = llm.invoke(
        f"""
        You are a financial analyst.

        Summarize the following information strictly in relation to:
        "{topic}"

        Focus on drivers, risks, and regime-level factors.
        Avoid generic macro commentary.

        Source material:
        {joined_text}
        """
    )

    return summary.content.strip()
