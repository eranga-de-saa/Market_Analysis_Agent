# kafka client
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") 

import os
import asyncio
import json
import uuid
import redis.asyncio as redis
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from src.build_graph import build_graph
from src.nodes.entrypoint import initialize_state

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP")
TOPIC = os.getenv("TOPIC")
REDIS_URL = os.getenv("REDIS_URL")

# ── Producer ────────────────────────────────────────────────────────────────

async def get_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    await producer.start()
    return producer


async def enqueue_job(producer: AIOKafkaProducer, prompt: str) -> str:
    """Push a job and return its job_id."""
    job_id = str(uuid.uuid4())
    await producer.send_and_wait(TOPIC, {"job_id": job_id, "prompt": prompt})
    return job_id


# ── Consumer (runs as a background worker) ───────────────────────────────────

async def run_consumer():
    """
    Single-partition consumer → processes ONE message at a time.
    High availability: run multiple replicas, Kafka assigns partitions.
    """
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id="workflow-workers",       # same group = competing consumers
        value_deserializer=lambda v: json.loads(v.decode()),
        max_poll_records=1,                # fetch one message per poll
        enable_auto_commit=False,          # manual commit after success
    )
    rdb = redis.from_url(REDIS_URL, decode_responses=True)

    await consumer.start()
    try:
        async for msg in consumer:
            job_id = msg.value["job_id"]
            prompt = msg.value["prompt"]

            # Mark as processing
            await rdb.set(f"job:{job_id}:status", "processing", ex=3600)

            try:
                workflow = build_graph()
                state = initialize_state(prompt)
                final_state = workflow.invoke(state)

                result = {
                    "topic": final_state["analysis_plan"].topic,
                    "report": final_state["final_report"],
                }
                await rdb.set(f"job:{job_id}:result", json.dumps(result), ex=3600)
                await rdb.set(f"job:{job_id}:status", "done", ex=3600)

            except Exception as e:
                await rdb.set(f"job:{job_id}:status", f"error:{e}", ex=3600)

            # Commit only after successful processing
            await consumer.commit()
    finally:
        await consumer.stop()
        await rdb.aclose()