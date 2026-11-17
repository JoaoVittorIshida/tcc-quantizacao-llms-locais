"""Summarize the ten completed llama-cli validation logs."""

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"offloaded (\d+)/(\d+) layers to GPU")
rows = []
for model in ("gemma3-4b", "qwen3-4b"):
    for quant in ("native", "q8_0", "q6_k", "q4_k_m", "q2_k"):
        name = f"{model}-{quant}"
        log_path = ROOT / "results" / "raw" / f"{name}-validation.log"
        log = log_path.read_text(encoding="utf-8-sig", errors="replace")
        matches = PATTERN.findall(log)
        if not matches:
            raise RuntimeError(f"No GPU offload confirmation for {name}")
        loaded, total = map(int, matches[-1])
        if loaded != total:
            raise RuntimeError(f"Partial GPU offload for {name}: {loaded}/{total}")
        answers = [line.strip() for line in log.splitlines() if line.startswith("A CPU cache")]
        if not answers:
            raise RuntimeError(f"No answer found for {name}")
        answer = answers[-1]
        if re.search(r"\b(?:nan|inf)\b", answer, re.IGNORECASE):
            raise RuntimeError(f"Non-finite marker found in answer for {name}")
        rows.append({
            "model": model,
            "quantization": quant.upper(),
            "gpu_layers": loaded,
            "total_layers": total,
            "cuda_detected": "CUDA0" in log,
            "check_tensors_passed": True,
            "answer": answer,
            "log": str(log_path.relative_to(ROOT)).replace("\\", "/"),
        })
out = ROOT / "analysis" / "validation.csv"
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f"Validated {len(rows)} models: {out}")
