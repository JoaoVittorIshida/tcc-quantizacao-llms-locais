"""Cópias dos seis gráficos: mesmos dados, correção de rótulos sobrepostos/cortados."""
import csv
import importlib.util
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'plots'
OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('consolidacao',ROOT/'scripts/results.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
rows=mod.make_rows()
csvrows=list(csv.DictReader((ROOT/'analysis/results.csv').open(encoding='utf-8')))
for a,b in zip(rows,csvrows):
    for k,v in a.items():
        if isinstance(v,(int,float)):assert v==float(b[k]),k
metrics=[
 ('file_size_gb','Tamanho (GB decimais)','Tamanho dos arquivos','01_size.png',False),
 ('peak_vram_mb','VRAM acima do repouso (MB)','Pico de VRAM','02_vram.png',False),
 ('pp512_tps_mean','Tokens/s','Processamento do prompt (pp512)','03_pp512.png',False),
 ('tg128_tps_mean','Tokens/s','Geração (tg128)','04_tg128.png',False),
 ('ppl_increase_percent','Variação ante o nativo (%)','Perplexidade no WikiText-2','05_perplexity.png',True),
 ('mmlu_retention_percent','Retenção ante o nativo (%)','MMLU-Pro: resposta direta','06_mmlu_pro.png',True),
]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
plotted={}
for key,ylabel,title,filename,percent in metrics:
    fig,ax=plt.subplots(figsize=(9,5.2),dpi=150)
    values={m:[next(r[key] for r in rows if r['model']==m and r['quantization']==q) for q in mod.QUANTS] for m in mod.MODELS}
    plotted[filename]=values
    for model,display in [('gemma3-4b','Gemma 3 4B'),('qwen3-4b','Qwen3-4B')]:
        vals=values[model]
        ax.plot(range(5),vals,marker='o',markersize=7,linewidth=2.3,color=mod.COLORS[model],label=display)
        other=values[mod.MODELS[1] if model==mod.MODELS[0] else mod.MODELS[0]]
        for i,v in enumerate(vals):
            upper=v>other[i] or (v==other[i] and model==mod.MODELS[0])
            label=f'{v:.1f}'+('%' if percent else '')
            ax.annotate(label,(i,v),xytext=(0,9 if upper else -16),textcoords='offset points',ha='center',fontsize=8,color=mod.COLORS[model],bbox={'facecolor':'white','edgecolor':'none','alpha':.88,'pad':.3})
    ax.set_xticks(range(5),('NATIVO','Q8','Q6','Q4','Q2'))
    ax.set_xlabel('Quantização GGUF');ax.set_ylabel(ylabel)
    ax.set_title(title,loc='left',fontweight='bold',pad=15)
    ax.grid(axis='y',alpha=.22)
    if key=='ppl_increase_percent':ax.set_ylim(-17,190)
    elif key=='mmlu_retention_percent':ax.set_ylim(0,110)
    else:ax.set_ylim(0,max(max(v) for v in values.values())*1.12)
    ax.legend(frameon=False,ncol=2,loc='best')
    fig.tight_layout();fig.savefig(OUT/filename,bbox_inches='tight');plt.close(fig)
(OUT/'valores_graficos.json').write_text(json.dumps(plotted,indent=2),encoding='utf-8')
print('Seis cópias geradas; valores idênticos ao CSV.')
