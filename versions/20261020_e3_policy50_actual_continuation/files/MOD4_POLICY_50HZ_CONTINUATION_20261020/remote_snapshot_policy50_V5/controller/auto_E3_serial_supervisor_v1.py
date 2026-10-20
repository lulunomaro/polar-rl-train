"""One authorized serial E3 continuation series, complete saves and pending cost only.

No canonical ledger is copied/opened/written. A durable series lease and per-window
O_EXCL receipts prevent overlap/replay; all source and cost gates precede next GO.
"""
from pathlib import Path
import ast,copy,fcntl,hashlib,json,os,secrets,shutil,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;BASE=B.parent;OWNED=Path('/home/lc01/Zonglin Li/zonglin2');PY=str(OWNED/'run-python.sh');LEASE=OWNED/'state/MOD4_E3_AUTO50_V5_PENDING_SERIES_20261020.json';AUTHORITY='auto-E3-existing-budget-20261020'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def event(kind,**fields):
 with (B/'SERIES_EVENTS.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(dict(epoch=time.time(),kind=kind,**fields))+'\n');f.flush();os.fsync(f.fileno())
def budget_admits(cfg,completed,cap=3900):
 ids=[x['run_id'] for x in completed];assert len(set(ids))==len(ids)
 spent=sum(x['actual_pending_seconds'] for x in completed);assert spent>=0
 available=cfg['last_settled_remaining_seconds']-cfg['legacy_unsettled_reserve_seconds']-cfg['original_safety_reserve_seconds']-cfg['prior_single_E3_pending_seconds']-cfg['prior_100hz_series_pending_seconds']-spent
 return dict(admit=available>=cap,available_after_pending_and_reserves=available,series_actual_pending_seconds=spent,prior_single_E3_pending_seconds=cfg['prior_single_E3_pending_seconds'],original_canonical_settled=False)
def closed_owner_node(owner,node):
 import psutil
 def alive(root):
  out=[]
  for p in psutil.process_iter(['pid','cmdline','create_time']):
   try:
    if p.pid!=os.getpid() and any(x.startswith(str(root)+'/') for x in p.info['cmdline'] or []):out.append(p.info)
   except psutil.Error:pass
  return out
 if not all((root/name).is_file() for root,name in [(owner,'COHORT_FINAL.json'),(owner,'OWNER_EXIT_ACTUAL.json'),(node,'NODE_TERMINAL_ACTUAL.json'),(node,'NODE_EXIT_ACTUAL.json')]):return False
 e=read(node/'NODE_EXIT_ACTUAL.json');t=read(node/'NODE_TERMINAL_ACTUAL.json')['row'];o=read(owner/'OWNER_EXIT_ACTUAL.json')
 return bool(e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and t['terminal_all_own_children_waited'] and o['pending_cost_record_complete'] and not alive(owner) and not alive(node))
def account_host(cfg):
 p=subprocess.run(['ssh-keyscan','-T','5','-t','ed25519',cfg['original_account_host']],capture_output=True,text=True,timeout=20);keys={line.split()[2] for line in p.stdout.splitlines() if len(line.split())>=3 and line.split()[1]=='ssh-ed25519'}
 if keys=={cfg['known_Windows_host_key']}:return 'known_Windows_original_canonical_offline'
 if keys=={cfg['original_Linux_host_key']}:return 'original_Linux_returned_requires_reconciliation'
 return 'unverified_account_host_no_new_GO'
def resources(spec,previous_root):
 import psutil
 assert spec['key']=='recovery' and spec['GPU_UUID']=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
 e=read(previous_root/'NODE_EXIT_ACTUAL.json');t=read(previous_root/'NODE_TERMINAL_ACTUAL.json')['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and t['returncode']==0 and not t['errors'] and t['final']['passed'];locks=[]
 for q in [Path(spec['private_lock']),OWNED/'state/finite_environment_validation.lock']:
  free=False
  with q.open('rb+') as f:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
   except BlockingIOError:pass
  locks.append(dict(path=str(q),actual_fcntl_free=free))
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();gpu=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if spec['GPU_UUID'] in x);disk=shutil.disk_usage(OWNED);ram=psutil.virtual_memory().available
 checks=dict(GPU_empty=not any(spec['GPU_UUID'] in x for x in compute.splitlines()),GPU_free_over7000=int(gpu.split(',')[-1])>7000,RAM_over8GiB=ram>8*1024**3,disk_over25GiB=disk.free>25*1024**3,private_shared_fcntl_free=all(x['actual_fcntl_free'] for x in locks))
 return dict(epoch=time.time(),ready=all(checks.values()),checks=checks,GPU_line=gpu,compute_snapshot=compute,disk_free=disk.free,RAM_available=ram,locks=locks)
def build_window(index,previous_node,previous_owner,previous_spec,source,proof,authority):
 window=BASE/'windows'/('hour'+str(index).zfill(4));node=window/'recovery';owner=window/'owner';assert not window.exists() and window.resolve().is_relative_to(OWNED.resolve());node.mkdir(parents=True);owner.mkdir();old=read(previous_node/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');m=copy.deepcopy(old);spec=copy.deepcopy(previous_spec);oldfilename=old['source_filename'];oldAdam=old['source_Adamstep'];newfilename='RECOVERY_auto_source.pt';newAdam=source['Adam_step'];assert source['SHA']==H(source['path']) and Path(source['path']).stat().st_size==source['bytes']
 for row in old['files']:
  rel=Path(row['relative']);assert (node/rel).resolve().is_relative_to(node.resolve())
  if str(rel).replace('\\','/')=='job0/source/'+oldfilename:continue
  src=previous_node/rel;assert src.is_file() and not src.is_symlink() and src.stat().st_size==row['bytes'] and H(src)==row['SHA'];dst=node/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 (node/'job0/source').mkdir(parents=True,exist_ok=True);shutil.copy2(source['path'],node/'job0/source'/newfilename)
 worker=node/'recovery_worker.py';before=(previous_node/'recovery_worker.py').read_text('utf8');overlay=read(B/'POLICY50_OVERLAY_CONFIG.json');binding=[]
 for change in overlay['changes']:
  rel=change['relative'];src=B/'overlay'/rel;assert H(src)==change['candidate_SHA'];prior=previous_node/rel;assert H(prior) in (change['baseline_SHA'],change['candidate_SHA']) or rel=='recovery_worker.py';dst=node/rel;shutil.copy2(src,dst);binding.append(change)
 old_policy=previous_spec.get('policy_hz',100);after=(B/'overlay/recovery_worker.py').read_text('utf8').replace(str(overlay['worker_baseline_Adam']),str(newAdam));worker.write_text(after,encoding='utf8');put(node/'POLICY50_OVERLAY_BINDING_ACTUAL.json',dict(changes=binding,source_policy_hz=old_policy,policy_hz=50))
 task=read(node/'job0/TASK.json');task.update(policy_clock_migration_authorized=True,source_policy_hz=old_policy,policy_hz=50,id='AUTO_E3_SERIAL_'+str(index),source_SHA=source['SHA'],source_Adamstep=newAdam,source_filename=newfilename,source_owned_updates=source['updates'],source_owned_completed_updates=source['updates'],exact_closed_source_updates=source['updates'],automatic_continuation_authority=AUTHORITY,prior_source_cost_pending_not_canonical_settled=True);put(node/'job0/TASK.json',task)
 # New admission logic is explicit about pending source cost; production bytes stay exact.
 shutil.copy2(B/'policy50_closed_source_CPU_v1.py',node/'closed_production_continuation_CPU_v2.py');shutil.copy2(B/'policy50_native_CPU_v1.py',node/'policy50_native_CPU_v1.py');put(node/'AUTO_CONTINUATION_AUTHORITY.json',authority);put(node/'PREVIOUS_CLOSED_WHOLE_MODEL_CPU_REPORT.json',proof)
 provenance=read(node/'CLOSED_PRODUCTION_SOURCE_PROVENANCE.json');provenance.update(source_SHA=source['SHA'],Adam=newAdam,whole_tensor_counts=[173,96],all_model_runtime_finite=True,actual_original_owner_node_all_children_out=True,original_cost_once_settled=False,explicit_pending_cost_continuation_authorized=True,pending_source_cost_record_complete=True,previous_pending_owner_root=str(previous_owner),previous_pending_run_id=proof['pending_cost']['run_id'],pending_source_cost_canonical_settled=False,whole_model_CPU_report_SHA=H(node/'PREVIOUS_CLOSED_WHOLE_MODEL_CPU_REPORT.json'),previous_source_filename=oldfilename,new_source_filename=newfilename,previous_Adam=oldAdam,actual_previous_updates=source['updates']);put(node/'CLOSED_PRODUCTION_SOURCE_PROVENANCE.json',provenance)
 shutil.copy2(B/'three_slot_common_v1.py',node/'three_slot_common_v1.py')
 m.update(policy_hz=50,source_policy_hz=old_policy,source_SHA=source['SHA'],source_filename=newfilename,source_Adamstep=newAdam,explicit_source_Adam_expectation_changes=True,automatic_continuation_authority=AUTHORITY);m['files']=[x for x in m['files'] if x['relative']!='job0/source/'+oldfilename]
 relatives={x['relative'] for x in m['files']}|{'job0/source/'+newfilename,'AUTO_CONTINUATION_AUTHORITY.json','PREVIOUS_CLOSED_WHOLE_MODEL_CPU_REPORT.json','POLICY50_OVERLAY_BINDING_ACTUAL.json','policy50_native_CPU_v1.py'};m['files']=[dict(relative=rel,bytes=(node/rel).stat().st_size,SHA=H(node/rel)) for rel in sorted(relatives)];put(node/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',m)
 spec.update(policy_hz=50,source_policy_hz=old_policy,source_SHA=source['SHA'],source_filename=newfilename,source_Adamstep=newAdam,manifest_SHA=H(node/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),previous_runtime_root=str(previous_node));put(window/'SPEC_NO_TOKEN.json',spec)
 for local,remote in [('auto_E3_pending_owner_v2.py','three_slot_finite_owner_v1.py'),('three_slot_common_v1.py','three_slot_common_v1.py'),('owner_listener_ready_single_cpu_v1.py','owner_listener_ready_single_cpu_v1.py')]:shutil.copy2(B/local,owner/remote)
 return window,node,owner,spec
def launch(root,entry,cfg):
 p=subprocess.run([PY,'-u','-B',str(root/entry)],input=json.dumps(cfg)+'\n',text=True,capture_output=True,cwd=root,timeout=30);assert p.returncode==0,p.stderr;return json.loads(p.stdout)
def CPU_source(node):
 clock=node/'job0/runtime/isaac/mod4/physics_clock.py';local={};exec(compile(clock.read_text('utf8'),str(clock),'exec'),local);q=local['validate_clock'](.0025,.02);assert q['decimation']==8 and q['policy_hz']==50.;assert read(node/'job0/runtime/train/deploy/contract_rm2025_later.json')['policy_hz']==50;put(node/'POLICY50_ACTUAL_IMPORT_CLOCK_CPU_ACTUAL.json',dict(epoch=time.time(),actual_import_path=str(clock),clock=q,spawn_grace_seconds=.1,before_any_GPU=True))
 p=subprocess.run([PY,'-u','-B',str(B/'target_full_source_sdk_cpu_review.py'),str(node)],capture_output=True,text=True,timeout=240);put(node.parent/'TARGET_SOURCE_CPU_PROCESS_ACTUAL.json',dict(epoch=time.time(),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,actual_waited=True));assert p.returncode==0,p.stderr
def review_closed(owner,node,spec):
 import torch
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();co=read(owner/'COHORT_FINAL.json');assert set(co['go'])=={'recovery'} and co['pending_cost_record_complete'] and co['original_cost_settled'] is False;row=read(node/'NODE_TERMINAL_ACTUAL.json')['row'];assert row['returncode']==0 and not row['errors'] and row['final']['passed'];model=row['final']['final'];assert H(model['path'])==model['SHA'] and Path(model['path']).stat().st_size==model['bytes'];s=torch.load(model['path'],map_location='cpu',weights_only=False);before=torch.load(node/'job0/source'/spec['source_filename'],map_location='cpu',weights_only=False);counts=[0,0]
 def finite(x):
  if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for y in x.values():finite(y)
  elif isinstance(x,(tuple,list)):
   for y in x:finite(y)
 finite(s);assert counts==[173,96] and s['E3_phase']=='production' and not s.get('failed_partial_prefix',False);updates=s['E3_production_updates'];assert updates>0 and updates==model['updates'];states=s['optimizer_state_dict']['state'];assert len(states)==17 and {int(x['step']) for x in states.values()}=={spec['source_Adamstep']+20*updates} and model['Adam_step']==spec['source_Adamstep']+20*updates
 changes={name:[k for k in before[name] if not torch.equal(before[name][k],s[name][k])] for name in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8;pending=co['pending_cost'];cost=pending['cost'];assert not pending['canonical_settled'] and cost['actual_returncode']==0 and cost['duration_bound_passed'] and abs(cost['actual_production_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5;assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();proof=dict(epoch=time.time(),passed=True,final=model,updates=updates,all17Adam_after=model['Adam_step'],whole_tensor_counts=counts,all_model_runtime_finite=True,all17_changes=changes,pending_cost=pending,original_canonical_settled=False,CPU_RNG_unchanged_0CUDA_0optimizer=True,not_skill_qualification=True);put(node.parent/'CLOSED_FINAL_WHOLE_MODEL_CPU_ACTUAL.json',proof);return proof
def main(cfg):
 import psutil
 assert cfg['authority']['id']==AUTHORITY and cfg['authority']['automatic_serial_E3_continuation'] is True and cfg['authority']['no_new_budget'] is True;assert cfg['last_settled_remaining_seconds']==259890.6132156849 and cfg['prior_single_E3_pending_seconds']==3626.8895361423492;assert cfg['original_safety_reserve_seconds']==64800 and cfg['legacy_unsettled_reserve_seconds']==9400.860692501068+512;verify_previous_100hz_series(cfg);assert not LEASE.exists();fd=os.open(LEASE,os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);os.write(fd,json.dumps(dict(epoch=time.time(),series_id=cfg['series_id'],root=str(B),pid=os.getpid(),creation=psutil.Process().create_time(),authority=AUTHORITY,original_canonical_settled=False)).encode());os.fsync(fd);state=dict(series_id=cfg['series_id'],completed=[],active=None,status='initializing',original_canonical_settled=False);put(B/'SERIES_IDENTITY.json',dict(pid=os.getpid(),creation=psutil.Process().create_time(),argv=sys.argv,root=str(B)));source=cfg['initial_source'];previous_node=Path(cfg['initial_node']);previous_owner=Path(cfg['initial_owner']);spec=cfg['initial_spec'];proof=read(B/'INITIAL_SOURCE_WHOLE_CPU_PROOF.json');index=1
 try:
  while True:
   budget=budget_admits(cfg,state['completed']);state['budget_guard']=budget;state['active']=None
   if (B/'STOP_SERIES_AFTER_CURRENT.json').exists():state['status']='requested_stop_at_boundary';break
   if not budget['admit']:state['status']='original_remaining_budget_guard_stop';break
   host=account_host(cfg);state['account_host_state']=host
   if host!='known_Windows_original_canonical_offline':state['status']='account_host_requires_reconciliation_or_identity_review';break
   assert closed_owner_node(previous_owner,previous_node);res=resources(spec,previous_node);state['last_resource_snapshot']=res
   if not res['ready']:
    state['status']='resources_pending_before_new_window';put(B/'SERIES_CURRENT.json',dict(epoch=time.time(),**state));event('resource_wait_before_new_root',resource=res)
    until=time.monotonic()+900
    while time.monotonic()<until and not (B/'STOP_SERIES_AFTER_CURRENT.json').exists():time.sleep(3)
    continue
   window,node,owner,newspec=build_window(index,previous_node,previous_owner,spec,source,proof,cfg['authority']);CPU_source(node);qualify_clock_native(node,newspec) if newspec['source_policy_hz']==100 else None;runid=cfg['series_id']+'_hour'+str(index).zfill(4);token=secrets.token_hex(32);owner_cfg=dict(role='owner',experts={'recovery':newspec},approval_id=AUTHORITY,explicit_offline_cost_approval=True,expected_source_SHA=source['SHA'],deferred_experts=['h1','e2'],run_id=runid,token=token);oid=launch(owner,'three_slot_finite_owner_v1.py',owner_cfg)
   p=subprocess.run([PY,'-u','-B','-c',"from pathlib import Path;import sys,json;B=Path(sys.argv[1]);sys.path.insert(0,str(B));from owner_listener_ready_single_cpu_v1 import wait_actual;print(json.dumps(wait_actual(B,int(sys.argv[2]),20.)))",str(owner),str(oid['detached_pid'])],capture_output=True,text=True,timeout=45);assert p.returncode==0,p.stderr
   nid=launch(node,'three_slot_finite_node_v1.py',dict(newspec,role='node',run_id=runid,token=token));owner_cfg.clear();token=None;state['active']=dict(index=index,run_id=runid,window=str(window),owner_root=str(owner),node_root=str(node),owner=oid,node=nid,spec=newspec);put(window/'DISPATCH_ACTUAL_NO_TOKEN.json',state['active']);state['status']='learning_or_initializing';event('window_dispatched',active=state['active'],budget_guard=budget)
   while not closed_owner_node(owner,node):
    if (owner/'OWNER_EXIT_ACTUAL.json').exists() and (node/'NODE_EXIT_ACTUAL.json').exists():raise RuntimeError('Window owner/node exited without a valid complete cost handoff; retained for audit, no next GO')
    current=read(owner/'OWNER_CURRENT.json') if (owner/'OWNER_CURRENT.json').exists() else {};state['active']['GO']=current.get('go',{}).get('recovery');state['active']['pending_cost']=current.get('pending_cost');state['active']['node_current']=read(node/'NODE_CURRENT.json') if (node/'NODE_CURRENT.json').exists() else None;put(B/'SERIES_CURRENT.json',dict(epoch=time.time(),**state));time.sleep(3)
   co=read(owner/'COHORT_FINAL.json');cost=co['pending_cost']['cost'];assert co['pending_cost']['run_id']==runid;completed=dict(index=index,run_id=runid,owner_root=str(owner),node_root=str(node),actual_pending_seconds=cost.get('actual_production_seconds',0.),original_canonical_settled=False);assert runid not in {x['run_id'] for x in state['completed']};state['completed'].append(completed);put(B/'SERIES_STATE.json',dict(epoch=time.time(),**state));event('window_actual_terminal_cost_once',completed=completed)
   proof=review_closed(owner,node,newspec);completed['whole_CPU_proof']=str(window/'CLOSED_FINAL_WHOLE_MODEL_CPU_ACTUAL.json');completed['final']=proof['final'];put(B/'SERIES_STATE.json',dict(epoch=time.time(),**state));event('window_whole_CPU_passed',index=index,source=proof['final']);source=proof['final'];previous_node=node;previous_owner=owner;spec=newspec;index+=1
  state['active']=None;put(B/'SERIES_CURRENT.json',dict(epoch=time.time(),**state));event('series_boundary_stop',reason=state['status'],budget_guard=budget)
 except BaseException:
  state['status']='original_error_no_automatic_retry';put(B/'SERIES_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),state=state,canonical_not_written=True,inspect_any_active_children_before_resume=True));put(B/'SERIES_CURRENT.json',dict(epoch=time.time(),**state));raise
 finally:
  # A failed coordinator never deletes its lease or pretends an active child exited.
  fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd);put(B/'SERIES_EXIT_ACTUAL.json',dict(epoch=time.time(),status=state['status'],active_child_exit_not_inferred=state.get('active'),reservation_retained=True,original_canonical_settled=False))

def verify_previous_100hz_series(cfg):
 import psutil
 old=Path(cfg['previous_100hz_controller']);state=read(old/'SERIES_STATE.json');ex=read(old/'SERIES_EXIT_ACTUAL.json');assert ex['status']=='requested_stop_at_boundary' and read(old/'SERIES_CURRENT.json')['active'] is None
 assert not any(p.pid!=os.getpid() and any(x.startswith(str(old.parent)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 rows=state['completed'];assert len(rows)==len({x['run_id'] for x in rows}) and sum(x['actual_pending_seconds'] for x in rows)==cfg['prior_100hz_series_pending_seconds']
 with (OWNED/'state/MOD4_E3_AUTO_PENDING_SERIES_20261020.json').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 assert rows[-1]['final']['SHA']==cfg['initial_source']['SHA']
def qualify_clock_native(node,spec):
 import importlib.util
 sp=importlib.util.spec_from_file_location('clock_native_common',node/'three_slot_common_v1.py');common=importlib.util.module_from_spec(sp);sp.loader.exec_module(common)
 sp=importlib.util.spec_from_file_location('clock_native_resource',node/'three_real_gpu_resource_v1.py');res=importlib.util.module_from_spec(sp);sp.loader.exec_module(res);lock=res.acquire(spec,node);p=None
 try:
  p=common.spawn(spec,'native')
  try:rc=p.wait(timeout=850)
  except subprocess.TimeoutExpired:
   put(node/'job0/clock_native50/STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='bounded clock qualification timeout; own saved stop'));p.wait();raise
  put(node/'POLICY50_NATIVE_WORKER_WAITED_EXIT_ACTUAL.json',dict(epoch=time.time(),returncode=rc,pid=p.pid,actual_waited=True));assert rc==0 and read(node/'job0/clock_native50/FINAL.json')['passed'] and not list((node/'job0/clock_native50').glob('*ORIGINAL_ERROR*'))
  run=subprocess.run([PY,'-u','-B',str(node/'policy50_native_CPU_v1.py'),str(node)],capture_output=True,text=True,timeout=120);put(node/'POLICY50_NATIVE_CPU_PROCESS_ACTUAL.json',dict(epoch=time.time(),returncode=run.returncode,stdout=run.stdout,stderr=run.stderr));assert run.returncode==0
 finally:
  if p and p.poll() is None:put(node/'job0/clock_native50/STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='qualification saved stop'));p.wait()
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close()

if __name__=='__main__':
 cfg=json.loads(sys.stdin.readline());assert not (B/'supervisor_CONSOLE.log').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='serial_supervisor')),flush=True)
 else:
  os.setsid();fd=os.open(str(B/'supervisor_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd);main(cfg)
