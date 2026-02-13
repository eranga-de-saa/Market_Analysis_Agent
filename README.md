# Market Analysis AI

End-to-end market analysis pipeline that plans an analysis, collects market data and context, computes metrics, and generates a structured report. Built with FastAPI + LangGraph and integrates with MCP for tool orchestration.

## What It Does

1. Plans an analysis (LLM) from a user prompt.
2. Fetches market time series data (Yahoo Finance via `yfinance`).
3. Pulls qualitative context (DuckDuckGo search + LLM summary).
4. Cleans data and computes metrics.
5. Generates a structured research report.

## Architecture

- FastAPI app in `src/main.py`
- LangGraph workflow in `src/build_graph.py`
- Nodes in `src/nodes/`
  - `planner` -> `data` -> `cleaning`
  - `context` runs in parallel with `data`
  - `join` -> `analysis` -> `report`
- Tools in `src/tools/`
- State schema in `src/classes/state.py`

## Requirements

- Python 3.10+ recommended
- OpenAI API key for `langchain_openai`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file at the repo root:

```bash
OPENAI_API_KEY=your_key_here
```

Optional (if using LangSmith):

```bash
LANGSMITH_API_KEY=your_key_here
LANGSMITH_TRACING=true
```

## Run The API

```bash
python /Users/erangad/Desktop/Market-analysis-ai/src/main.py
```

The server starts on `http://0.0.0.0:8000`.

## API Usage

### 1) Run (SSE stream)

```bash
curl -N -X POST "http://localhost:8000/run/stream?prompt=Analyze AAPL and MSFT over the last 3 years" \
  -H "Accept: text/event-stream"
```

You will receive progress events and a final report payload.

### 2) MCP-friendly run

```bash
curl -X POST "http://localhost:8000/mcp/run?prompt=Analyze BTC and ETH over the last 2 years"
```

## Output Shape

The final response contains:

- `metrics`: computed metric outputs per symbol
- `topic`: the analysis topic inferred by the planner
- `report`: a structured research report (executive summary, findings, conclusion)

## Notes / Gotchas

- `yfinance` returns data based on ticker availability. If no data is returned, the workflow raises an error.
- `context_research` uses DuckDuckGo search via `ddgs`; rate limits or empty results will be summarized as no context found.
- For `beta` computation, a benchmark must be present in the `AnalysisPlan`.

## Project Structure

```text
src/
  main.py
  build_graph.py
  nodes/
    planner.py
    market_data_collection.py
    data_cleaning.py
    context_research.py
    statistical_analysis.py
    report_generation_node.py
    entrypoint.py
  tools/
    market_data.py
    market_metrics.py
    compute_market_metrics.py
    context_research.py
  classes/
    AnalysisPlan.py
    report_schema.py
    state.py
  utils/
    time.py
```

## Development Tips

- Use `uvicorn` for reloads:
  ```bash
  uvicorn src.main:app --reload
  ```
- Add new metrics in `src/tools/market_metrics.py` and map them in `METRIC_FUNCTIONS`.

