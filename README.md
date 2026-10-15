
# Freight Tiger — Smart Shipping Cost Monitor

A Python-based system for detecting unusual freight transportation
cost increases and identifying documented explanations using
contextual evidence.

## Overview

The system processes shipment records, computes normalized weekly
transportation costs, compares them against historical and peer
baselines, and flags potentially abnormal increases.

It then examines contextual notes to identify evidence that
could justify the higher costs.

## Tech Stack

- Python
- pandas
- pytest
- Rule-based contextual evidence retrieval

## Pipeline

1. Shipment preprocessing
2. Weekly cost aggregation
3. Historical and peer comparisons
4. Anomaly detection
5. Context retrieval and evidence validation
6. Final report generation

## Cost Calculation

Weekly cost per tonne-km:

    sum(freight_cost_inr) / sum(quantity_tonnes * distance_km)

Shipments are grouped by origin, destination, route_type,
and Monday-starting week.

## Comparison Baselines

Historical baseline:
- Previous 8 available weekly observations for the same route
- Current week excluded
- Fewer than 8 prior weeks: use available history
- First week: historical comparison unavailable

Peer baseline:
- Average weekly cost of other routes with the same route_type
- Same calendar week
- Current route excluded

## Anomaly Detection

An initial 20% increase threshold is used.

A record is considered a potential anomaly when the cost
is rising relative to known history (or history is unavailable)
and exceeds the historical or peer baseline by more than 20%.

This threshold is a documented design assumption rather
than a threshold specified by Freight Tiger.

## Evidence Validation

Potential anomalies are checked against context_notes.csv.

A justification is accepted only when:
- The note applies to the correct route or all routes
- The event overlaps the relevant week
- The note explicitly supports increased transportation costs
- Magnitude constraints are respected where applicable

No valid supporting evidence results in an unexplained anomaly.

The current implementation uses deterministic retrieval and
rules, not a vector database or LLM.

## Dataset

- 2,940 shipment records
- 7 routes
- 728 aggregated route-week records
- 10 contextual notes

## Running

Install dependencies:

    pip install -r requirements.txt

Run the pipeline:

    python -m src.processor
    python -m src.anomaly_detector
    python -m src.flagger
    python -m src.report_generator

Run tests:

    python -m pytest tests/ -v

Run evaluation:

    python -m src.evaluation

Run reproducibility check:

    python -m src.reproducibility

Generate LLM cost log:

    python -m src.cost_tracker

## Output

Final report:

    output/final_report.csv

Required columns:

- route
- week_of
- cost_per_tonne_km
- vs_own_history
- vs_similar_routes
- flagged
- matched_note_id
- reason

Flag categories:

- No
- Yes
- No (justified)

## Initial Results

- 728 weekly records
- 709 normal
- 19 potential anomalies
- 3 justified anomalies
- 16 unexplained anomalies

Results are based on the selected anomaly threshold and
the current contextual evidence rules.

## Trust and Evaluation

The project uses unit tests for weekly aggregation,
baseline comparisons, flagging, and evidence validation.

A small labeled evaluation set checks that supporting notes
are correctly selected and unsupported explanations are rejected.

A three-run reproducibility check compares SHA-256 hashes of
the generated CSV outputs.

## LLM Cost

No external LLM is currently used.

- Input tokens: 0
- Output tokens: 0
- LLM calls: 0
- Estimated LLM API cost: $0.00

Local processing costs are excluded.

## Limitations

- The 20% threshold is heuristic and not statistically optimized.
- Context matching depends on documented evidence rules.
- The system does not currently support semantic RAG or natural
  language question-answering.
- Historical comparisons use available recorded weeks, assuming
  continuous weekly observations within the supplied dataset.
