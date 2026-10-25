from pathlib import Path
import base64,hashlib,importlib.util,json,os,sys,time,traceback
Z=Path(__file__).resolve().parent;T=Z.parent;W=T.parent;R=Z/'reports';ROOT='/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
H=lambda b:hashlib.sha256(b).hexdigest()
try:
    closed=json.loads((T/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025/reports/BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert closed['owner_node_workers_all_actual_out'] and closed['original_canonical_cost_settled']
    rows=[];local={}
    for p in sorted((Z/'engineering_agent').rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        rel='engineering_bundle/'+p.relative_to(Z/'engineering_agent').as_posix();raw=p.read_bytes();assert len(raw)<5*1024**2;rows.append(dict(relative=rel,bytes=len(raw),SHA=H(raw)));local[rel]=p
    p=Z/'root_preparation_sources/prepare_isolated_finite_phases_v2.py';raw=p.read_bytes();rel='engineering_bundle/scripts/prepare_isolated_finite_phases_v2.py';rows.append(dict(relative=rel,bytes=len(raw),SHA=H(raw)));local[rel]=p
    put('HOST72_MOE_SOURCE_PREPARATION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,root=ROOT,files=rows,source_only_no_GPU_training_or_budget_write=True))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
    try:
        begin=d.code(c,d.PY72,"from pathlib import Path;import json,os,shutil,time,psutil;B=Path(v['root']);base=Path('/home/lc01/Zonglin Li/zonglin2');assert B.parent==base/'research' and not B.exists();assert shutil.disk_usage(base).free>25*1024**3+sum(r['bytes'] for r in v['rows']);assert psutil.virtual_memory().available>8*1024**3;B.mkdir(parents=True);assert B.resolve()==B;(B/'receipts').mkdir();[(B/r['relative']).parent.mkdir(parents=True,exist_ok=True) for r in v['rows']];print(json.dumps(dict(epoch=time.time(),root=str(B),fresh_free_bytes=shutil.disk_usage(B).free,RAM_available_bytes=psutil.virtual_memory().available,conda_candidates={p:Path(p).is_file() for p in ['/home/lc01/miniconda3/bin/conda','/opt/anaconda3/bin/conda']},CPU_only_no_GPU_query=True)))",dict(root=ROOT,rows=rows),timeout=45)
        put('HOST72_MOE_EXACT_NEW_ROOT_CAPACITY_AND_CONDA_METADATA_ACTUAL.json',begin)
        sf=c.open_sftp();sf.get_channel().settimeout(60)
        try:
            for row in rows:sf.put(str(local[row['relative']]),ROOT+'/'+row['relative'])
        finally:sf.close()
        code="""from pathlib import Path
import base64,hashlib,json,os,subprocess,time
B=Path(v['root']);rows=v['rows']
for r in rows:
 p=B/r['relative'];assert p.resolve().is_relative_to(B) and not p.is_symlink();raw=p.read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['SHA']
receipt=B/'receipts/ROOT_SOURCE_BUNDLE_EXACT_SHA_ACTUAL.json'
with receipt.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),files=rows,all_bytes_SHA_verified=True),f,indent=2)
env=dict(os.environ,CUDA_VISIBLE_DEVICES='',NVIDIA_VISIBLE_DEVICES='none',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
cmd=['nice','-n','19',v['python'],str(B/'engineering_bundle/scripts/prepare_isolated_finite_phases_v2.py'),'source','--command-timeout','300']
p=subprocess.run(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=400)
log=B/'receipts/ROOT_SOURCE_FULL_STDOUT_STDERR_ACTUAL.log'
with log.open('xb') as f:f.write(p.stdout)
texts=[]
for pth in sorted((B/'receipts').iterdir()):
 if not pth.is_file():continue
 raw=pth.read_bytes();texts.append(dict(relative=pth.name,path=str(pth),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode()))
print(json.dumps(dict(epoch=time.time(),actual_returncode=p.returncode,source_stage_passed=p.returncode==0,root=str(B),texts=texts,no_GPU_model_load_or_training=True,no_original_mod4_environment_or_budget_write=True)))
"""
        result=d.code(c,d.PY72,code,dict(root=ROOT,rows=rows,python=d.PY72),timeout=450)
    finally:c.close()
    target=Z/'actual_host72_preparation_texts/source';target.mkdir(parents=True)
    for row in result['texts']:
        raw=base64.b64decode(row.pop('base64'));assert len(raw)==row['bytes'] and H(raw)==row['SHA']
        with (target/row['relative']).open('xb') as f:f.write(raw)
    put('HOST72_WHOLE_MOE_T2Z_SOURCE_EXACT_RETURNED_ACTUAL.json',result);print(json.dumps({k:v for k,v in result.items() if k!='texts'}))
except BaseException:
    put('HOST72_MOE_SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_training_or_existing_env_mutation=True));raise
