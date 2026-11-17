"""Auditoria retrospectiva; somente lê os experimentos e grava novos derivados em analysis/reproduced_audit.

Executar com .venv/Scripts/python.exe, pois pyarrow está no ambiente experimental.
Não carrega modelos nem inicia inferência.
"""
import csv
import hashlib
import io
import json
import math
import pickle
import os
import re
import sqlite3
from pathlib import Path
import pyarrow as pa

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "reproduced_audit"
REV = 'b189ec765aa7ed75c8acfea42df31fdae71f97be'
DATA = Path(os.environ['TCC_MMLU_ARROW']) if os.environ.get('TCC_MMLU_ARROW') else Path.home()/'.cache/huggingface/datasets/TIGER-Lab___mmlu-pro/default/0.0.0'/REV/'mmlu-pro-test.arrow'
PATTERN = re.compile(r'^\s*(?:(?i:answer)\s*:\s*)?([A-J])\b')

class StringsOnly(pickle.Unpickler):
    def find_class(self, module, name):
        raise ValueError('Objeto inesperado no cache')

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    docs = pa.ipc.open_stream(pa.memory_map(str(DATA), 'r')).read_all().to_pylist()
    assert len(docs) == 12032
    assert len({d['question_id'] for d in docs}) == 12032
    kwargs = dict(until=['\n'], max_gen_toks=8, do_sample=False, temperature=0.0)
    keys = []
    for d in docs:
        options = '\n'.join(f'{"ABCDEFGHIJ"[i]}. {o.strip()}' for i, o in enumerate(d['options']))
        prompt = ('Choose the best answer. Reply with only its capital letter (A-J), '
                  'without explanation.\n\n'+f"Question: {d['question'].strip()}\nOptions:\n{options}\nAnswer:")
        chat = json.dumps([dict(role='user', content=prompt)], ensure_ascii=False)
        keys.append(hashlib.sha256(json.dumps(['generate_until', [chat], kwargs]).encode()).hexdigest())
    assert len(set(keys)) == 12032
    rows = list(csv.DictReader((ROOT/'analysis/results.csv').open(encoding='utf-8')))
    paired, scores, inventory = [], [], []
    with (OUT/'mmlu_por_questao_recuperado.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['model','quantization','question_id','category','cache_key','target','response','extracted','correct'])
        writer.writeheader()
        for model in ('gemma3-4b', 'qwen3-4b'):
            base = None
            for quant in ('native','q8_0','q6_k','q4_k_m','q2_k'):
                name = f'{model}-{quant}'
                db = ROOT/'results/processed'/f'{name}-mmlu-full-cache_rank0.db'
                with sqlite3.connect(db.resolve().as_uri()+'?mode=ro', uri=True) as con:
                    cache = {k: StringsOnly(io.BytesIO(v)).load() for k,v in con.execute('SELECT key,value FROM unnamed')}
                assert set(keys) == set(cache), name
                assert all(isinstance(v,str) for v in cache.values())
                correct, invalid = [], 0
                for d,k in zip(docs, keys):
                    match = PATTERN.search(cache[k])
                    ans = match.group(1) if match else ''
                    ok = ans == d['answer']
                    correct.append(ok)
                    invalid += not bool(match)
                    writer.writerow(dict(model=model, quantization=quant.upper(), question_id=d['question_id'], category=d['category'], cache_key=k, target=d['answer'], response=cache[k], extracted=ans, correct=int(ok)))
                row = next(r for r in rows if r['model']==model and r['quantization']==quant.upper())
                assert math.isclose(sum(correct)/12032, float(row['mmlu_pro_score']), abs_tol=1e-15)
                if base is None:
                    base = correct
                else:
                    both = sum(b and q for b,q in zip(base,correct))
                    lost = sum(b and not q for b,q in zip(base,correct))
                    gained = sum(q and not b for b,q in zip(base,correct))
                    neither = sum(not b and not q for b,q in zip(base,correct))
                    assert both+lost+gained+neither == 12032
                    assert gained-lost == sum(correct)-sum(base)
                    paired.append(dict(model=model, quantization=quant.upper(), both_correct=both, native_correct_quant_wrong=lost, native_wrong_quant_correct=gained, both_wrong=neither, net_correct=gained-lost))
                scores.append(dict(model=model,quantization=quant.upper(),n=12032,correct=sum(correct),invalid=invalid,accuracy=sum(correct)/12032))
                inventory.append(dict(file=str(db.relative_to(ROOT)),sha256=sha(db),entries=len(cache)))
    for filename, records in [('mmlu_contagens.csv',scores),('mmlu_pareado_descritivo.csv',paired)]:
        with (OUT/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
    checks=[]
    for row in rows:
        name=f"{row['model']}-{row['quantization'].lower()}"
        raw=json.loads((ROOT/'results/raw'/f'{name}-bench.json').read_text())
        proc=json.loads((ROOT/'results/processed'/f'{name}-benchmark.json').read_text())
        for prefix,field,nprompt,ngen in [('pp512','pp512_tps_mean',512,0),('tg128','tg128_tps_mean',0,128)]:
            b=next(x for x in raw if x['n_prompt']==nprompt and x['n_gen']==ngen)
            assert b['avg_ts']==float(row[field])==proc[field]
            assert len(b['samples_ts'])==5
            assert b['stddev_ts']==float(row[prefix+'_tps_std'])
        assert math.isclose(float(row['peak_vram_mb']),proc['peak_vram_above_baseline_mib']*1048576/1e6)
        text=(ROOT/'results/raw'/f'{name}-perplexity.log').read_text(encoding='utf-8-sig')
        val=float(re.search(r'Final estimate: PPL = ([0-9.]+)',text).group(1))
        assert val==float(row['perplexity'])
        log=(ROOT/'results/raw'/f'{name}-mmlu-full-server.log').read_text(encoding='utf-8-sig')
        assert log.count('stop processing: n_tokens')==12032
        assert not re.search(r'truncated = [1-9]',log)
        checks.append(dict(configuration=name,raw_csv_agree=True,server_releases=12032,truncated_nonzero=0))
    meta=json.loads((ROOT/'datasets/wiki.test.metadata.json').read_text())
    assert sha(ROOT/'datasets/wiki.test.raw')==meta['sha256']
    report=dict(date='2026-10-16',dataset_revision=REV,dataset_cache_file=DATA.name,dataset_arrow_sha256=sha(DATA),rows=12032,unique_ids=12032,matching_keys_per_configuration=12032,recovered_rows=120320,all_scores_reproduce_csv=True,statistical_tests_performed=False,cache_files=inventory,checks=checks,experimental_sources_sha256={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'analysis/results.csv',ROOT/'analysis/validation.csv',ROOT/'environment.txt',ROOT/'results/raw/quantization_manifest.csv',ROOT/'configs/mmlu_pro_direct.yaml',ROOT/'configs/mmlu_pro_direct_utils.py']})
    (OUT/'auditoria_dados.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(scores=scores,paired=paired,checks='OK'),ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
