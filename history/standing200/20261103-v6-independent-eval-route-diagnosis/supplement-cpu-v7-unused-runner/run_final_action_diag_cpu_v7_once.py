"""Unused finite CPU-only diagnosis runner, never restarts standing training.

Requires all local known controllers gone, original canonical inactive and
original resource locks free. The helper itself performs the single necessary
model decode for action diagnosis, not for Git or another skill evaluation.
"""
from pathlib import Path
import hashlib,json,re,sys,time,traceback
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
from check_four4090_once import local_rows
from stage_start_standing200_v6 import run

def put(name,value):
    with(R/'reports'/name).open('x',encoding='utf-8')as f:json.dump(value,f,indent=2)

EXECUTE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,subprocess,time
J=Path(v['job']);D=J/'source_checks/standing200_actiondiag_v7'
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
locks=[]
try:
 for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock']:
  f=p.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 canonical=json.loads(C.read_bytes());assert canonical['active_segment']is None
 assert canonical['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
 exited=json.loads((J/'OWNER_EXIT.json').read_bytes())
 assert exited['run_id']==v['run_id']and exited['all_own_waited']and exited['original_cost_settled']and exited['original_leases_released']
 final=json.loads((J/'production/FINAL.json').read_bytes());assert final['checkpoint']['SHA']==v['final_SHA']and final['native_BPTT_steps']==1019
 evaluated=json.loads((J/'evaluation/RESULT.json').read_bytes());assert evaluated['cases']==80 and evaluated['strict_successes']==0
 assert not D.exists();D.mkdir(parents=True)
 source=v['helper_source'].encode('utf-8');assert hashlib.sha256(source).hexdigest()==v['helper_SHA']
 script=D/'diagnose_final_action_cpu_v7.py';script.write_bytes(source)
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMP_NUM_THREADS='4')
 for k in ['PYTHONPATH','PYTHONHOME','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE']:env.pop(k,None)
 with(D/'STDOUT.txt').open('xb')as out,(D/'STDERR.txt').open('xb')as err:
  p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-B',str(script),'--job',str(J),'--output',str(D/'result')],
   cwd=J,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL)
  rc=p.wait()
 report=D/'result/ACTION_DECOMPOSITION.json'
 result=json.loads(report.read_bytes())if report.exists()else None
 print(json.dumps(dict(epoch=time.time(),returncode=rc,own_waited=True,sourceSHA=v['helper_SHA'],
  result=result,stderr=(D/'STDERR.txt').read_text(errors='replace')[-8000:],
  stdout=(D/'STDOUT.txt').read_text(errors='replace')[-1500:],canonical_writes=0,original_locks_released_in_finally=True)))
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
'''

def main():
    assert not(R/'reports/FINAL_ACTION_DIAG_CPU_V7_ONCE.json').exists()
    assert(R/'reports/CLOSED_ACTUAL_EVALUATION_TRANSFER.json').exists()
    w=json.loads((R/'CURRENT_WORK_ORDER.json').read_bytes())
    assert w['run_id']=='MOD4_STANDING200_RLBPTT_V6_1793639156617427400'
    rows,blocked=local_rows()
    pat=r'MOD4_H1|RMPOLAR|watch|run_once_after_resume|E1.*collect|prepare_archive|single_gpu|collect_nine|collect_generic|collect_actual|stage_new|dispatch|retention|(?<![a-z])PAIR[0-9_]*(?![a-z])'
    relevant=[r for r in blocked if re.search(pat,r.get('CommandLine')or'',re.I)]
    if relevant:print(json.dumps(dict(blocked=relevant,network=0,once_consumed=False)));return
    put('FINAL_ACTION_DIAG_CPU_V7_ONCE.json',dict(epoch=time.time(),run_id=w['run_id'],rows=rows,CPU_purpose='measured leftcrank constant clipping diagnosis'))
    c=None
    try:
        sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'))
        from project_connector import connect72
        c=connect72();raw=(R/'diagnose_final_action_cpu_v7.py').read_bytes()
        result=run(c,EXECUTE,dict(job=w['remote_job'],run_id=w['run_id'],final_SHA=w['latest_checkpoint']['SHA'],helper_source=raw.decode('utf-8'),helper_SHA=hashlib.sha256(raw).hexdigest()),600)
        put('FINAL_ACTION_DIAG_CPU_V7_ACTUAL.json',result)
        assert result['returncode']==0 and result['result']['passed'],result['stderr']
        print(json.dumps(dict(passed=True,result='reports/FINAL_ACTION_DIAG_CPU_V7_ACTUAL.json',clip_fraction=result['result']['clip_fraction'])))
    except BaseException:
        put('FINAL_ACTION_DIAG_CPU_V7_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
    finally:
        if c is not None:c.close()
        put('FINAL_ACTION_DIAG_CPU_V7_SSH_CLOSED.json',dict(epoch=time.time(),SSHclosed=True,serial='FREE'))

if __name__=='__main__':main()
