"""Own startup failure text/terminal/account snapshot only; never model or rearm."""
from pathlib import Path
import sys,json,time,traceback,importlib.util
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
TEXT=r'''from pathlib import Path
import json,psutil,time
B=Path(v['root']);result=dict(root=str(B),files={},own_processes={})
def small(p):
 if not p.is_file():return None
 assert p.stat().st_size<=16000000
 raw=p.read_bytes()
 if p.suffix=='.json':return json.loads(raw)
 return dict(bytes=len(raw),text=raw.decode('utf8','replace')[-180000:],bounded_tail=len(raw)>180000)
if v['role']=='owner':
 names=['OWNER_IDENTITY.json','OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','owner_CONSOLE.log']
else:
 names=['NODE_IDENTITY.json','NODE_CURRENT.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','node_CONSOLE.log','job0/production_STARTED_ACTUAL.json','job0/production_WAITED_EXIT_ACTUAL.json','job0/production_WORKER.log']
 names += [p.relative_to(B).as_posix() for p in B.glob('H1_PHASE_ORIGINAL_ERROR_*.json')]
 names += [p.relative_to(B).as_posix() for p in (B/'job0/production').glob('*ORIGINAL_ERROR*.json')]
 names += ['job0/production/FINAL.json','job0/production/APP_CLOSING.json','job0/production/NATIVE87_ACTUAL_BEFORE_FIRST_CONTROL_ADMISSION.json','job0/production/NATIVE87_ACTUAL_GPU_PRECONTROL_ADMISSION.json']
for name in dict.fromkeys(names):
 p=B/name;assert p.resolve().is_relative_to(B.resolve());x=small(p)
 if x is not None:result['files'][name]=x
identity=result['files'].get('OWNER_IDENTITY.json' if v['role']=='owner' else 'NODE_IDENTITY.json')
if identity:
 try:
  p=psutil.Process(identity['pid']);same=p.create_time()==identity['creation'];result['own_processes']['identity']=dict(pid=p.pid,same_creation=same,actual_original_out=not same)
  if same:result['own_processes']['identity'].update(exe=p.exe(),argv=p.cmdline(),cwd=p.cwd())
 except psutil.NoSuchProcess:result['own_processes']['identity']=dict(pid=identity['pid'],actual_original_out=True)
if v['role']=='owner':
 C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());a=c['active_segment'];segments=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==identity['pid']]
 result['original_account_snapshot']=dict(remaining=c['remaining_training_seconds'],mode=c['budget_mode'],generation=c['authority_generation'],active_segment=a,completed_own_segments=segments,no_account_write=True)
result.update(epoch=time.time(),no_model_raw_GPU_or_unknown_peer_query=True,no_rearm_or_account_write=True)
print(json.dumps(result))'''
def main():
    q=json.loads((R/'AVAILABLE_TWO_NATIVE87R2_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes())
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    sp=importlib.util.spec_from_file_location('native87R2_existing_memory_error_reader',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None;rows={}
    try:
        c=d.connect72(secret)
        for key,root,role in [('owner',q['owner_root'],'owner'),('recovery',q['roots']['recovery'],'node')]:
            value=d.code(c,d.PY72,TEXT,dict(root=root,role=role),timeout=90);rows[key]=value;put('NATIVE87R2_'+key.upper()+'_OWN_STARTUP_ERROR_TEXT_RETURNED_ACTUAL.json',value)
        c.close();c=None;c=route.connect();value=d.code(c,route.PY,TEXT,dict(root=q['roots']['h1'],role='node'),timeout=90);rows['h1']=value;put('NATIVE87R2_H1_OWN_STARTUP_ERROR_TEXT_RETURNED_ACTUAL.json',value)
        put('NATIVE87R2_ALL_OWN_STARTUP_ERROR_TEXT_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,rows=rows,no_model_or_rearm=True))
        print(json.dumps(dict(actual_finite_returned=True,owner_files=list(rows['owner']['files']),target_files={k:list(rows[k]['files']) for k in ('h1','recovery')},account=rows['owner']['original_account_snapshot'])))
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        put('NATIVE87R2_STARTUP_ERROR_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_model_or_rearm=True));raise
