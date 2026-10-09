"""Immutable actual E1 terrain pair and old-skill candidate; no GPU/ledger mutation."""
from pathlib import Path
import ast,hashlib,json,sys,time,zipfile,shlex
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent;read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json').exists()
proof=read(R/'E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json');worker=read(R/'E1_BEHAVIOR_EVALUATOR_ACTUAL.json')
assert proof['active_Sactive_empty'] and proof['two_original_locks_free'] and proof['snapshot57_exact'] and worker['healthy_actual_worker_no_restart']
base=B/'MOD4_D7_RESET_PERFORMANCE_REVIEW_20261009/d7-original-frozen.zip';assert sha(base.read_bytes())=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
with zipfile.ZipFile(base) as z:
 m=read(B/'MOD4_D7_RESET_PERFORMANCE_REVIEW_20261009/reports/template.json');manifest=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in manifest['files']}
assert all(sha(v)==manifest['files'][n] for n,v in payload.items())
matched={}
for n,h in proof['source_freeze']['sha256'].items():
 if n.startswith('isaac/mod4/'):
  member='runtime/'+n
  if member in payload:
   if Path(n).name=='env.json':continue
   assert sha(payload[member])==h,('D7 frozen source differs from actual E1',n)
   matched[n]=h
extras={p.relative_to(D/'actual_source').as_posix():p.read_bytes() for p in (D/'actual_source').rglob('*') if p.is_file()}
assert 'isaac/mod4/e1_reset_evidence.py' in extras and 'isaac/mod4/e1_scene_query_resource.py' in extras
for n,b in extras.items():
 assert sha(b)==proof['source_freeze']['sha256'][n],n
 if n.endswith('.py'):ast.parse(b.decode('utf8'))
 payload['runtime/'+n]=b
entry=(D/'e1_frozen_route_behavior.py').read_bytes();ast.parse(entry.decode());payload['runtime/isaac/mod4/frozen_history_flat.py']=entry
changed={n:sha(v) for n,v in payload.items() if n not in manifest['files'] or sha(v)!=manifest['files'][n]}
newmanifest=dict(manifest,files={n:sha(v) for n,v in payload.items()},actual_E1_learning_root=proof['source_freeze']['candidate_root'],actual310_E1_source_SHA=proof['source_freeze']['sha256'],matched_D7_members=matched,new_or_changed_members=changed,
 protocol='approved_E1_gentle_route_behavior_v1',transport_kind_flat_actual_route_scope=True,no_learning=True,not_user_paused93_94=True,full15s_every_control_pre_reset_route_raw=True,
 RM_annotation_id='MOD4-RM-TERRAIN-SPIN-AND-ENTRY-LIP-ANNOTATION-001',RM_entry_lip_not_installed=True,geometry_seed=20260928,no_geometry_simplification=True)
package=D/'s3-e1-actual310-gentle-fullroute-frozen.zip';assert not package.exists()
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(newmanifest,indent=2))
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
try:
 with c.open_sftp() as f:
  path=E+'/artifacts/'+package.name
  try:f.stat(path)
  except FileNotFoundError:pass
  else:raise AssertionError('Package already installed')
  f.put(str(package),path+'.partial');assert sha(f.open(path+'.partial').read())==sha(package.read_bytes());f.rename(path+'.partial',path)
 # Full checkpoint is copied only from the actual reviewed own completion.
 code='''
from pathlib import Path
import shutil,hashlib,json
source=Path(SOURCE);out=Path(DEST);h=EXPECTED
assert hashlib.sha256(source.read_bytes()).hexdigest()==h
if not out.exists():shutil.copy2(source,out)
assert hashlib.sha256(out.read_bytes()).hexdigest()==h
print(json.dumps(dict(path=str(out),bytes=out.stat().st_size,sha256=h)))
'''.replace('SOURCE',repr(proof['row']['checkpoint']['path'])).replace('DEST',repr(E+'/artifacts/e1-own32053-'+proof['row']['checkpoint']['sha256']+'.pt')).replace('EXPECTED',repr(proof['row']['checkpoint']['sha256']))
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');candidate=json.loads(raw)
 oldjobs=read(B/'MOD4_D9_COMBINATION_PREPARE_20261009/reports/SELECTED_D7_BEHAVIOR_SOURCE.json')['paired_cases']
 baseline=read(B/'MOD4_S3_E1_FULL_DR_TERRAIN_PREPARE_20261009/reports/E1_SCENE_QUERY_RESOURCE_SDK_PUBLISHED.json')['manifest']['artifacts']['checkpoint']
 runtime=dict(path=path,bytes=package.stat().st_size,sha256=sha(package.read_bytes()));jobs=[]
 for number,label,kind,checkpoint in [(113,'terrain-anchor','flat',baseline),(114,'terrain32053','flat',candidate),(115,'retention32053','flat',candidate),(115,'retention32053','spin',candidate),(115,'retention32053','world',candidate)]:
  row=json.loads(json.dumps(m));terrain=number in (113,114)
  job=f'clk2500-closure-episode-d3-{number}-e1-{label}-{kind}'
  row.update(job_id=job,published_epoch=time.time(),kind=kind,num_envs=80 if kind=='flat' else 88,steps=1500,seed=20260928 if terrain else 20261002,
    actual_curriculum_stage='S3',actual_curriculum_expert='E1',actual_behavior_scope='gentle terrain forward/reverse/stand full pre-reset routes' if terrain else 'matched inherited flat/spin/world retention',
    role='Planned E1 behavior admission; actual completed32053 vs retained31903, not paused optional93/94 and not skill graduation',scope_pending_actual_review=True)
  row['artifacts']['checkpoint']=checkpoint
  if terrain:row['artifacts']['runtime']=runtime
  dest=E+'/eval_queue/'+job+'.json'
  with c.open_sftp() as f:
   try:f.stat(dest)
   except FileNotFoundError:pass
   else:raise AssertionError('Job already published '+job)
   raw=json.dumps(row,indent=2).encode()
   with f.open(dest+'.partial','wb') as q:q.write(raw)
   f.rename(dest+'.partial',dest)
  jobs.append(row)
 v=dict(epoch=time.time(),source=candidate,baseline=baseline,terrain_package=runtime,package_manifest=newmanifest,jobs=jobs,reused_old_skill_baseline=oldjobs,
  actual_saved_closeout=proof['row'],no_GPU_training_or_canonical_write=True,new_budget_seconds=0,not_user_paused93_94=True,evaluator_not_restarted=True,behavior_scope_pending=True)
 (R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(published=[j['job_id'] for j in jobs],package_SHA=runtime['sha256'],candidate_SHA=candidate['sha256'],no_training_or_ledger_mutation=True)))
finally:c.close()
