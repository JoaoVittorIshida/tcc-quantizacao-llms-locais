"""Run pp512/tg128 five times per GGUF and sample GPU memory with NVML."""

import json
import os
import statistics
import subprocess
import time
from pathlib import Path

import pynvml


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
PROCESSED = ROOT / "results" / "processed"
EXE = ROOT / "llama.cpp" / "build" / "bin" / "llama-bench.exe"
MODELS = ("gemma3-4b", "qwen3-4b")
QUANTS = ("native", "q8_0", "q6_k", "q4_k_m", "q2_k")
CUDA_BIN = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin"
ENV = os.environ.copy()
ENV["PATH"] = os.path.join(CUDA_BIN, "x64") + os.pathsep + CUDA_BIN + os.pathsep + ENV["PATH"]
ARGS = ["-p", "512", "-n", "128", "-r", "5", "-ngl", "999", "-b", "2048", "-ub", "512", "-ctk", "f16", "-ctv", "f16", "-fa", "off", "-o", "json"]


def memory_mib(handle):
    return pynvml.nvmlDeviceGetMemoryInfo(handle).used / (1024 * 1024)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    try:
        for model in MODELS:
            for quant in QUANTS:
                name = f"{model}-{quant}"
                result_path = PROCESSED / f"{name}-benchmark.json"
                if result_path.exists():
                    print(f"Skip completed {name}", flush=True)
                    continue
                gguf = ROOT / "models" / model / f"{name}.gguf"
                raw_path = RAW / f"{name}-bench.json"
                stderr_path = RAW / f"{name}-bench.stderr.log"
                baseline = statistics.median(memory_mib(handle) for _ in range(10))
                peak = baseline
                command = [str(EXE), "-m", str(gguf), *ARGS]
                print(f"Benchmark {name}", flush=True)
                started = time.time()
                with raw_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
                    proc = subprocess.Popen(command, cwd=ROOT, env=ENV, stdout=out, stderr=err)
                    while proc.poll() is None:
                        peak = max(peak, memory_mib(handle))
                        time.sleep(0.05)
                    code = proc.returncode
                peak = max(peak, memory_mib(handle))
                if code:
                    raise RuntimeError(f"{name} failed with exit {code}: {stderr_path}")
                data = json.loads(raw_path.read_text(encoding="utf-8"))
                assert len(data) == 2, (name, len(data))
                pp = next(x for x in data if x["n_prompt"] == 512 and x["n_gen"] == 0)
                tg = next(x for x in data if x["n_prompt"] == 0 and x["n_gen"] == 128)
                assert len(pp["samples_ts"]) == len(tg["samples_ts"]) == 5
                assert pp["backends"] == tg["backends"] == "CUDA"
                result = {
                    "model": model,
                    "quantization": quant.upper(),
                    "file": str(gguf.relative_to(ROOT)).replace("\\", "/"),
                    "size_bytes": gguf.stat().st_size,
                    "size_gb": gguf.stat().st_size / 1e9,
                    "pp512_tps_mean": pp["avg_ts"],
                    "pp512_tps_std": pp["stddev_ts"],
                    "pp512_samples_tps": pp["samples_ts"],
                    "tg128_tps_mean": tg["avg_ts"],
                    "tg128_tps_std": tg["stddev_ts"],
                    "tg128_samples_tps": tg["samples_ts"],
                    "baseline_vram_mib": baseline,
                    "peak_vram_mib": peak,
                    "peak_vram_above_baseline_mib": max(0, peak - baseline),
                    "duration_s": time.time() - started,
                    "bench_args": ARGS,
                    "llama_commit_short": pp["build_commit"],
                    "gpu_info": pp["gpu_info"],
                }
                result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
                print(f"  pp={pp['avg_ts']:.1f} tg={tg['avg_ts']:.1f} peak={peak:.0f} MiB", flush=True)
    finally:
        pynvml.nvmlShutdown()


if __name__ == "__main__":
    main()
