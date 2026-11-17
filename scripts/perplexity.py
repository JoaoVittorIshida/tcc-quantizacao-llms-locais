"""Evaluate all ten GGUF files on the same WikiText-2 raw test split."""

import json
import os
import re
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
PROCESSED = ROOT / "results" / "processed"
EXE = ROOT / "llama.cpp" / "build" / "bin" / "llama-perplexity.exe"
DATA = ROOT / "datasets" / "wiki.test.raw"
CUDA_BIN = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin"
ENV = os.environ.copy()
ENV["PATH"] = os.path.join(CUDA_BIN, "x64") + os.pathsep + CUDA_BIN + os.pathsep + ENV["PATH"]
ARGS = ["-f", str(DATA), "-c", "512", "-b", "2048", "-ub", "512", "-ngl", "all", "-fa", "off", "-fit", "off", "-ctk", "f16", "-ctv", "f16"]
PATTERN = re.compile(r"Final estimate: PPL = ([0-9.]+) \+/- ([0-9.]+)")


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    for model in ("gemma3-4b", "qwen3-4b"):
        for quant in ("native", "q8_0", "q6_k", "q4_k_m", "q2_k"):
            name = f"{model}-{quant}"
            target = PROCESSED / f"{name}-perplexity.json"
            if target.exists():
                print(f"Skip completed {name}", flush=True)
                continue
            log = RAW / f"{name}-perplexity.log"
            if not log.exists():
                gguf = ROOT / "models" / model / f"{name}.gguf"
                print(f"Perplexity {name}", flush=True)
                started = time.time()
                with log.open("w", encoding="utf-8") as out:
                    result = subprocess.run([str(EXE), "-m", str(gguf), *ARGS], cwd=ROOT, env=ENV, stdout=out, stderr=subprocess.STDOUT)
                if result.returncode:
                    raise RuntimeError(f"{name} failed with exit {result.returncode}: {log}")
                duration = time.time() - started
            else:
                print(f"Parse existing {name}", flush=True)
                duration = None
            match = PATTERN.search(log.read_text(encoding="utf-8-sig", errors="replace"))
            if not match:
                raise RuntimeError(f"No final PPL for {name}: {log}")
            output = {
                "model": model,
                "quantization": quant.upper(),
                "perplexity": float(match.group(1)),
                "reported_uncertainty": float(match.group(2)),
                "duration_s": duration,
                "dataset_sha256": json.loads((ROOT / "datasets" / "wiki.test.metadata.json").read_text(encoding="utf-8"))["sha256"],
                "args": ARGS,
            }
            target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
            print(f"  PPL={output['perplexity']:.4f}", flush=True)


if __name__ == "__main__":
    main()
