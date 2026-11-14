"""Index the retained failed run and quantify its exploration/quality regression."""
import hashlib
import json
from pathlib import Path
import statistics
import time
import torch

T = Path(__file__).resolve().parent
old = T.parent / 'MOD4V3_FLAT_ACCEL_HEIGHT_2H_20261115'
parent = T.parent / 'MOD4V3_FORWARD_JUMP_HEIGHT_2H_20261114/weights/train7200__model_040m.pt'
rows = []
for path in [parent] + [old / 'weights' / ('train_remaining_r3__model_' + suffix + '.pt')
                        for suffix in ('005m', '060m', '110m', 'final')]:
    model = torch.load(path, map_location='cpu', weights_only=False)
    rows.append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     iteration=model['iter'], STD=model['actor_state_dict']['distribution.std_param'].tolist()))
evaluations = []
for folder in sorted(p for p in (old / 'evidence/remote').glob('eval_train_remaining_r3_*') if p.is_dir()):
    path = folder / 'RESULT.json'
    if not path.exists():
        continue
    result = json.loads(path.read_bytes())
    score = statistics.mean(r['rim_peak_m'] * r['flight_quality']
                            if r['sequence_complete'] and not r['failed'] else 0. for r in result['episodes'])
    evaluations.append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            summary=result['summary'], score_m=score))
progress = json.loads((old / 'evidence/remote/train_remaining_r3/LATEST_PROGRESS.json').read_bytes())
report = dict(attempt_id='stable-height-repair-diagnosis-01', epoch=time.time(),
    previous_final_trial='trial-20261115-flat-accel-height2h-final-01',
    previous_final_commit='77e723106d29cdc132cdafa95ab9974b4968a5f0',
    previous_final_report=str(old / 'FINAL_REPORT.md'),
    previous_final_report_sha256=hashlib.sha256((old / 'FINAL_REPORT.md').read_bytes()).hexdigest(),
    checkpoints=rows, fixed_evaluations=evaluations, final_training_counts=progress['task']['counts'],
    observed='STD grew without bounds while every training episode missed settled reward; later deterministic policies regressed',
    repair=['retain H40 actor MLP', 'bounded lower exploration with zero entropy bonus',
            'reset value output and corresponding Adam state for the new reward',
            'lower PPO step size', 'stochastic full-scale reward-feasibility admission',
            'checkpoint comparisons stop persistent severe regressions'],
    no_new_optimizer_updates=True)
(T / 'evidence').mkdir(exist_ok=True)
(T / 'evidence/DIAGNOSIS.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
print(json.dumps(dict(indexed_checkpoints=len(rows), fixed_evaluations=len(evaluations),
                      previous_training_complete=progress['task']['counts']['sequence_complete'])))
