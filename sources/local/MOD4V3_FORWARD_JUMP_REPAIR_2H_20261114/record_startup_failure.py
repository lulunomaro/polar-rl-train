"""Record the observed dead evaluator without fabricating a scene-close event."""
import json
from pathlib import Path
import shlex
import sys
T=Path(__file__).resolve().parent
sys.path.insert(0,sys.argv[1])
from ssh72 import connect,execute
root=json.loads((T/'PLAN.json').read_bytes())['root']
script='''
import json,subprocess,time
from pathlib import Path
r=Path(ROOT);name='eval_model_070m';j=r/name
launch=json.loads((r/('LAUNCH_'+name+'.json')).read_text());pid=launch['pid']
proc=Path('/proc')/str(pid)
assert not proc.exists(),'Do not mark a live evaluator failed'
owners=subprocess.run(['nvidia-smi','--query-compute-apps=pid,gpu_uuid','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout
assert str(pid) not in owners
text=(r/(name+'.log')).read_text()
assert 'Fatal Python error: Segmentation fault' in text
assert not (j/'RESULT.json').exists() and not (j/'STARTUP.json').exists()
report=dict(epoch=time.time(),attempt=name,pid=pid,status='startup_failed',
 engine_startup_segmentation_fault_observed=True,process_absent=True,GPU_context_absent=True,
 environment_created=False,evaluated_cases=0,optimizer_created=False,optimizer_updates=0,
 native_exit_code_not_observed=True,checkpoint=launch['cmd'][-1],
 log='eval_model_070m.log',retry_attempt='eval_model_070m_retry1',
 monitor_repair='Recognize recorded startup failure as terminal; no fake SAFE_CLOSED or RESULT')
(j/'STARTUP_FAILED.json').write_text(json.dumps(report,indent=2)+chr(10))
print(json.dumps(report))
'''.replace('ROOT',repr(root))
c=connect()
try:
    status,out,err=execute(c,'python3 -c '+shlex.quote(script),30)
    assert status==0,out+err
    report=json.loads(out)
    (T/'evidence/EVALUATION_STARTUP_REPAIR.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
finally:c.close()
