from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from src.build_graph import build_graph
from src.nodes.entrypoint import initialize_state
from fastapi_mcp import FastApiMCP
import json

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

# MCP-safe
@app.post("/run/step", operation_id="run_workflow")
async def run_mcp(prompt: str):
    workflow = build_graph()
    state = initialize_state(prompt)
    final_state = workflow.invoke(state)
    return {
        "metrics": final_state.get("computed_metrics"),
        "topic": final_state["analysis_plan"].topic,
        "report": final_state["final_report"]
    }


@app.post("/run/stream", operation_id="stream_workflow")
async def run(prompt: str):

    workflow = build_graph()
    state = initialize_state(prompt)
    seen_progress = set()

    def event_stream():
        try:
            # Stream intermediate progress
            for event in workflow.stream(state, stream_mode="updates"):
                for node, payload in event.items():
                    if "progress" in payload:
                        for msg in payload["progress"]:
                            if msg in seen_progress:
                                continue
                            seen_progress.add(msg)
                            data = {
                                "type": "progress",
                                "node": node,
                                "progress": msg,
                            }
                            yield f"data: {json.dumps(data)}\n\n"
                    if "final_report" in payload:    
                        data = {
                            "report": payload["final_report"],
                        }
                        yield f"data: {json.dumps(data)}\n\n"
        except Exception as e:
            error = { "error": str(e)}
            yield f"error: {json.dumps(error)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )

# MCP mounted at import time
mcp = FastApiMCP(app, include_operations=['stream_workflow', 'run_workflow'])

# Mount the MCP server directly to your app
mcp.mount_http()  



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True)

