"""Portfolio-facing research artifacts stay reviewable and provenance-complete."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "feature_name",
    "feature_family",
    "raw_source",
    "grain",
    "transformation",
    "observation_cutoff",
    "available_at_decision",
    "fit_partition",
    "missing_treatment",
    "model_role",
    "leakage_risk",
    "proxy_or_fairness_risk",
    "validation",
}


def test_feature_provenance_contract() -> None:
    path = ROOT / "reports" / "feature_provenance.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    assert REQUIRED.issubset(reader.fieldnames or [])
    assert rows
    for row in rows:
        assert row["feature_name"]
        assert row["raw_source"]
        assert row["observation_cutoff"]
        assert row["validation"]


def test_research_notebooks_are_clean() -> None:
    notebooks = sorted((ROOT / "notebooks").glob("*.ipynb"))
    assert notebooks
    forbidden = ("/Users/", "chatgpt", "openai", "codex")
    for path in notebooks:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        assert not any(token.lower() in lowered for token in forbidden)
        notebook = json.loads(text)
        assert notebook["nbformat"] == 4
        assert any(cell["cell_type"] == "code" for cell in notebook["cells"])
        for cell in notebook["cells"]:
            for output in cell.get("outputs", []):
                assert output.get("output_type") != "error"
