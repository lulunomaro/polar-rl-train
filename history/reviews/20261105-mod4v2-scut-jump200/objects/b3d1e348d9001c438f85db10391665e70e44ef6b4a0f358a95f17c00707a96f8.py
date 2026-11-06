"""Measure C++ graph dispatch on unchanged learned tensor geometry."""
from pathlib import Path
import json,runpy,sys,time,traceback
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
import mod4v2_scut.supermimic_speed as speed
original_optimizer=speed.enable_fused_adam
out=dict(epoch=time.time(),passed=False,production_PT_reads=0,SSH=0)
def candidate(learner):
    receipt=original_optimizer(learner);receipt['geometry']=speed.enable_scripted_geometry();return receipt
speed.enable_fused_adam=candidate
try:
    source=(N/'benchmark_sampling_total.py').read_text(encoding='utf8')
    source=source.replace("sampling_total_ABBA07","sampling_scripted_ABBA10")
    exec(compile(source,str(N/'benchmark_sampling_total.py'),'exec'),
        {'__file__':str(N/'benchmark_sampling_total.py'),'__name__':'__main__'})
    row=json.loads((N/'sampling_scripted_ABBA10/RESULT.json').read_bytes())
    out.update(passed=row['passed'],result=str(N/'sampling_scripted_ABBA10/RESULT.json'),
        candidate_geometry_pure_tensor=True)
except BaseException:out['error']=traceback.format_exc()
finally:
    speed.enable_fused_adam=original_optimizer
    with(N/'reports/SCRIPTED_GEOMETRY_BENCHMARK_RETRY10.json').open('x',encoding='utf8')as stream:json.dump(out,stream,indent=2)
    print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
