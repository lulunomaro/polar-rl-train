"""One explicit finite CPU preparation phase, never a training launcher."""
from pathlib import Path
import argparse,base64,hashlib,importlib.util,json,os,sys,time,traceback
Z=Path(__file__).resolve().parent;T=Z.parent;W=T.parent;R=Z/'reports';ROOT='/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025'
p=argparse.ArgumentParser();p.add_argument('phase',choices=['bootstrap','torch','requirements','check']);args=p.parse_args();PHASE=args.phase
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    assert json.loads((R/'HOST72_WHOLE_MOE_T2Z_SOURCE_EXACT_RETURNED_ACTUAL.json').read_bytes())['source_stage_passed']
    put('HOST72_'+PHASE.upper()+'_FINITE_PHASE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,root=ROOT,CPU_only_no_T2z_training=True))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
    code="""from pathlib import Path
import base64,hashlib,json,os,subprocess,time,shutil
B=Path(v['root']);assert B.resolve()==B and (B/'source/.git').is_dir();assert shutil.disk_usage(B).free>25*1024**3
env=dict(os.environ,CUDA_VISIBLE_DEVICES='',NVIDIA_VISIBLE_DEVICES='none',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
cmd=['nice','-n','19',v['python'],str(B/'engineering_bundle/scripts/prepare_isolated_finite_phases_v2.py'),v['phase'],'--command-timeout','600']
if v['phase']=='bootstrap':cmd+=['--conda','/home/lc01/miniconda3/bin/conda']
started=time.time();error=None
try:
 p=subprocess.run(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=700);rc=p.returncode;raw=p.stdout
except subprocess.TimeoutExpired as e:
 rc=124;raw=e.stdout or b'';error='Own finite preparation phase timed out700s; no training process signaled'
log=B/'receipts'/('ROOT_'+v['phase'].upper()+'_FULL_STDOUT_STDERR_ACTUAL.log')
with log.open('xb') as f:f.write(raw)
result=dict(epoch=time.time(),phase=v['phase'],actual_returncode=rc,phase_passed=rc==0,error=error,elapsed_seconds=time.time()-started,root=str(B),fresh_free_bytes=shutil.disk_usage(B).free,no_GPU_model_load_or_training=True,no_original_mod4_environment_or_budget_write=True)
with (B/'receipts'/('ROOT_'+v['phase'].upper()+'_ACTUAL.json')).open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
result['texts']=[]
for p in sorted((B/'receipts').iterdir()):
 if not p.is_file():continue
 raw=p.read_bytes();result['texts'].append(dict(relative=p.name,path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode()))
print(json.dumps(result))
"""
    try:result=d.code(c,d.PY72,code,dict(root=ROOT,python=d.PY72,phase=PHASE),timeout=750)
    finally:c.close()
    dest=Z/'actual_host72_preparation_texts'/PHASE;dest.mkdir(parents=True)
    for row in result['texts']:
        raw=base64.b64decode(row.pop('base64'));assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
        with (dest/row['relative']).open('xb') as f:f.write(raw)
    put('HOST72_'+PHASE.upper()+'_FINITE_PHASE_RETURNED_ACTUAL.json',result);print(json.dumps({k:v for k,v in result.items() if k!='texts'}))
except BaseException:
    put('HOST72_'+PHASE.upper()+'_ORIGINAL_TRANSPORT_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_training_or_existing_environment_change=True));raise
