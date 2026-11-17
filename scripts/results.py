"""Consolidate the ten measured configurations and draw the six plan charts."""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "results" / "processed"
ANALYSIS = ROOT / "analysis"
PLOTS = ANALYSIS / "plots"
MODELS = ("gemma3-4b", "qwen3-4b")
QUANTS = ("NATIVE", "Q8_0", "Q6_K", "Q4_K_M", "Q2_K")
LABELS = ("Native", "Q8", "Q6", "Q4", "Q2")
COLORS = {"gemma3-4b": "#21618c", "qwen3-4b": "#c05a28"}


def read_metric(model, quant, kind):
    path = PROCESSED / f"{model}-{quant.lower()}-{kind}.json"
    if not path.exists():
        raise FileNotFoundError(f"Required completed experiment missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def make_rows():
    rows = []
    for model in MODELS:
        baseline_bench = read_metric(model, "NATIVE", "benchmark")
        baseline_ppl = read_metric(model, "NATIVE", "perplexity")
        baseline_mmlu = read_metric(model, "NATIVE", "mmlu-full")
        base_size = baseline_bench["size_bytes"]
        base_vram = baseline_bench["peak_vram_above_baseline_mib"]
        base_pp = baseline_bench["pp512_tps_mean"]
        base_tg = baseline_bench["tg128_tps_mean"]
        base_ppl = baseline_ppl["perplexity"]
        base_score = baseline_mmlu["mmlu_pro_score"]
        assert base_score > 0, f"Native MMLU-Pro accuracy is zero for {model}"
        for quant in QUANTS:
            bench = read_metric(model, quant, "benchmark")
            ppl = read_metric(model, quant, "perplexity")
            mmlu = read_metric(model, quant, "mmlu-full")
            harness_result = json.loads((ROOT / mmlu["harness_result"]).read_text(encoding="utf-8"))
            harness_metrics = harness_result["results"]["mmlu_pro_direct"]
            mmlu_stderr = harness_metrics["exact_match_stderr,letter-only"]
            assert mmlu["n_samples"] == 12032, (model, quant, mmlu["n_samples"])
            vram_mib = bench["peak_vram_above_baseline_mib"]
            row = {
                "model": model,
                "quantization": quant,
                "size_bytes": bench["size_bytes"],
                "file_size_gb": bench["size_gb"],
                "peak_vram_mb": vram_mib * 1048576 / 1e6,
                "gpu_peak_total_mb": bench["peak_vram_mib"] * 1048576 / 1e6,
                "gpu_idle_baseline_mb": bench["baseline_vram_mib"] * 1048576 / 1e6,
                "pp512_tps_mean": bench["pp512_tps_mean"],
                "pp512_tps_std": bench["pp512_tps_std"],
                "tg128_tps_mean": bench["tg128_tps_mean"],
                "tg128_tps_std": bench["tg128_tps_std"],
                "perplexity": ppl["perplexity"],
                "mmlu_pro_score": mmlu["mmlu_pro_score"],
                "mmlu_pro_stderr": mmlu_stderr,
                "mmlu_pro_n": mmlu["n_samples"],
                "size_reduction_percent": (1 - bench["size_bytes"] / base_size) * 100,
                "vram_reduction_percent": (1 - vram_mib / base_vram) * 100,
                "prompt_speedup": bench["pp512_tps_mean"] / base_pp,
                "generation_speedup": bench["tg128_tps_mean"] / base_tg,
                "ppl_delta": ppl["perplexity"] - base_ppl,
                "ppl_increase_percent": (ppl["perplexity"] / base_ppl - 1) * 100,
                "mmlu_retention_percent": mmlu["mmlu_pro_score"] / base_score * 100,
                "notes": (
                    "Gemma language-only GGUF; " if model == "gemma3-4b" else "Qwen reasoning disabled; "
                ) + "MMLU-Pro zero-shot direct-letter protocol; full 12032 questions",
            }
            rows.append(row)
    return rows


def plot_metric(rows, key, ylabel, title, filename, zero=False, percent=False):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150)
    x = range(len(QUANTS))
    for model, display in (("gemma3-4b", "Gemma 3 4B"), ("qwen3-4b", "Qwen3-4B")):
        values = [float(next(r[key] for r in rows if r["model"] == model and r["quantization"] == q)) for q in QUANTS]
        ax.plot(x, values, marker="o", markersize=7, linewidth=2.3, color=COLORS[model], label=display)
        for xi, value in zip(x, values):
            label = f"{value:.1f}%" if percent else f"{value:.1f}"
            ax.annotate(label, (xi, value), xytext=(0, 8 if model == "gemma3-4b" else -15), textcoords="offset points", ha="center", fontsize=8, color=COLORS[model])
    ax.set_xticks(list(x), LABELS)
    ax.set_xlabel("Quantização GGUF")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontweight="bold", pad=15)
    ax.grid(axis="y", alpha=0.22)
    if zero:
        ax.set_ylim(bottom=0)
    ax.legend(frameon=False, ncol=2, loc="best")
    fig.tight_layout()
    fig.savefig(PLOTS / filename, bbox_inches="tight")
    plt.close(fig)


def main():
    rows = make_rows()
    ANALYSIS.mkdir(exist_ok=True)
    PLOTS.mkdir(exist_ok=True)
    with (ANALYSIS / "results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    plot_metric(rows, "file_size_gb", "Tamanho (GB decimais)", "Tamanho dos arquivos", "01_size.png", zero=True)
    plot_metric(rows, "peak_vram_mb", "VRAM acima do repouso (MB)", "Pico de VRAM", "02_vram.png", zero=True)
    plot_metric(rows, "pp512_tps_mean", "Tokens/s", "Processamento do prompt (pp512)", "03_pp512.png", zero=True)
    plot_metric(rows, "tg128_tps_mean", "Tokens/s", "Geração (tg128)", "04_tg128.png", zero=True)
    plot_metric(rows, "ppl_increase_percent", "Variação ante o nativo (%)", "Perplexidade no WikiText-2", "05_perplexity.png", percent=True)
    plot_metric(rows, "mmlu_retention_percent", "Retenção ante o nativo (%)", "MMLU-Pro: resposta direta", "06_mmlu_pro.png", percent=True)
    print(f"Wrote {ANALYSIS / 'results.csv'} and six plots")


if __name__ == "__main__":
    main()
