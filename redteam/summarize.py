"""Descriptive audit rank: prescribed directions, absolute weights, cohort SD.

The real future ranking cohort is unavailable. This is an explicitly fixed,
illustrative cohort of audited finite methods, not an asserted future score.
All raw hidden-test scores remain available in the per-case directories.
"""
import json
import math
import statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'redteam'
EXP='synthetic_articulated_gaussians'
metadata=json.loads((AUDIT/'rank_metadata.json').read_text())
# rank_metadata is a verbatim audit-only copy of the original reference schema.
if 'experiments' not in metadata:
    metadata=json.loads((ROOT/'scoring/reference.json').read_text())
def load(p):
    return json.loads(p.read_text())
rows={}
statuses={}
for folder in sorted(AUDIT.iterdir()):
    if not folder.is_dir() or not (folder/'status.json').exists():
        continue
    status=load(folder/'status.json')
    statuses[folder.name]=status
    path=folder/'scores_test.json'
    if status['test_exit'] or not path.exists():
        continue
    results=load(path)['experiments'][EXP]['results']
    if folder.name in results:
        rows[folder.name]=results[folder.name]
anchor=load(AUDIT/'reference_original/scores_test.json')['experiments'][EXP]['results']['reference_original']
finite={n:r for n,r in rows.items() if all(isinstance(v,(int,float)) and math.isfinite(v) for v in r.values())}
schema=metadata['experiments'][EXP]
std={k:statistics.pstdev([r[k] for r in finite.values()]) for k in schema['metrics']}
def rank(row):
    return sum(schema['weight']*abs(m['coefficient'])*(1 if m['higher_is_better'] else -1)*(row[k]-anchor[k])/std[k]
               for k,m in schema['metrics'].items() if std[k]>0)
ranks={n:rank(r) for n,r in finite.items()}
seeds={n:r for n,r in finite.items() if n.startswith('reference_seed')}
spread={k:max(r[k] for r in seeds.values())-min(r[k] for r in seeds.values()) for k in schema['metrics']} if seeds else {}
seed_ranks=[ranks[n] for n in seeds]
summary={'reference':anchor,'scores':rows,'illustrative_rank':ranks,'cohort':list(finite),
         'normalization_sd':std,'metric_seed_range':spread,
         'rank_seed_range':max(seed_ranks)-min(seed_ranks) if seed_ranks else None,
         'statuses':statuses,'unscored_reference_experiments':[e for e in metadata['experiments'] if e!=EXP]}
(AUDIT/'summary.json').write_text(json.dumps(summary,indent=2))
for n,r in rows.items():
    print(n,'quality=',round(r['quality_score'],6),'success=',r['success'],'rank=',round(ranks[n],6) if n in ranks else 'NONFINITE')
print('Seed quality range:', spread.get('quality_score'),'Seed illustrative rank range:',summary['rank_seed_range'])
