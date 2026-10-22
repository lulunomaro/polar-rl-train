from pathlib import Path
import importlib.util,json,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;R=T/'reports';sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
READ=r'''
from pathlib import Path
import hashlib,json,os,psutil,re,shutil,time
base=Path('/home/lc01/Zonglin Li/zonglin2/tasks');rows=[];skips=[]
for item in v['roots']:
 node=Path(item['root']);prod=node/'job0/production';final=Path(item['final_path'])
 if not node.is_dir() or not prod.is_dir():skips.append(dict(root=str(node),reason='no actual directory'));continue
 assert node.resolve().is_relative_to(base.resolve()) and final.parent==prod
 epath=node/'NODE_EXIT_ACTUAL.json';tpath=node/'NODE_TERMINAL_ACTUAL.json'
 if not epath.is_file() or not tpath.is_file():skips.append(dict(root=str(node),reason='no complete node exit/terminal'));continue
 e=json.loads(epath.read_bytes());t=json.loads(tpath.read_bytes())
 if not e.get('actual_all_own_children_waited') or not t.get('row',{}).get('final',{}).get('passed'):skips.append(dict(root=str(node),reason='not a complete passed node'));continue
 if any(p.pid!=os.getpid() and any(a.startswith(str(node)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline'])):skips.append(dict(root=str(node),reason='own stage still active'));continue
 assert final.is_file() and final.stat().st_size==item['final_bytes']
 pts=[]
 for p in prod.glob('model_update*.pt'):
  m=re.fullmatch(r'model_update(\d+)\.pt',p.name)
  if m and p.is_file() and not p.is_symlink():pts.append((int(m.group(1)),p))
 keep={final};keep.update(p for _,p in sorted(pts,reverse=True)[:2]);keep.update(p for n,p in pts if n==1)
 for name in ('FINAL.json','latest_complete.json'):
  p=prod/name
  if p.is_file():
   x=json.loads(p.read_bytes())
   if isinstance(x,dict) and isinstance(x.get('path'),str):keep.add(Path(x['path']))
 candidates=[]
 for n,p in sorted(pts):
  if p in keep:continue
  s=p.stat();candidates.append(dict(path=str(p),bytes=s.st_size,mtime_ns=s.st_mtime_ns,inode=s.st_ino,links=s.st_nlink,update=n))
 rows.append(dict(root=str(node),qualified_final=item,exit_text_SHA=hashlib.sha256(epath.read_bytes()).hexdigest(),terminal_text_SHA=hashlib.sha256(tpath.read_bytes()).hexdigest(),all_own_stage_out=True,kept_model_paths=sorted(map(str,keep)),candidates=candidates))
u=shutil.disk_usage(base)
print(json.dumps(dict(epoch=time.time(),readonly_inventory=True,target_total=u.total,target_free=u.free,original_target_reserve=25*1024**3,free_above_reserve=u.free-25*1024**3,stages=rows,skipped=skips,candidate_count=sum(len(x['candidates']) for x in rows),candidate_bytes=sum(p['bytes'] for x in rows for p in x['candidates']),no_model_hash_download_delete_GPU_or_account_write=True,no_deletion_authorization_inferred=True,keep_all_FINAL_source_first_last2_failed_prefix_raw_text_errors_logs=True)))
'''
def main():
    paths=list(W.glob('MOD4_TWO_LINUX_POLICY50_COHORT_*/reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'))
    paths+=list(T.glob('*/reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'))+list(T.glob('*/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'))
    roots={}
    for p in paths:
        z=json.loads(p.read_bytes())
        if not z.get('passed') or not z.get('original_canonical_cost_settled'):continue
        m=z.get('models',{}).get('recovery')
        if not m:continue
        f=m['final'];root=f['path'].split('/job0/')[0]
        if root.startswith('/home/lc01/Zonglin Li/zonglin2/tasks/'):
            roots[root]=dict(root=root,final_path=f['path'],final_bytes=f['bytes'],final_SHA=f['SHA'],local_complete_CPU_report=str(p))
    assert roots;put('V101_CLOSED72_INTERMEDIATE_PT_INVENTORY_STARTED_ACTUAL.json',dict(epoch=time.time(),roots_count=len(roots),readonly=True,no_delete=True))
    spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=None
    try:
        c=d.connect72(secret);secret=None;result=d.code(c,d.PY72,READ,dict(roots=list(roots.values())),timeout=120);put('V101_CLOSED72_E3_INTERMEDIATE_PT_READONLY_CANDIDATES_ACTUAL.json',result)
        print(json.dumps({k:result[k] for k in ('readonly_inventory','target_free','free_above_reserve','candidate_count','candidate_bytes','no_deletion_authorization_inferred')}))
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:put('V101_CLOSED72_INVENTORY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_delete_or_replay=True));raise
