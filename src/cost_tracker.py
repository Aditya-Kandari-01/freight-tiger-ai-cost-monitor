
import json
from pathlib import Path


def main():
    usage = {
        "retrieval_model": (
            "sentence-transformers/all-MiniLM-L6-v2"
        ),
        "retrieval_type": "Local embedding-based semantic search",
        "llm_model": None,
        "llm_api_calls": 0,
        "llm_input_tokens": 0,
        "llm_output_tokens": 0,
        "estimated_llm_api_cost_usd": 0.0,
        "local_inference_cost": "Not measured",
        "notes": (
            "Context notes and anomaly queries are embedded "
            "locally using Sentence Transformers. "
            "No paid LLM API is used. "
            "Final evidence decisions use deterministic "
            "route, date, and cost-impact validation."
        )
    }

    output = Path("output/token_cost_log.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(usage, indent=2),
        encoding="utf-8"
    )

    print(json.dumps(usage, indent=2))


if __name__ == "__main__":
    main()
