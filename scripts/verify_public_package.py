"""Read-only verification of the public evidence; no models, network or inference.

Added while preparing the public package, not used to produce the experiment.
Run from the repository root with Python 3.12 or newer.
"""
import ast
import collections
import csv
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def close(a, b):
    assert math.isfinite(float(a)) and math.isfinite(float(b))
    assert math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12), (a, b)


def main():
    for row in read_csv("docs/package_checksums.csv"):
        path = ROOT / row["path"]
        assert path.is_file(), row["path"]
        assert path.stat().st_size == int(row["size_bytes"]), row["path"]
        assert digest(path) == row["sha256"], row["path"]
    assert digest(ROOT / "analysis/results.csv") == "091f19a313157de822effd597550f16b7bf0273c5a6a5573c5f349ee3a34efe3"
    assert digest(ROOT / "analysis/validation.csv") == "8bcb26b78f59f9172c6e342d20ab3a6fa9ece763dc5f5fdbf453e8aa61527763"
    rows = read_csv("analysis/results.csv")
    validation = read_csv("analysis/validation.csv")
    assert len(rows) == len(validation) == 10
    assert all(r["check_tensors_passed"] == r["cuda_detected"] == "True" for r in validation)
    cases = {(r["model"], r["quantization"]): r for r in rows}
    assert len(cases) == 10
    for row in rows:
        name = f"{row['model']}-{row['quantization'].lower()}"
        raw = read_json(f"results/raw/{name}-bench.json")
        bench = read_json(f"results/processed/{name}-benchmark.json")
        ppl = read_json(f"results/processed/{name}-perplexity.json")
        mmlu = read_json(f"results/processed/{name}-mmlu-full.json")
        harness = read_json(mmlu["harness_result"])
        for prefix, nprompt, ngen in (("pp512", 512, 0), ("tg128", 0, 128)):
            trial = next(t for t in raw if (t["n_prompt"], t["n_gen"]) == (nprompt, ngen))
            assert trial["build_commit"] == "1c4729414"
            assert len(trial["samples_ts"]) == len(bench[prefix + "_samples_tps"]) == 5
            assert trial["samples_ts"] == bench[prefix + "_samples_tps"]
            for suffix, field in (("mean", "avg_ts"), ("std", "stddev_ts")):
                close(trial[field], row[prefix + "_tps_" + suffix])
                close(trial[field], bench[prefix + "_tps_" + suffix])
        close(row["size_bytes"], bench["size_bytes"])
        close(row["file_size_gb"], bench["size_bytes"] / 1e9)
        close(row["peak_vram_mb"], bench["peak_vram_above_baseline_mib"] * 1048576 / 1e6)
        close(row["gpu_peak_total_mb"], bench["peak_vram_mib"] * 1048576 / 1e6)
        close(row["gpu_idle_baseline_mb"], bench["baseline_vram_mib"] * 1048576 / 1e6)
        log = (ROOT / f"results/raw/{name}-perplexity.log").read_text(encoding="utf-8-sig")
        close(re.search(r"Final estimate: PPL = ([0-9.]+)", log).group(1), ppl["perplexity"])
        close(row["perplexity"], ppl["perplexity"])
        assert ppl["dataset_sha256"] == read_json("datasets/wiki.test.metadata.json")["sha256"]
        assert mmlu["dataset_revision"] == "b189ec765aa7ed75c8acfea42df31fdae71f97be"
        assert mmlu["n_samples"] == harness["n-samples"]["mmlu_pro_direct"]["effective"] == 12032
        metrics = harness["results"]["mmlu_pro_direct"]
        close(mmlu["mmlu_pro_score"], metrics["exact_match,letter-only"])
        close(row["mmlu_pro_score"], mmlu["mmlu_pro_score"])
        close(row["mmlu_pro_stderr"], metrics["exact_match_stderr,letter-only"])
        base = cases[(row["model"], "NATIVE")]
        formulas = {
            "size_reduction_percent": (1 - float(row["size_bytes"]) / float(base["size_bytes"])) * 100,
            "vram_reduction_percent": (1 - float(row["peak_vram_mb"]) / float(base["peak_vram_mb"])) * 100,
            "prompt_speedup": float(row["pp512_tps_mean"]) / float(base["pp512_tps_mean"]),
            "generation_speedup": float(row["tg128_tps_mean"]) / float(base["tg128_tps_mean"]),
            "ppl_delta": float(row["perplexity"]) - float(base["perplexity"]),
            "ppl_increase_percent": (float(row["perplexity"]) / float(base["perplexity"]) - 1) * 100,
            "mmlu_retention_percent": float(row["mmlu_pro_score"]) / float(base["mmlu_pro_score"]) * 100,
        }
        for key, value in formulas.items():
            close(row[key], value)
        if row["quantization"] == "Q2_K":
            repeat = (ROOT / f"results/raw/{name}-perplexity-repeat.log").read_text(encoding="utf-8-sig")
            close(re.search(r"Final estimate: PPL = ([0-9.]+)", repeat).group(1), ppl["perplexity"])

    pattern = re.compile(r"^\s*(?:(?i:answer)\s*:\s*)?([A-J])\b")
    groups = collections.defaultdict(dict)
    targets, cache_keys = {}, {}
    total = 0
    with (ROOT / "analysis/mmlu_por_questao_recuperado.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            case = row["model"], row["quantization"]
            assert case in cases
            question = row["question_id"]
            assert question not in groups[case]
            match = pattern.search(row["response"])
            answer = match.group(1) if match else ""
            assert answer == row["extracted"]
            correct = int(answer == row["target"])
            assert correct == int(row["correct"])
            assert targets.setdefault(question, row["target"]) == row["target"]
            assert cache_keys.setdefault(question, row["cache_key"]) == row["cache_key"]
            groups[case][question] = (correct, not bool(match))
            total += 1
    assert total == 120320 and len(targets) == len(set(cache_keys.values())) == 12032
    counts = {(r["model"], r["quantization"]): r for r in read_csv("analysis/mmlu_contagens.csv")}
    assert set(groups) == set(cases) == set(counts)
    for case, entries in groups.items():
        assert len(entries) == 12032
        count = sum(v[0] for v in entries.values())
        invalid = sum(v[1] for v in entries.values())
        assert count == int(counts[case]["correct"])
        assert invalid == int(counts[case]["invalid"])
        close(count / 12032, cases[case]["mmlu_pro_score"])
        close(count / 12032, counts[case]["accuracy"])
    paired = read_csv("analysis/mmlu_pareado_descritivo.csv")
    assert len(paired) == 8
    for row in paired:
        base = groups[(row["model"], "NATIVE")]
        quant = groups[(row["model"], row["quantization"])]
        transitions = collections.Counter((base[q][0], quant[q][0]) for q in base)
        for key, pair in (("both_correct", (1, 1)), ("native_correct_quant_wrong", (1, 0)), ("native_wrong_quant_correct", (0, 1)), ("both_wrong", (0, 0))):
            assert int(row[key]) == transitions[pair]
        assert int(row["net_correct"]) == transitions[(0, 1)] - transitions[(1, 0)]
    figures = read_json("plots/valores_graficos.json")
    metrics = ("file_size_gb", "peak_vram_mb", "pp512_tps_mean", "tg128_tps_mean", "ppl_increase_percent", "mmlu_retention_percent")
    for filename, key in zip(sorted(figures), metrics):
        assert (ROOT / "plots" / filename).stat().st_size > 10000
        for model, values in figures[filename].items():
            for quant, value in zip(("NATIVE", "Q8_0", "Q6_K", "Q4_K_M", "Q2_K"), values):
                close(cases[(model, quant)][key], value)
    for path in (ROOT / "scripts").glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
    ast.parse((ROOT / "configs/mmlu_pro_direct_utils.py").read_text(encoding="utf-8"))
    print("OK: hashes do pacote; 10 configurações; 5 amostras por teste; normalizações; 120.320 respostas; 8 transições pareadas; 6 figuras; sintaxe Python. Nenhum experimento executado.")


if __name__ == "__main__":
    main()
