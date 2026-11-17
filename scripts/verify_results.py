"""Check completeness and cross-file consistency of the final experiment."""

import csv
import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "results" / "processed"
RAW = ROOT / "results" / "raw"
rows = list(csv.DictReader((ROOT / "analysis" / "results.csv").open(encoding="utf-8")))
assert len(rows) == 10
assert len({(r["model"], r["quantization"]) for r in rows}) == 10
validations = list(csv.DictReader((ROOT / "analysis" / "validation.csv").open(encoding="utf-8")))
assert len(validations) == 10
assert all(r["check_tensors_passed"] == "True" and r["cuda_detected"] == "True" for r in validations)
for row in rows:
    name = f"{row['model']}-{row['quantization'].lower()}"
    bench = json.loads((PROCESSED / f"{name}-benchmark.json").read_text(encoding="utf-8"))
    ppl = json.loads((PROCESSED / f"{name}-perplexity.json").read_text(encoding="utf-8"))
    quality = json.loads((PROCESSED / f"{name}-mmlu-full.json").read_text(encoding="utf-8"))
    harness = json.loads((ROOT / quality["harness_result"]).read_text(encoding="utf-8"))
    assert len(bench["pp512_samples_tps"]) == len(bench["tg128_samples_tps"]) == 5
    assert quality["n_samples"] == harness["n-samples"]["mmlu_pro_direct"]["effective"] == 12032
    assert quality["mmlu_pro_score"] == harness["results"]["mmlu_pro_direct"]["exact_match,letter-only"]
    assert bench["size_bytes"] == (ROOT / bench["file"]).stat().st_size
    assert ppl["dataset_sha256"] == json.loads((ROOT / "datasets" / "wiki.test.metadata.json").read_text(encoding="utf-8"))["sha256"]
    assert all(math.isfinite(float(row[k])) for k in ("file_size_gb", "peak_vram_mb", "pp512_tps_mean", "tg128_tps_mean", "perplexity", "mmlu_pro_score"))
    assert 0 <= float(row["mmlu_pro_score"]) <= 1
    assert math.isclose(float(row["perplexity"]), ppl["perplexity"])
    assert math.isclose(float(row["mmlu_pro_score"]), quality["mmlu_pro_score"])

for model in ("gemma3-4b", "qwen3-4b"):
    name = f"{model}-q2_k"
    first = json.loads((PROCESSED / f"{name}-perplexity.json").read_text(encoding="utf-8"))["perplexity"]
    repeat_text = (RAW / f"{name}-perplexity-repeat.log").read_text(encoding="utf-8-sig", errors="replace")
    match = re.search(r"Final estimate: PPL = ([0-9.]+)", repeat_text)
    assert match and first == float(match.group(1))
    manifest = next(r for r in csv.DictReader((RAW / "quantization_manifest.csv").open(encoding="utf-8")) if r["model"] == model and r["quantization"] == "Q2_K")
    gguf = ROOT / "models" / model / f"{name}.gguf"
    digest = hashlib.sha256()
    with gguf.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    assert digest.hexdigest().upper() == manifest["sha256"].upper()

plots = list((ROOT / "analysis" / "plots").glob("*.png"))
assert len(plots) == 6 and all(path.stat().st_size > 10000 for path in plots)
print("OK: 10 configurations, 5 pp and 5 tg samples each, 12,032 MMLU-Pro questions each, 2 Q2 repeats, 6 plots")
