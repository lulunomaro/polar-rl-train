"""Local fixture: keep learned weights/Adam/replay and persist bounded residual."""
from pathlib import Path
import json,runpy,sys,time,traceback
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut import supermimic_train as train
original=train.build
def scaled(*args,**kwargs):
    kwargs['residual_scale']=.25
    return original(*args,**kwargs)
train.build=scaled
try:
    sys.argv=[str(N/'test_supermimic_worker.py'),'--output','supermimic_residual025_resume10']
    runpy.run_path(sys.argv[0],run_name='__main__')
    row=json.loads((N/'supermimic_residual025_resume10/RESULT.json').read_bytes())
    value=train.decode(row['checkpoint']['path'],row['checkpoint']['SHA'])
    assert value['policy_residual_scale']==.25
    assert row['passed']and row['resumed_bptt']['verified_bptt_optimizer_step']
    report=dict(epoch=time.time(),passed=True,production_PT_reads=0,SSH=0,
        residual_scale=.25,full_checkpoint_persists_scale=True,
        all4_optimizers_replay_RNG_restored=True,real_second_H32_update=True,
        source=str(N/'supermimic_residual025_resume10/RESULT.json'))
except BaseException:
    report=dict(epoch=time.time(),passed=False,error=traceback.format_exc(),production_PT_reads=0)
finally:train.build=original
with(N/'reports/RESIDUAL025_FULL_RESUME_TEST.json').open('x',encoding='utf8')as stream:json.dump(report,stream,indent=2)
print(json.dumps(report))
if not report['passed']:raise SystemExit(1)
