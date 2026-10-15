# Freight Tiger — Smart Shipping Cost Monitor

A Python-based freight cost anomaly detection system using historical analysis, peer comparisons, semantic evidence retrieval, and deterministic validation.

## Overview

This project analyzes shipment records to identify unusual transportation cost increases and determine whether contextual events, such as weather disruptions, fuel price changes, or festival surcharges, provide valid explanations.

The system combines numerical anomaly detection with local embedding-based semantic search while maintaining reproducible, evidence-grounded decisions.

## Tech Stack

- Python 3.13
- pandas and NumPy
- Sentence Transformers
- `all-MiniLM-L6-v2` embedding model
- Cosine similarity
- pytest
- SHA-256 for reproducibility verification

## System Pipeline

1. **Data Processing:** Load and validate shipment records.
2. **Weekly Aggregation:** Calculate weighted freight cost per tonne-kilometre for each route and week.
3. **Historical Comparison:** Compare each route's current cost with its previous eight available weeks.
4. **Peer Comparison:** Compare costs against other routes of the same route type during the same week.
5. **Anomaly Detection:** Identify unusual increases using a configurable threshold.
6. **Semantic Retrieval:** Retrieve and rank contextual notes using Sentence Transformers and cosine similarity.
7. **Evidence Validation:** Verify route applicability, event dates, and documented cost impact.
8. **Report Generation:** Produce an eight-column CSV containing anomaly classifications and explanations.

## Cost Calculation

Weekly cost per tonne-kilometre:

```text
Cost per tonne-km =
    SUM(freight_cost_inr)
    / SUM(quantity_tonnes × distance_km)
```

Shipments are grouped by origin, destination, `route_type`, and Monday-starting week.

The weighted calculation makes transportation costs comparable across shipments of different sizes and distances.

## Comparison Baselines

### Historical Comparison

- Uses the previous eight available weekly observations for the same route.
- Excludes the current week to prevent data leakage.
- Uses available history when fewer than eight prior weeks exist.
- Leaves the historical comparison unavailable for the first recorded week.

### Peer Comparison

- Compares routes with the same `route_type`.
- Uses costs from the same calendar week.
- Excludes the route being evaluated.
- Leaves the peer comparison unavailable if no other comparable route exists.

## Anomaly Detection

A configurable 20% threshold is used.

A route-week is considered a potential anomaly when its cost exceeds the historical or peer baseline by more than 20%, provided its historical change is positive or historical data is unavailable.

This threshold is a documented heuristic rather than a value specified by Freight Tiger.

## Semantic Evidence Retrieval

The system uses the local Sentence Transformers model `all-MiniLM-L6-v2` to generate embeddings for contextual notes and anomaly descriptions.

### Retrieval Process

1. Filter contextual notes by route applicability and date proximity.
2. Generate embeddings for contextual notes and anomaly queries.
3. Rank eligible notes using cosine similarity.
4. Pass candidate notes to the deterministic evidence validator.
5. Accept a justification only when the evidence supports the increase.

Embeddings are processed locally. No dedicated vector database is required for the small contextual dataset.

The system uses embedding-based semantic retrieval, but it does not use a generative LLM to produce explanations.

## Evidence Validation

Potential anomalies are evaluated against `context_notes.csv`.

A contextual note is accepted only when:

- It applies to the correct route or all routes.
- Its documented event period overlaps the evaluated week.
- It explicitly supports an increase in transportation costs.
- Applicable magnitude restrictions are satisfied.

The validator uses predefined evidence policies for the supplied contextual notes. Semantic similarity alone is never sufficient to justify an anomaly.

## Dataset

| Metric | Count |
|---|---:|
| Shipment records | 2,940 |
| Routes | 7 |
| Weekly route records | 728 |
| Contextual notes | 10 |

## Installation

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

The Sentence Transformers model is downloaded on first use and cached locally.

## Running the Pipeline

Execute the following commands from the project root:

```bash
python -m src.processor
python -m src.anomaly_detector
python -m src.flagger
python -m src.report_generator
```

The final report is generated at:

`output/final_report.csv`

## Running Tests

```bash
python -m pytest tests/ -v
```

Latest verified result: **24 tests passed**, including four semantic retrieval tests.

## Evidence Evaluation

```bash
python -m src.evaluation
```

The curated evidence evaluation includes nine scenarios covering valid matches, irrelevant notes, date mismatches, and unsupported cost increases.

Latest result: **9/9 cases passed**.

This evaluation primarily checks deterministic evidence validation rather than semantic ranking quality.

## Reproducibility

```bash
python -m src.reproducibility
```

The pipeline is executed three times, and SHA-256 checksums of the resulting CSV files are compared.

The earlier deterministic version passed all three checks. The embedding-enhanced version should be verified separately before submission.

## Token and Cost Tracking

```bash
python -m src.cost_tracker
```

The system uses local sentence embeddings without external LLM API calls.

| Metric | Value |
|---|---|
| Embedding model | all-MiniLM-L6-v2 |
| LLM API calls | 0 |
| LLM input tokens | 0 |
| LLM output tokens | 0 |
| Estimated LLM API cost | $0.00 |
| Local inference cost | Not measured |

The reported zero token counts refer to LLM API usage, not the internal tokenization performed by the local embedding model.

## Output Format

The final report contains exactly eight columns:

1. `route`
2. `week_of`
3. `cost_per_tonne_km`
4. `vs_own_history`
5. `vs_similar_routes`
6. `flagged`
7. `matched_note_id`
8. `reason`

Possible classifications:

- **No:** No significant anomaly detected.
- **Yes:** Unusual increase without adequate supporting evidence.
- **No (justified):** Unusual increase supported by validated contextual evidence.

## Results

The latest report generated using semantic retrieval produced:

| Classification | Records |
|---|---:|
| Normal | 709 |
| Unexplained anomalies | 16 |
| Justified anomalies | 3 |
| Total | 728 |

The justified anomalies matched notes N001 and N002.

## Limitations

- The 20% anomaly threshold is heuristic rather than statistically optimized.
- Evidence validation uses manually defined policies for the provided contextual notes.
- Semantic retrieval ranks eligible candidates but does not independently establish causal explanations.
- The small evaluation dataset does not establish real-world retrieval accuracy.
- The system does not provide generative question-answering.
- Historical comparison assumes available recorded weeks are suitable for rolling averages.
- Local embedding inference time, memory use, and computational cost are not measured.

## Conclusion

The Smart Shipping Cost Monitor combines weighted freight cost analysis, historical and peer comparisons, embedding-based contextual retrieval, and deterministic validation to identify unusual transportation cost increases.

The system prioritizes explainability, reproducibility, and evidence-grounded anomaly classification.