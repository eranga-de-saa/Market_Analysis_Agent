from build_graph import build_graph
from nodes.entrypoint import initialize_state


def main():
    """
    Simple sanity check to verify the full pipeline runs.
    """

    app = build_graph()

    prompt = "Analyze volatility of Apple and Microsoft over the last 3 years"
    state = initialize_state(prompt)

    print("\nStarting market analysis...\n")

    # Optional: stream progress
    # for event in app.stream(state, stream_mode="updates"):
    #     node_name = list(event.keys())[0]
    #     print(f"[STEP] {node_name}")

    # Final invoke to get completed state
    final_state = app.invoke(state)

    report = final_state["final_report"]

    print("\n=== FINAL REPORT ===\n")
    print(report.model_dump_json(indent=2))

if __name__ == "__main__":
    main()    