from pathlib import Path
import os,sys,time,json,shutil,ast,secrets,getpass,traceback
N=Path(__file__).resolve().parent;R=N/'reports';sys.path.insert(0,str(N));import deploy_two72_new_native_after_actual_final_then_original_CURB_handoff_once as a
Q=N/'v2_payload';SOURCE='/mnt/mod4_linux_durable_20261013/N72_1710v2';ROOTS={k:'/home/lc01/Zonglin Li/zonglin2/tasks/N72_1710v2/'+k for k in ('e2','recovery')}
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 diag=json.loads((R/'REJECTED_DEPLOY_ACTUAL_EMPTY_OWNER_AND_TARGET_SELF_ARG_MATCH_READONLY.json').read_bytes());assert len(diag['target']['matched'])==1 and diag['target']['matched'][0]['is_this_observer'] and not diag['target']['newroot_exists'];assert json.loads((R/'EXACT_NEW_EMPTY_COORDINATOR593869_ACTUAL_TERMINATED_NO_TRAINING_BUDGET_MUTATION.json').read_bytes())['actual_process_out_or_reaped_zombie'];assert Q.exists() and not (Q/'e2/two72_native_then_original_owner_handoff_v2.py').exists();proof=json.loads((R/'TWO72_FINAL_PROTOCOL_CPU_NEGATIVES_FROZEN_SOURCES_ACTUAL.json').read_bytes());specs={}
 ownertext=(N/'two72_native_then_original_owner_handoff_v1.py').read_text('utf8');needle="  while True:\n   with mutex:rows=";assert ownertext.count(needle)==2;ownertext=ownertext.replace(needle,"  while True:\n   if not active and not shared['go'] and not shared['remote'] and time.time()-started>120:\n    put(B/'EMPTY_UNOBSERVED_NODE_ADMISSION_EXPIRED_NO_GO.json',dict(epoch=time.time(),no_observed_node_status=True,no_GO_no_canonical_write_no_original_locks=True,not_claiming_unobserved_remote_child_out=True));break\n   with mutex:rows=",1)
 for key in ROOTS:
  b=Q/key;(b/'two72_native_then_original_owner_handoff_v2.py').write_text(ownertext,encoding='utf8');p=b/'three_expert_helpers_v2.py';p.write_text(p.read_text('utf8').replace('PORT=29752','PORT=29753'),encoding='utf8');m=json.loads((b/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());m['files'].append(dict(relative='two72_native_then_original_owner_handoff_v2.py',bytes=(b/'two72_native_then_original_owner_handoff_v2.py').stat().st_size,SHA=a.H(b/'two72_native_then_original_owner_handoff_v2.py')))
  for row in m['files']:
   p=b/row['relative'];row.update(bytes=p.stat().st_size,SHA=a.H(p));ast.parse(p.read_text('utf8')) if p.suffix=='.py' else None
  mf=b/'CONTINUATION_COMPLETE_MANIFEST_V2.json';mf.write_text(json.dumps(m,indent=2),encoding='utf8');s=next(x for x in proof['specs'] if x['key']==key);specs[key]=dict(s,python=a.PY,manifest_SHA=a.H(mf),files=len(m['files']))
 # Concrete self/real/unrelated process fixture; only observerPID is omitted.
 base=a.PREV['e2'];fixture=[dict(pid=1,argv=['python','-',base+'/job0/production/model_update152.pt']),dict(pid=2,argv=['python',base+'/production_worker.py']),dict(pid=3,argv=['python','elsewhere.py'])];found=[x for x in fixture if x['pid']!=1 and any(s.startswith(base+'/') for s in x['argv'])];assert [x['pid'] for x in found]==[2];put('V3_SOURCE_SELF_PID_EXCLUSION_CPU_AND_EMPTY_OWNER_TIMEOUT_FIX_ACTUAL.json',dict(epoch=time.time(),passed_CPU_fixture_only=True,original_observer_self_match_rejection_preserved=True,only_exact_observer_PID_excluded_real_old_worker_still_rejected=True,source_control_empty_unobserved_node_timeout120_without_fake_exit_or_PPO=True,no_current_CURB_or_existingSDK_guard_change=True,specs=specs));put('V3_TARGET_FIRST_FINITE_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True));pw=getpass.getpass('Host72 corrected self-observer admission (hidden): ');c=None;cfg=None
 try:
  c=a.connect72(pw);pw=None;create=a.CREATE.replace('import sys,json,time,hashlib,shutil,psutil,subprocess','import sys,json,time,hashlib,shutil,psutil,subprocess,os').replace("  if any(str(A)+'/' in s for s in p.info['cmdline'] or []):alive.append(p.info)","  if p.pid!=os.getpid() and any(str(A)+'/' in s for s in p.info['cmdline'] or []):alive.append(p.info)")
  assert 'p.pid!=os.getpid()' in create
  for key,s in specs.items():
   root=ROOTS[key];put('V3_'+key.upper()+'_PREVIOUS_FINAL_OUT_SOURCE_RESOURCE_NEW_ROOT_ACTUAL.json',a.code(c,a.PY,create,root,a.PREV[key],s['prior_exact_final'],s['source_SHA'],s['source_filename'],s['GPU_UUID']));sf=c.open_sftp();sf.get_channel().settimeout(120)
   try:
    mf=Q/key/'CONTINUATION_COMPLETE_MANIFEST_V2.json';sf.put(str(mf),root+'/'+mf.name);missing=a.code(c,a.PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());print(json.dumps(dict(missing=[r for r in m['files'] if not (B/r['relative']).is_file() or (B/r['relative']).stat().st_size!=r['bytes'] or hashlib.sha256((B/r['relative']).read_bytes()).hexdigest()!=r['SHA']])))",root);put('V3_'+key.upper()+'_MISSING_ONLY_UPLOAD_ACTUAL.json',missing)
    for row in missing['missing']:
     p=Q/key/row['relative'];assert a.H(p)==row['SHA'];folder=root
     for piece in row['relative'].split('/')[:-1]:
      folder+='/'+piece
      try:sf.stat(folder)
      except FileNotFoundError:sf.mkdir(folder)
     sf.put(str(p),root+'/'+row['relative'])
   finally:sf.close()
   put('V3_'+key.upper()+'_ALL_TARGET_CPU_SOURCE_SHA_AST_ACTUAL.json',a.code(c,a.PY,a.CPU,root,timeout=180))
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=a.t.connect();put('V3_SOURCE_COORDINATOR_NEW_ROOT_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json,time,socket,psutil;B=Path(sys.argv[1]);assert not B.exists() and B.parent==Path('/mnt/mod4_linux_durable_20261013');assert not psutil.pid_exists(593869) or psutil.Process(593869).status()==psutil.STATUS_ZOMBIE\nwith socket.socket() as s:s.bind(('10.24.4.210',29753))\nB.mkdir();print(json.dumps(dict(epoch=time.time(),root=str(B),old_empty_owner_not_alive=True,current_CURB_and_budget_untouched=True)))",SOURCE));sf=c.open_sftp()
  try:
   for name in ('two72_native_then_original_owner_handoff_v2.py','three_expert_helpers_v2.py'):sf.put(str(Q/'e2'/name),SOURCE+'/'+name)
  finally:sf.close()
  cfg=dict(role='owner',experts=specs,run_id='TWO72_SAVED152_90_HEALTHY_V2_'+str(time.time_ns()),token=secrets.token_hex(32));launchsrc="from pathlib import Path;import sys,json,subprocess;B=Path(sys.argv[1]);assert not (B/(json.loads(sys.argv[3])['role']+'_CONSOLE.log')).exists();p=subprocess.run([sys.argv[2],'-u','-B',str(B/'two72_native_then_original_owner_handoff_v2.py')],input=sys.argv[3]+chr(10),text=True,capture_output=True,cwd=B,timeout=30);assert p.returncode==0,p.stderr;print(p.stdout)";owner=a.code(c,a.t.PY,launchsrc,SOURCE,a.t.PY,json.dumps(cfg));put('V3_SOURCE_OWNER_AFTER_BOTH_TARGET_CPU_ACTUAL_DISPATCH.json',dict(epoch=time.time(),owner=owner))
 finally:a.t.close(c);c=None
 # Password only acquired again as hidden input; no on-disk capability/credential.
 pw=getpass.getpass('Host72 launch two admitted finite native nodes (hidden): ')
 try:
  c=a.connect72(pw);pw=None;nodes={}
  for key in ROOTS:nodes[key]=a.code(c,a.PY,launchsrc,ROOTS[key],a.PY,json.dumps(dict(specs[key],role='node',run_id=cfg['run_id'],token=cfg['token'])))
  put('V3_TWO72_ACTUAL_NEW_NATIVE144_336_TARGETCPU_THEN_ORIGINAL_CURB_HANDOFF_DETACHED.json',dict(epoch=time.time(),owner=owner,nodes=nodes,source_root=SOURCE,target_roots=ROOTS,source_SHA={k:s['source_SHA'] for k,s in specs.items()},actual_new_native_not_PPO_pass=True,only_after_original_CURB_actual_exit_locks_then_each3600_accounted=True,no_new_budget_or_extra_watcher=True));print(json.dumps(dict(owner=owner,nodes=nodes,new_native_actually_dispatched_not_PPO=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('V3_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_replay=True));raise
