"""Run MMLU-Pro direct-answer evaluations through lm-eval and llama-server."""

import argparse
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
PROCESSED = ROOT / "results" / "processed"
SERVER = ROOT / "llama.cpp" / "build" / "bin" / "llama-server.exe"
EVAL = ROOT / ".venv" / "Scripts" / "lm-eval.exe"
CUDA_BIN = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin"
ENV = os.environ.copy()
ENV["PATH"] = os.path.join(CUDA_BIN, "x64") + os.pathsep + CUDA_BIN + os.pathsep + ENV["PATH"]
ENV["PYTHONIOENCODING"] = "utf-8"
PORT = 8090
SERVER_ARGS = [
    "--host", "127.0.0.1", "--port", str(PORT), "--alias", "tcc-model",
    "-ngl", "all", "-fit", "off", "-c", "2048", "-np", "1",
    "-b", "2048", "-ub", "512", "-ctk", "f16", "-ctv", "f16",
    "-fa", "on", "-rea", "off", "--no-webui",
]


def wait_ready(server):
    url = f"http://127.0.0.1:{PORT}/health"
    until = time.time() + 120
    while time.time() < until:
        if server.poll() is not None:
            raise RuntimeError(f"llama-server exited {server.returncode} during startup")
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(0.5)
    raise TimeoutError("llama-server did not become ready within 120 seconds")


def find_result(directory):
    for path in sorted(directory.rglob("results_*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(obj, dict) and "results" in obj and "mmlu_pro_direct" in obj["results"]:
            return path, obj
    raise FileNotFoundError(f"No lm-eval result JSON under {directory}")


def run_one(model, quant, mode, force=False, cache_tag=""):
    name = f"{model}-{quant}"
    target = PROCESSED / f"{name}-mmlu-{mode}.json"
    if target.exists() and not force:
        print(f"Skip completed {name} {mode}", flush=True)
        return
    gguf = ROOT / "models" / model / f"{name}.gguf"
    output_dir = RAW / f"mmlu_{mode}" / name
    output_dir.mkdir(parents=True, exist_ok=True)
    server_log = RAW / f"{name}-mmlu-{mode}-server.log"
    eval_log = RAW / f"{name}-mmlu-{mode}-harness.log"
    command = [str(SERVER), "-m", str(gguf), *SERVER_ARGS]
    print(f"MMLU-Pro {mode} {name}", flush=True)
    started = time.time()
    with server_log.open("w", encoding="utf-8") as slog:
        server = subprocess.Popen(command, cwd=ROOT, env=ENV, stdout=slog, stderr=subprocess.STDOUT)
        try:
            wait_ready(server)
            model_args = (
                f"model=tcc-model,base_url=http://127.0.0.1:{PORT}/v1/chat/completions,"
                "tokenizer_backend=none,tokenized_requests=False,num_concurrent=8,"
                "max_length=2048,max_retries=3,timeout=300"
            )
            eval_command = [
                str(EVAL), "run", "--model", "local-chat-completions",
                "--model_args", model_args, "--tasks", "mmlu_pro_direct",
                "--include_path", str(ROOT / "configs"),
                "--apply_chat_template", "--num_fewshot", "0",
                "--batch_size", "1", "--output_path", str(output_dir),
                "--use_cache", str(PROCESSED / f"{name}-mmlu-{mode}-cache{cache_tag}"),
            ]
            if mode == "pilot":
                eval_command.extend(["--limit", "70", "--log_samples"])
            with eval_log.open("w", encoding="utf-8") as elog:
                result = subprocess.run(eval_command, cwd=ROOT, env=ENV, stdout=elog, stderr=subprocess.STDOUT)
            if result.returncode:
                raise RuntimeError(f"lm-eval exited {result.returncode}: {eval_log}")
            source, data = find_result(output_dir)
            metrics = data["results"]["mmlu_pro_direct"]
            score_key = next(k for k in metrics if k.startswith("exact_match,") and not k.endswith("_stderr"))
            sample_counts = data.get("n-samples", {}).get("mmlu_pro_direct", {})
            count = sample_counts.get("effective")
            output = {
                "model": model,
                "quantization": quant.upper(),
                "mode": mode,
                "mmlu_pro_score": metrics[score_key],
                "score_key": score_key,
                "n_samples": count,
                "duration_s": time.time() - started,
                "task": "mmlu_pro_direct",
                "protocol": "zero-shot; direct letter; 8 generation tokens; temperature 0; Qwen reasoning off",
                "dataset_revision": "b189ec765aa7ed75c8acfea42df31fdae71f97be",
                "harness_result": str(source.relative_to(ROOT)).replace("\\", "/"),
                "server_args": SERVER_ARGS,
                "model_args": model_args,
                "cuda_graphs_disabled": bool(ENV.get("GGML_CUDA_DISABLE_GRAPHS")),
            }
            target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
            print(f"  accuracy={output['mmlu_pro_score']:.4f}, n={count}", flush=True)
        finally:
            server.terminate()
            try:
                server.wait(timeout=15)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("pilot", "full"))
    parser.add_argument("--force", action="store_true", help="rerun even if a parsed result exists")
    parser.add_argument("--cache-tag", default="", help="suffix for an independent lm-eval cache")
    parser.add_argument("--model", choices=("gemma3-4b", "qwen3-4b"), help="run only one model family")
    args = parser.parse_args()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    if args.mode == "pilot":
        cases = (("gemma3-4b", "native"), ("qwen3-4b", "native"))
    else:
        cases = ((model, quant) for model in ("gemma3-4b", "qwen3-4b") for quant in ("native", "q8_0", "q6_k", "q4_k_m", "q2_k"))
    for model, quant in cases:
        if args.model and model != args.model:
            continue
        run_one(model, quant, args.mode, args.force, args.cache_tag)


if __name__ == "__main__":
    main()
