from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from src.build_graph import build_graph
from src.nodes.entrypoint import initialize_state
import json

app = FastAPI()

@app.post("/run")
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
