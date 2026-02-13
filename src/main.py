from src.build_graph import build_graph
from src.nodes.entrypoint import initialize_state
from fastapi import FastAPI

app = FastAPI()

@app.post("/run")
async def root(prompt: str):
    return {"message": prompt}


# def main():
#     """
#     Simple sanity check to verify the full pipeline runs.
#     """

#     workflow = build_graph()

#     prompt = "Analyze volatility of Apple and Microsoft over the last 3 years"
#     state = initialize_state(prompt)

#     print("\nStarting market analysis...\n")

#     # Optional: stream progress
#     # for event in app.stream(state, stream_mode="updates"):
#     #     node_name = list(event.keys())[0]
#     #     print(f"[STEP] {node_name}")

#     # Final invoke to get completed state
#     final_state = workflow.invoke(state)

#     report = final_state["final_report"]

#     print("\n=== FINAL REPORT ===\n")
#     print(report.model_dump_json(indent=2))

# if __name__ == "__main__":
#     main()    