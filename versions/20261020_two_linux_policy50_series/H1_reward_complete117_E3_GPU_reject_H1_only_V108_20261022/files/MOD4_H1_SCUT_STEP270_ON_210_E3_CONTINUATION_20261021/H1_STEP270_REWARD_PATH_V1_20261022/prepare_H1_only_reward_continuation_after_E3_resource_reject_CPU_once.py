from pathlib import Path
import ast,copy,hashlib,json,shutil,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';P=T/'H1_STEP270_E3_REWARD_PATH_PAIR_V19_20261022'
read=lambda p:json.loads(Path(p).read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 resource=read(R/'PAIR19_ACTUAL_RESOURCE_REJECTION_COMPONENTS_ACTUAL.json');assert not resource['expected_GPU_empty'] and not resource['pair19_remote_root_exists']
 oldq=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 N=T/'H1_STEP270_REWARD_H1_ONLY_V20_20261022';assert not N.exists();N.mkdir();(N/'reports').mkdir();shutil.copytree(P/'controllers',N/'controllers')
 old=(P/'controllers/three_slot_finite_owner_v1.py').read_text('utf8');changes=[("set(specs)=={'h1','recovery'}","set(specs)=={'h1'}"),("cfg['deferred_experts']==['e2']","cfg['deferred_experts']==['e2','recovery']"),("sum(b.CAPS[k] for k in specs)+9400.860692501068","7800+9400.860692501068"),("'Linux_H1_STEP270_E3_'","'Linux_H1_STEP270_E3_RESOURCE_DEFERRED_'")]
 owner=old
 for a,z in changes:assert owner.count(a)==1;owner=owner.replace(a,z)
 restored=owner
 for a,z in reversed(changes):restored=restored.replace(z,a)
 assert ast.dump(ast.parse(restored))==ast.dump(ast.parse(old))
 def fn(text,name):return ast.dump(next(x for x in ast.walk(ast.parse(text)) if isinstance(x,ast.FunctionDef) and x.name==name))
 assert fn(owner,'account')==fn(old,'account') and fn(owner,'do_POST')==fn(old,'do_POST')
 (N/'controllers/three_slot_finite_owner_v1.py').write_text(owner,encoding='utf8')
 dest=N/'payloads/h1';shutil.copytree(Path(oldq['payloads']['h1']),dest)
 # Node payload keeps its old, unused owner file byteexact; the actual owner runs in its separate qualified root.
 task=read(dest/'job0/TASK.json');(dest/'PAIR19_TASK_METADATA_UNUSED_HISTORICAL.json').write_text(json.dumps(task,indent=2),encoding='utf8');task.update(id=N.name+'_h1',E3_deferred_for_actual_GPU_nonempty=True);(dest/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 (dest/'E3_ACTUAL_RESOURCE_REJECTION_NO_GO.json').write_text(json.dumps(resource,indent=2),encoding='utf8')
 manifest=read(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');prior={x['relative']:x for x in manifest['files']};rows=[]
 for p in sorted(dest.rglob('*')):
  if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(dest).as_posix();sha=prior[rel]['SHA'] if p.suffix in ('.pt','.npz','.usd','.stl') else H(p)
  rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
 manifest['files']=rows;(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 spec=dict(oldq['specs']['h1'],manifest_SHA=H(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'))
 q=dict(oldq,payloads=dict(h1=str(dest)),specs=dict(h1=spec),sources=dict(h1=oldq['sources']['h1']),roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_reward_H1only_2210v20/h1'),owner_root='/mnt/mod4_linux_durable_20261013/H1step270_reward_H1only_2210v20/owner',E3_deferred_resource_actual=resource,reserve_seconds=7800)
 put(N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
 shutil.copy2(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',N/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')
 proof=dict(epoch=time.time(),passed=True,source_SHA=q['sources']['h1']['SHA'],source_Adam=q['sources']['h1']['Adam'],only_scheduled_expert='h1',deferred=['e2','recovery'],admission_reserve_seconds=7800,strict_threshold=82512.86069250107,original_account_and_authenticated_handler_AST_exact=True,entire_owner_AST_exact_after_reversing_four_scheduler_label_edits=True,common_and_node_byteexact=True,no_PPO_physics_reward_or_source_state_change=True,owner_SHA=H(N/'controllers/three_slot_finite_owner_v1.py'),reference_owner_SHA=H(P/'controllers/three_slot_finite_owner_v1.py'),changes=changes,not_remote_installed_or_GO_yet=True,local_read_basename_error_preserved='E3_bridge_continuation_V8/controllers absent; actual two_policy50_original_account_controllers source was read; no helper/SSH executed by that local FileNotFound read')
 put(N/'reports/H1_ONLY_ORIGINAL_ACCOUNT_SCHEDULER_CPU_ACTUAL.json',proof)
 deploy=(P/'deploy_pair_new_original_writer_bounded_once.py').read_text('utf8')
 a=deploy.index('def main():');deploy=deploy[:a]+'''def main():
 q=json.loads((R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());receipt=json.loads((R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').read_bytes());scheduler=json.loads((R/'H1_ONLY_ORIGINAL_ACCOUNT_SCHEDULER_CPU_ACTUAL.json').read_bytes())
 assert scheduler['passed'] and scheduler['admission_reserve_seconds']==7800 and set(q['specs'])=={'h1'}
 put('H1_ONLY_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),source=q['sources'],E3_no_GO_resource_deferred=True,reserve7800=True));c=d.t.connect();cfg=None
 try:
  install_h1(c,q)
  boundary=d.code(c,d.t.PY,d.OWNER,dict(root=q['owner_root'],receipt=receipt),timeout=90);put('H1_ONLY_FRESH_ORIGINAL_CANONICAL_LOCKS_ACTUAL.json',boundary)
  sf=c.open_sftp()
  try:
   for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py'):sf.put(str(N/'controllers'/name),q['owner_root']+'/'+name)
  finally:sf.close()
  remote=d.code(c,d.t.PY,OWNER_CPU,dict(root=q['owner_root'],reference='/mnt/mod4_linux_durable_20261013/H1step270_rewardmigration_2210v18/owner',scheduler=scheduler),timeout=60);put('H1_ONLY_INSTALLED_OWNER_ACCOUNT_AUTH_AST_CPU_ACTUAL.json',remote)
  cfg=dict(role='owner',experts=q['specs'],scheduling_authority='human_requested_available_experts',deferred_experts=['e2','recovery'],run_id='H1_REWARD_E3_RESOURCE_DEFERRED_ORIGINAL_'+str(time.time_ns()),token=secrets.token_hex(32))
  owner=d.launch(c,d.t.PY,q['owner_root'],'three_slot_finite_owner_v1.py',cfg)
  ready=d.code(c,d.t.PY,"from pathlib import Path;import json,socket,time;B=Path(v['root']);until=time.monotonic()+20\\nwhile not (B/'OWNER_IDENTITY.json').exists():\\n assert time.monotonic()<until;time.sleep(.1)\\nwith socket.create_connection(('10.24.4.210',29754),timeout=5):pass\\nprint(json.dumps(dict(owner=json.loads((B/'OWNER_IDENTITY.json').read_bytes()),listener_ready=True)))",dict(root=q['owner_root']),timeout=30);put('H1_ONLY_OWNER_ACTUAL_READY.json',ready)
  node=d.launch(c,d.t.PY,q['roots']['h1'],'three_slot_finite_node_v1.py',dict(q['specs']['h1'],role='node',run_id=cfg['run_id'],token=cfg['token']))
  result=dict(epoch=time.time(),owner=owner,owner_identity=ready['owner'],nodes=dict(h1=node),roots=q['roots'],owner_root=q['owner_root'],specs=q['specs'],sources=q['sources'],run_id=cfg['run_id'],E3_no_GO_resource_deferred=True,reserve_seconds=7800,not_learning_until_actual_GO_PPO=True)
  put('H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json',result);print(json.dumps(dict(owner=owner,node=node,not_learning_until_GO_PPO=True)))
 finally:
  if cfg:cfg.clear()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('H1_ONLY_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_same_root_or_refund=True));raise
'''
 owner_cpu="""from pathlib import Path
import ast,hashlib,json
B=Path(v['root']);old=(Path(v['reference'])/'three_slot_finite_owner_v1.py').read_text('utf8');s=(B/'three_slot_finite_owner_v1.py').read_text('utf8');assert hashlib.sha256(s.encode()).hexdigest()==v['scheduler']['owner_SHA']
for a,z in reversed(v['scheduler']['changes']):s=s.replace(z,a)
assert ast.dump(ast.parse(s))==ast.dump(ast.parse(old))
assert (B/'three_slot_common_v1.py').read_bytes()==(Path(v['reference'])/'three_slot_common_v1.py').read_bytes()
print(json.dumps(dict(passed=True,original_account_auth_AST_exact=True,reserve7800=True,no_ledger_write_or_GO=True)))"""
 deploy=deploy.replace('def main():', 'OWNER_CPU='+repr(owner_cpu)+'\ndef main():',1)
 (N/'deploy_H1_only_new_original_writer_bounded_once.py').write_text(deploy,encoding='utf8');ast.parse(deploy)
 src=(P/'collect_pair_first_actual_GO_positive_PPO_once.py').read_text('utf8');a=src.index('READ210=r');z=src.index("READ72=r",a);prefix=src[:z]
 prefix=prefix.replace("('h1','recovery')","('h1',)").replace("{'h1','recovery'}","{'h1'}").replace("==['e2']","==['e2','recovery']")
 meta=prefix+'''try:
 q=json.loads((R/'H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());put('H1_ONLY_FIRST_METADATA_STARTED_ACTUAL.json',dict(epoch=time.time(),max_wait_seconds=570));c=d.t.connect()
 try:a=d.code(c,d.t.PY,READ210,dict(owner=q['owner_identity'],root=q['roots']['h1'],source_SHA=q['sources']['h1']['SHA'],GPU_UUID=q['specs']['h1']['GPU_UUID'],run_id=q['run_id']),timeout=600)
 finally:c.close()
 result=dict(epoch=time.time(),passed=True,run_id=q['run_id'],source210=a,actual_finite_returned=True,E3_no_GO_resource_deferred=True,reserve_seconds=7800,not_skill_or_future_FINAL=True)
 put('H1_ONLY_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json',result);print(json.dumps(dict(passed=True,run_id=q['run_id'],H1_updates=a['current']['rows']['h1']['latest_save']['updates'])))
except BaseException:
 put('H1_ONLY_FIRST_METADATA_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_rerun_or_hotpatch=True));raise
'''
 (N/'collect_H1_only_actual_GO_positive_PPO_once.py').write_text(meta,encoding='utf8');ast.parse(meta)
 put(R/'V108_H1_ONLY_SCHEDULER_AFTER_ACTUAL_E3_RESOURCE_REJECT_UNUSED_WORKFLOW_CPU_ACTUAL.json',dict(proof,new_stage=str(N),files=[dict(path=str(p),SHA=H(p)) for p in N.glob('*.py')]))
 print(json.dumps(dict(prepared=True,new_stage=str(N),reserve_seconds=7800,no_GO=True)))
except BaseException:
 put(R/('H1_ONLY_PREPARER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc()));raise
