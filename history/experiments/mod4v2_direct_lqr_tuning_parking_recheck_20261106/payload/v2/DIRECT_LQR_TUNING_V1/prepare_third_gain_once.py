"""Final third actual gain candidate, declared before its new controlled run.
Original three-condition protocol/results immutable; score/gates unchanged.
"""
from pathlib import Path
import json
D=Path(__file__).resolve().parent;out=D/'THIRD_GAIN_CANDIDATE'
if out.exists():raise RuntimeError('Third gain candidate already prepared')
a=json.loads((D/'TRAIN_SELECTION001/RESULT.json').read_text(encoding='utf-8'))
if a['best_training_name']!='baseline':raise RuntimeError('This branch was for actual failure of higher-rate gains')
p=json.loads((D/'PROTOCOL.json').read_text(encoding='utf-8'))
p.update(id='MOD4V2_DIRECT_LQR_THIRD_GAIN_001',status='fixed_before_third_gain_run',
 scope='Final third gain candidate after original two candidates worsened fixed score;old protocol/results preserved. Increase R4 to reduce feedback bandwidth/noise amplification,not new torqueFF/observer.',
 formal_cases=[dict(id='lqr_effort4',seed=530300,nominal=False,profile='slow',tuning_name='lqr_effort4',tuning=dict(effort_weight=4.))])
p['execution_policy'].update(max_total_changed_gain_candidates=3,no_further_gain_search_in_this_stage=True,
 comparison='Same existing training setting/new distinct gain case,not replay of baseline/oldcase. Fixed original score and5percent selection unchanged.')
s=(D/'run_tuning_case.py').read_text(encoding='utf-8');old='ROOT = Path(__file__).resolve().parents[1]'
if s.count(old)!=1:raise RuntimeError('Unknown runner root')
s=s.replace(old,'ROOT = Path(__file__).resolve().parents[2]',1);compile(s,str(out/'run_tuning_case.py'),'exec')
out.mkdir(exist_ok=False);(out/'run_tuning_case.py').write_text(s,encoding='utf-8');(out/'PROTOCOL.json').write_text(json.dumps(p,indent=2),encoding='utf-8')
(out/'PREEXEC.json').write_text(json.dumps(dict(reason='rateQ4/velocityQ2.25 worsened pitchRMS and fixed score;keep originalQ and useR4',candidate_count_now=3,
 original_score_unchanged=True,models=0,physics=0,no_more_candidates=True),indent=2),encoding='utf-8')
print('FINAL_THIRD_GAIN_READY R4;oldrecords/gates/score unchanged,one new gain run only')
