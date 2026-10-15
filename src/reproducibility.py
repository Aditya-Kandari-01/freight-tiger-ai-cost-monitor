
import subprocess
import sys
import hashlib
from pathlib import Path

PIPELINE = [
    "src.processor",
    "src.anomaly_detector",
    "src.flagger",
    "src.report_generator"
]

OUTPUT = Path("output/final_report.csv")
LOG = Path("output/reproducibility_log.txt")


def run_pipeline():
    for module in PIPELINE:
        subprocess.run(
            [sys.executable, "-m", module],
            check=True,
            capture_output=True,
            text=True
        )


def get_hash(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def main():
    hashes = []

    for i in range(3):
        run_pipeline()

        file_hash = get_hash(OUTPUT)
        hashes.append(file_hash)

        print(f"Run {i + 1}: {file_hash}")

    passed = len(set(hashes)) == 1

    report = [
        "Freight Tiger Reproducibility Check",
        "Runs: 3",
        f"Identical CSV outputs: {passed}",
        "",
        *[
            f"Run {i + 1}: {value}"
            for i, value in enumerate(hashes)
        ]
    ]

    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text("\n".join(report), encoding="utf-8")

    print("\n" + "\n".join(report))

    if not passed:
        raise SystemExit(
            "FAILED: Results changed between runs"
        )

    print("\nPASS: All three runs produced identical CSV files.")


if __name__ == "__main__":
    main()
