from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") 
import asyncio
import json
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi_mcp import FastApiMCP                       

from src.kafka_client import get_producer, enqueue_job, run_consumer, REDIS_URL

app = FastAPI()
producer = None


@app.on_event("startup")
async def startup():
    global producer
    producer = await get_producer()
    asyncio.create_task(run_consumer())


@app.on_event("shutdown")
async def shutdown():
    await producer.stop()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run/step", operation_id="run_workflow")       
async def run_mcp(prompt: str):
    job_id = await enqueue_job(producer, prompt)
    rdb = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        for _ in range(300):
            status = await rdb.get(f"job:{job_id}:status")
            if status == "done":
                raw = await rdb.get(f"job:{job_id}:result")
                return json.loads(raw)
            if status and status.startswith("error:"):
                raise HTTPException(500, status[6:])
            await asyncio.sleep(1)
        raise HTTPException(408, "Job timed out")
    finally:
        await rdb.aclose()


@app.post("/run/enqueue")
async def enqueue(prompt: str):
    job_id = await enqueue_job(producer, prompt)
    return {"job_id": job_id}


@app.get("/run/status/{job_id}")
async def job_status(job_id: str):
    rdb = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        status = await rdb.get(f"job:{job_id}:status")
        if not status:
            raise HTTPException(404, "Job not found")
        if status == "done":
            raw = await rdb.get(f"job:{job_id}:result")
            return {"status": "done", "result": json.loads(raw)}
        return {"status": status}
    finally:
        await rdb.aclose()


@app.post("/run/stream", operation_id="stream_workflow") 
async def run_stream(prompt: str):
    job_id = await enqueue_job(producer, prompt)
    rdb = redis.from_url(REDIS_URL, decode_responses=True)

    async def event_stream():
        try:
            yield f"data: {json.dumps({'job_id': job_id, 'status': 'queued'})}\n\n"
            for _ in range(300):
                status = await rdb.get(f"job:{job_id}:status")
                if status == "done":
                    raw = await rdb.get(f"job:{job_id}:result")
                    yield f"data: {json.dumps({'status': 'done', 'result': json.loads(raw)})}\n\n"
                    return
                if status and status.startswith("error:"):
                    yield f"data: {json.dumps({'status': 'error', 'detail': status[6:]})}\n\n"
                    return
                yield f"data: {json.dumps({'status': status or 'queued'})}\n\n"
                await asyncio.sleep(1)
            yield f"data: {json.dumps({'status': 'timeout'})}\n\n"
        finally:
            await rdb.aclose()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# exposes both operations to MCP clients
mcp = FastApiMCP(app, include_operations=["run_workflow", "stream_workflow"])
mcp.mount_http()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)