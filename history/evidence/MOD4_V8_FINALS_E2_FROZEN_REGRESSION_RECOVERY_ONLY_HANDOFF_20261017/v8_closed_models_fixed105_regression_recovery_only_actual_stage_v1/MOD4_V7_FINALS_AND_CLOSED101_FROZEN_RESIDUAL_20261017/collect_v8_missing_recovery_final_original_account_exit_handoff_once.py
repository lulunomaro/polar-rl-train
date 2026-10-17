"""One bounded sequential read; fetch only missing recovery final, reuse complete E2 evidence."""
from pathlib import Path
import importlib.util,sys,os,json,time,getpass,traceback
J=Path(__file__).resolve().parent;R=J/'reports';W=J.parent;G=W/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017';sys.path.insert(0,str(G))
from deploy_v7_closed_finals_v8_healthy_native_after_frozen22of64_original_handoff_once import a,SOURCE,ROOTS
sp=importlib.util.spec_from_file_location('existing_final_read_functions_only',G/'collect_existing_v5_actual_terminal_original_handoff_bounded_missing_final_only_once.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as p:json.dump(v,p,indent=2)
def main():
 put('V8_MISSING_RECOVERY_FINAL_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,one_source_then_one_target_connection_no_poll=True,only_missing_recovery_final_no_old_PT_or_raw_rehash_download=True))
 previous=json.loads((R/'V8_EXISTING_IMMUTABLE_FINALS_ORIGINAL_COST_EXIT_1400_BOUND_COLLECTION_ACTUAL.json').read_bytes());v={};models={'e2':previous['downloaded_final_models']['e2']};pw=getpass.getpass('Host72 missing own recovery final and original account only (hidden): ');c=None
 try:c=a.t.connect();v['owner']=a.code(c,a.t.PY,f.READ,SOURCE,'owner');v['account']=a.code(c,a.t.PY,f.ACCOUNT)
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;metadata_only=f.READ.replace("if key!='owner' and f.is_file():","if False and f.is_file():");assert metadata_only!=f.READ
  v['e2']=a.code(c,a.PY,metadata_only,ROOTS['e2'],'e2');actual_final=next(x['value'] for x in v['e2']['files'] if x['path'].endswith('/production/FINAL.json'));assert actual_final['passed'] and actual_final['final']['SHA']==models['e2'][0]['SHA'] and actual_final['final']['bytes']==models['e2'][0]['bytes'];models['e2'][0]['previous_complete_1400_PT_reused_not_remote_rehashed_or_downloaded']=True
  v['recovery']=a.code(c,a.PY,f.READ,ROOTS['recovery'],'recovery');models['recovery']=[]
  if v['recovery']['models']:
   folder=J/'actual_safe72_closed_finals/recovery';folder.mkdir(parents=True,exist_ok=True);sf=c.open_sftp();sf.get_channel().settimeout(90)
   try:
    for row in v['recovery']['models']:
     p=folder/Path(row['path']).name;tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(row['path'],str(tmp));assert p.parent==folder and tmp.stat().st_size==row['bytes'] and a.H(tmp)==row['SHA'];tmp.replace(p);models['recovery'].append(dict(row,local_path=str(p),twohost_complete_SHA=True))
   finally:sf.close()
 finally:
  pw=None
  if c:c.close()
 done=next((x['value'] for x in v['owner']['files'] if x['path'].endswith('/COHORT_FINAL.json')),None);v.update(epoch=time.time(),downloaded_final_models=models,actual_closed=bool(done and all(models.values()) and all(not v[k]['actual_own_processes'] for k in ('owner','e2','recovery')) and v['account']['original_canonical']['active_segment'] is None and all(x['actual_fcntl_free'] for x in v['account']['actual_locks'])),read_only_no_GPU_budget_signal_or_earlier_once_replay=True,old_complete_E2_not_remote_rehashed_or_downloaded=True)
 put('V8_CLOSED_FINALS_EXACT_CPU_INPUT_BINDING_ACTUAL.json',v);print(json.dumps(dict(actual_closed=v['actual_closed'],models={k:[dict(updates=r['updates'],SHA=r['SHA'],bytes=r['bytes']) for r in rows] for k,rows in models.items()},remaining=v['account']['original_canonical']['remaining_training_seconds'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('V8_MISSING_RECOVERY_FINAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_mutation=True));raise
