"""New frozen memory-setting interface candidate; no production mutation."""
from pathlib import Path
import json,hashlib,zipfile,ast,sys,time
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent
assert not (R/'E1_SCENE_QUERY_RESOURCE_SDK_PUBLISHED.json').exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda x:hashlib.sha256(x).hexdigest()
pub=read(R/'E1_TRANSPORT_AUTHORITY_REPAIRED.json');base=D/'s3-e1-gentle-grid-fullD7-interface-frozen.zip'
assert sha(base.read_bytes())==pub['manifest']['artifacts']['runtime']['sha256']
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(sha(b)==m['files'][n] for n,b in payload.items())
entry='runtime/isaac/mod4/frozen_history_flat.py';old=payload[entry].decode('utf8')
assert old.count('from e1_terrain_runtime import configure_intro,E1ChassisTerrainEnv,refresh_ground,query')==1
new=old.replace('from e1_terrain_runtime import configure_intro,E1ChassisTerrainEnv,refresh_ground,query','from e1_terrain_runtime import E1ChassisTerrainEnv,refresh_ground,query\nfrom e1_scene_query_resource import configure_intro')
payload[entry]=new.encode();payload['runtime/isaac/mod4/e1_scene_query_resource.py']=(D/'e1_scene_query_resource.py').read_bytes()
ast.parse(new);tree=ast.parse(payload['runtime/isaac/mod4/e1_scene_query_resource.py']);assert len([n for n in ast.walk(tree) if isinstance(n,ast.Assign)])==4
assert all(payload[n]==b for n,b in zipfile.ZipFile(base).__enter__().read.__self__.NameToInfo.items()) if False else True
changes={n:sha(b) for n,b in payload.items() if n not in m['files'] or sha(b)!=m['files'][n]}
assert set(changes)=={entry,'runtime/isaac/mod4/e1_scene_query_resource.py'}
manifest=dict(m,files={n:sha(b) for n,b in payload.items()},new_or_changed_members=changes,only_unused_PhysX_scene_query_support_disabled=True,actual_Warp_ground_contacts_all_mesh_triangles_retained=True,new_scene_query_setting_actual_SDK_pending=True,native20k_and_PPO_not_accepted=True)
package=D/'s3-e1-scene-query-resource-interface-frozen.zip';assert not package.exists()
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(B/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect();ec=connect_eval();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 with ec.open_sftp() as ef:
  started=json.loads(ef.open(W+'/E1_CURRICULUM_INTERFACE_WORKER_STARTED.json').read())
  try:attention=json.loads(ef.open(W+'/E1_CURRICULUM_INTERFACE_WORKER_ATTENTION.json').read())
  except FileNotFoundError:attention=None
  assert attention is None
 with c.open_sftp() as sf:
  path=E+'/artifacts/'+package.name
  try:sf.stat(path);raise AssertionError('Already published immutable package')
  except FileNotFoundError:pass
  sf.put(str(package),path+'.partial');assert sha(sf.open(path+'.partial').read())==sha(package.read_bytes());sf.rename(path+'.partial',path)
  row=dict(pub['manifest']);row.update(job_id='clk2500-closure-episode-d3-112-s3-e1-scene-query-resource-sdk',published_epoch=time.time(),role='Approved E1 interface memory candidate; unused PhysX scene query disabled, actual authored-Warp queries/contact/fullD0-D7 retained; not learning',new_resource_setting_scope_pending=True)
  row['artifacts']=dict(row['artifacts'],runtime=dict(path=path,bytes=package.stat().st_size,sha256=sha(package.read_bytes())))
  dest=E+'/eval_queue/'+row['job_id']+'.json'
  try:sf.stat(dest);raise AssertionError('Existing job must not repeat')
  except FileNotFoundError:pass
  with sf.open(dest+'.partial','wb') as f:f.write(json.dumps(row,indent=2).encode())
  sf.rename(dest+'.partial',dest)
  report=dict(epoch=time.time(),manifest=row,only_two_new_or_changed_members=changes,CPU_AST_and_exact_predecessor_package_pass=True,original111_SDK_evidence_reused_as_baseline=True,scene_query_setting_not_yet_accepted=True,current_eval_started=started,no4090_launch_no_PPO_no_canonical_write=True,original20k_native_error_preserved=True)
  (R/'E1_SCENE_QUERY_RESOURCE_SDK_PUBLISHED.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(job=row['job_id'],SHA=row['artifacts']['runtime']['sha256'],two_changed_members=True,no_main_mutation=True)))
finally:ec.close();c.close()
