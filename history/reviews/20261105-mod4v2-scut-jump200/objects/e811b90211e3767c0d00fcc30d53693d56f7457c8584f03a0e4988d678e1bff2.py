"""Add local candidate evidence without changing active run identity or source."""
from pathlib import Path
import json,time
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200'
read=lambda p:json.loads(Path(p).read_bytes())
parity=read(N/'sampling_state_fusion01/RESULT.json')
integration=read(N/'sampling_state_integration02/RESULT.json')
benchmark=read(N/'sampling_state_fullstep04/RESULT.json')
reader=read(N/'reports/SUPERMIMIC_CLOSED_READER_SELFTEST.json')
assert parity['passed']and integration['passed']and benchmark['passed']and reader['passed']
report=dict(epoch=time.time(),status='LOCAL_STATE_READ_CANDIDATE_NOT_SELECTED_FULLSTEP_REGRESSION',
    production_PT_reads=0,SSH=0,active_frozen_run_modified=False,
    parity=dict(path=str(N/'sampling_state_fusion01/RESULT.json'),max_error=4.76837158203125e-7,
        local20k_component_ratio=parity['measurements'][1]['local_component_ratio']),
    real_integration=dict(path=str(N/'sampling_state_integration02/RESULT.json'),
        compared=integration['real_control_endpoints_compared'],H32_fullsave_resume=True),
    fullstep=dict(path=str(N/'sampling_state_fullstep04/RESULT.json'),
        local128_ratio=benchmark['local_fullstep_ratio'],numerical_resets=benchmark['numerical_resets'],
        constraint_resets=benchmark['constraint_resets'],production_candidate_ready=False),
    prior_invalid_benchmark_preserved=str(N/'sampling_state_fullstep03/RESULT.json'),
    local_reader=dict(path=str(N/'reports/SUPERMIMIC_CLOSED_READER_SELFTEST.json'),
        passed=True,production_PT_reads=0,actual_final_diagnosis_not_run=True),
    next='Continue original sole15096 locally. After actual fullsave/80/formal return, use review_supermimic_closed.py --root A once, then native saved-pose review. Do not install this state-reader candidate based on component speed alone.')
with(N/'reports/STATE_FUSION_AND_CLOSED_READER.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
for p in [N.parents[1]/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
    value=read(p)
    value['sampling_state_candidate']=report
    value['supermimic_interleaving']['closed_final_reader']=str(N/'review_supermimic_closed.py')
    value['supermimic_interleaving']['closed_reader_selftest_passed']=True
    value['supermimic_interleaving']['actual_final_review_pending']=True
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(dict(saved=True,active_source_modified=False,local_fullstep_ratio=benchmark['local_fullstep_ratio'])))
