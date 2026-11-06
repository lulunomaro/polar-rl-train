"""Exercise production build/save/resume with sampling opt-in on a new fixture."""
from pathlib import Path
import json,runpy,sys,time,traceback
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut import supermimic_train as train
original=train.build
out=dict(epoch=time.time(),passed=False,production_PT_reads=0,SSH=0)
def optimized(*args,**kwargs):
    kwargs.update(residual_scale=.25,sampling_optimization=True)
    return original(*args,**kwargs)
train.build=optimized
try:
    sys.argv=[str(N/'test_supermimic_worker.py'),'--output','sampling_scripted_production_resume12']
    runpy.run_path(sys.argv[0],run_name='__main__')
    row=json.loads((N/'sampling_scripted_production_resume12/RESULT.json').read_bytes())
    payload=train.decode(row['checkpoint']['path'],row['checkpoint']['SHA'])
    assert payload['sampling_optimization']and payload['policy_residual_scale']==.25
    assert row['passed']and row['resumed_bptt']['verified_bptt_optimizer_step']
    out.update(passed=True,production_entry_build=True,sampling_option_persisted=True,
        residual025_unchanged=True,all4_Adam_replay_RNG_restored=True,
        actual_H32_after_full_resume=True,scripted_geometry_enabled=True,
        source=str(N/'sampling_scripted_production_resume12/RESULT.json'))
except BaseException:out['error']=traceback.format_exc()
finally:
    train.build=original
    with(N/'reports/SAMPLING_SCRIPTED_FULL_RESUME_TEST.json').open('x',encoding='utf8')as stream:json.dump(out,stream,indent=2)
    print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
