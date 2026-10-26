"""Preserve preGO83 rejection; repair only schema binding in a fresh normal-production namespace."""
from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
N=Path(__file__).resolve().parent;A=N.parent/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026';T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
 errors=list((A/'reports').glob('THREE_EXPERT_DEPLOY_ORIGINAL_ERROR_*.json'));assert len(errors)==1 and 'auth' in read(errors[0])['error'] and not (A/'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').exists()
 assert not (N/'payloads').exists();shutil.copytree(A/'controllers',N/'controllers');q=read(A/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');q.update(epoch=time.time(),owner_root=q['owner_root'].replace('2610v83/','2610v83b/'))
 put(R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',read(A/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json'))
 for key in ('h1','recovery','e2'):
  B=N/'payloads'/key;shutil.copytree(A/'payloads'/key,B,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));manifest=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');before={r['relative']:r for r in manifest['files']}
  role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py';hist=B/'prebind83B_exact_history';hist.mkdir()
  for name in (role,'NORMAL_THREE_83_PRODUCTION_SOURCE_AUTH_ACTUAL.json','THREE_SLOT_COMPLETE_MANIFEST_V1.json','job0/TASK.json'):shutil.copy2(B/name,hist/(Path(name).name+'.original_bytes.txt'))
  oldauth=B/'NORMAL_THREE_83_PRODUCTION_SOURCE_AUTH_ACTUAL.json';auth=read(oldauth);oldauth.unlink()
  s=(B/role).read_text('utf8');assert s.count('NORMAL_THREE_83_PRODUCTION_SOURCE_AUTH_ACTUAL.json')==1;s=s.replace('NORMAL_THREE_83_PRODUCTION_SOURCE_AUTH_ACTUAL.json','NORMAL_THREE_83B_PRODUCTION_SOURCE_AUTH_ACTUAL.json');(B/role).write_text(s,'utf8')
  if key=='e2':
   assert auth['kind']=='actual_closed_three_same_V8_landing_journal_continuation';auth['kind']='actual_closed_three_V8_landing_journal_continuation'
  auth.update(epoch=time.time(),guard_SHA=H(B/role),preGO83_auth_kind_typo_preserved=True);put(B/'NORMAL_THREE_83B_PRODUCTION_SOURCE_AUTH_ACTUAL.json',auth)
  task=read(B/'job0/TASK.json');task['id']=N.name+'_'+key;(B/'job0/TASK.json').write_text(json.dumps(task,indent=2),'utf8')
  rows=[]
  for p in sorted(B.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(B).as_posix();digest=before[rel]['SHA'] if p.suffix in ('.pt','.npz','.usd','.stl') else H(p)
   rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest))
  manifest['files']=rows;(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest,indent=2),'utf8');q['payloads'][key]=str(B);q['roots'][key]=q['roots'][key].replace('2610v83/','2610v83b/');q['specs'][key]['manifest_SHA']=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 put(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
 installer=(A/'e2_displaced_native_slot_qualified80_source_install_v1.py').read_text('utf8');assert installer.count('2610v83/e2')==1;installer=installer.replace('2610v83/e2','2610v83b/e2');(N/'e2_displaced_native_slot_qualified80_source_install83B_v1.py').write_text(installer,'utf8')
 names={
 'deploy_actual_three83_normal_experts_qualified82Q_80_original_writer_unused_once.py':'deploy_actual_three83B_normal_experts_qualified82Q_80_original_writer_unused_once.py',
 'collect_actual_three83_normal_experts_first_PPO_finite_unused_once.py':'collect_actual_three83B_normal_experts_first_PPO_finite_unused_once.py',
 'collect_actual_three83_finals_original_cost_unused_once.py':'collect_actual_three83B_finals_original_cost_unused_once.py',
 'review_three83_normal_complete_models_original_cost_CPU_unused_once.py':'review_three83B_normal_complete_models_original_cost_CPU_unused_once.py'}
 for old,new in names.items():
  s=(A/old).read_text('utf8').replace(A.name,N.name).replace('DEPLOYER_REUSED_H1_HELPER_83_EXACT_SOURCE.py','DEPLOYER_REUSED_H1_HELPER_83B_EXACT_SOURCE.py').replace('from e2_displaced_native_slot_qualified80_source_install_v1 import CODE','from e2_displaced_native_slot_qualified80_source_install83B_v1 import CODE')
  if new.startswith('deploy_'):
   needle='  c=d.connect72(secret);d.upload(c,d.PY72,\'recovery\',q)';assert s.count(needle)==1
   replacement='''  c=d.connect72(secret)
  prior83=d.code(c,d.PY72,"from pathlib import Path;import json,os,psutil;roots=[Path(x) for x in v['roots']];assert all(not (r/n).exists() for r in roots for n in ('NODE_IDENTITY.json','GO_PRODUCTION.json','NODE_TERMINAL_ACTUAL.json'));assert not any(p.pid!=os.getpid() and any(any(a.startswith(str(r)+'/') for r in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));print(json.dumps(dict(no_node_or_GO=True,own_processes_actual_out=True,roots=[str(x) for x in roots])))",dict(roots=[str(x).replace('2610v83b/','2610v83/') for x in [q['roots']['e2'],q['roots']['recovery']]]),timeout=30);put('PREGO83_OWN_TWO_TARGETS_NO_NODE_GO_AND_PROCESSES_OUT_ACTUAL.json',prior83)
  d.upload(c,d.PY72,'recovery',q)'''
   s=s.replace(needle,replacement,1)
   needle='c=route.connect();m.install_h1(c,q)';assert s.count(needle)==1
   replacement='''c=route.connect()
  prior83=d.code(c,route.PY,"from pathlib import Path;import json,os,psutil;roots=[Path(x) for x in v['roots']];assert all(not r.exists() for r in roots);assert not any(p.pid!=os.getpid() and any(any(a.startswith(str(r)+'/') for r in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));print(json.dumps(dict(original83_owner_H1_roots_absent=True,own_processes_actual_out=True)))",dict(roots=[q['owner_root'].replace('2610v83b/','2610v83/'),q['roots']['h1'].replace('2610v83b/','2610v83/')]),timeout=30);put('PREGO83_ORIGINAL_SOURCE_OWNER_H1_ABSENT_NO_FEE_ACTUAL.json',prior83)
  m.install_h1(c,q)'''
   s=s.replace(needle,replacement,1)
  ast.parse(s);(N/new).write_text(s,'utf8')
 test=(A/'review83_source_lineage_and_normal_controller_CPU_unused_once.py').read_text('utf8').replace('NORMAL_THREE_83_PRODUCTION_SOURCE_AUTH_ACTUAL.json','NORMAL_THREE_83B_PRODUCTION_SOURCE_AUTH_ACTUAL.json')
 needle="  v=ns['validate_closed69_metadata'](proof,key,prior['source_Adamstep']);";assert test.count(needle)==1
 extra="""  auth=read(B/'NORMAL_THREE_83B_PRODUCTION_SOURCE_AUTH_ACTUAL.json');roletree=ast.parse((B/role).read_bytes())
  authasserts=[x for x in ast.walk(roletree) if isinstance(x,ast.Assert) and any(isinstance(y,ast.Name) and y.id=='auth' for y in ast.walk(x))]
  assert authasserts
  for stmt in authasserts:
   if any(isinstance(x,ast.Name) and x.id=='closure' for x in ast.walk(stmt)):continue
   exec(compile(ast.Module(body=[stmt],type_ignores=[]),'actual_auth_assert','exec'),dict(auth=auth,spec=spec,B=B,role=role,H=H))
"""
 test=test.replace(needle,extra+needle,1);(N/'review83B_exact_auth_schema_and_source_lineage_CPU_unused_once.py').write_text(test,'utf8')
 transport=T/'H1_STEP270_REWARD_PATH_V1_20261022';s=(transport/'same_authorized_session_compressed_transport_v137.py').read_text('utf8');needle='    assert target.name in {';assert s.count(needle)==1;s=s.replace(needle,needle+'\n'+''.join('        '+repr(n)+',\n' for n in names.values() if not n.startswith('review_')),1);(transport/'same_authorized_session_compressed_transport_v138.py').write_text(s,'utf8')
 put(R/'PREGO83_REJECTION_AND_NEW83B_AUTH_SCHEMA_ONLY_FIX_ACTUAL.json',dict(epoch=time.time(),prepared_only=True,original83_error=str(errors[0]),original83_no_owner_GO_fee_not_training_failure=True,exact_rejected_kind='actual_closed_three_same_V8_landing_journal_continuation',guard_required_kind='actual_closed_three_V8_landing_journal_continuation',original83_bytes_preserved=True,new_namespace_only=True,source_H1_E3_82Q_E2_80_unchanged=True,original_owner_controller_bytes_unchanged=True,prior83_remote_allout_checked_before_original83B_GO=True))
 print(json.dumps(dict(prepared83B=True,auth_schema_fix_only=True,no_GO_yet=True)))
except BaseException:
 put(R/('SOURCE83B_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_replay=True));raise
