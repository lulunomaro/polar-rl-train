from pathlib import Path
import ast,json,time,hashlib,shutil,zipfile
B=Path(__file__).resolve().parent;R=B/'reports';old=B/'E2_world88_native60_V2_payload';P=B/'E2_world88_native60_V3_payload';assert not P.exists();shutil.copytree(old,P)
reference=B.parent/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/payload/h1/job0/runtime/isaac/mod4';tree=ast.parse((reference/'h1_fullstate_environment_v1.py').read_bytes());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='tensor')
helper='"""Original tensor/proxy readback body, no environment or dynamics imports."""\nimport torch\n'+ast.unparse(fn)+'\n';(P/'lib/frozen_saved_tensor_readback.py').open('x',encoding='utf8').write(helper)
shutil.copy2(reference/'h1_authored_full_collider_plane_reference_v1.py',P/'lib/h1_authored_full_collider_plane_reference_v1.py')
worker=(B/'frozen_E2_world88_worker_v2_command_reference.py').read_text();new=worker.replace('from h1_fullstate_environment_v1 import tensor','from frozen_saved_tensor_readback import tensor');assert new!=worker
(B/'frozen_E2_world88_worker_v3_readback_dependencies.py').open('x',encoding='utf8').write(new);(P/'worker.py').write_text(new,'utf8')
cfg=json.loads((P/'FROZEN_CONFIG.json').read_bytes());cfg['kind']='E2_world88_native60_v3_complete_readback_dependencies';(P/'FROZEN_CONFIG.json').write_text(json.dumps(cfg,indent=2),'utf8')
before=json.loads((old/'SOURCE_MANIFEST.json').read_bytes());prior={x['relative']:x for x in before['files']};rows=[]
for p in sorted(P.rglob('*')):
 if not p.is_file() or p.name=='SOURCE_MANIFEST.json':continue
 rel=p.relative_to(P).as_posix();prev=prior.get(rel)
 if rel not in ('worker.py','FROZEN_CONFIG.json') and prev:
  assert p.stat().st_size==prev['bytes'];rows.append(prev)
 else:
  raw=p.read_bytes();rows.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 if p.suffix=='.py':ast.parse(p.read_bytes())
manifest=dict(source_SHA=cfg['source_SHA'],source_Adam=cfg['source_Adam'],configuration=cfg,files=rows);(P/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),'utf8')
z=B/'E2_WORLD88_NATIVE60_PAYLOAD_V3.zip'
with zipfile.ZipFile(z,'x',zipfile.ZIP_DEFLATED,compresslevel=1) as out:
 for p in P.rglob('*'):
  if p.is_file():out.write(p,p.relative_to(P).as_posix())
v=dict(epoch=time.time(),passed_source_AST=True,source_SHA=cfg['source_SHA'],source_Adam=cfg['source_Adam'],package=dict(path=str(z),bytes=z.stat().st_size,SHA=hashlib.sha256(z.read_bytes()).hexdigest()),only_worker_import_dependency_repair=True,original_tensor_readback_function_body_AST_exact=True,original_geometry_source_SHA=hashlib.sha256((P/'lib/h1_authored_full_collider_plane_reference_v1.py').read_bytes()).hexdigest(),all_actor_reward_action_physics_schedule_source_unchanged=True,old_failed_V2_root_and_full_error_preserved=True,not_GPU_execution_pass=True)
(R/'E2_CURRENT_CLOSED50_WORLD88_PACKAGE_V3_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2))
install=(B/'install_E2_native60_V2_source_CPU_once.py').read_text().replace('V2','V3').replace('native60_v2','native60_v3')
needle="out=dict(epoch=time.time(),root=str(B),all_manifest_files_exact=True"
extra="import sys;sys.path.insert(0,str(B/'lib'));from frozen_saved_tensor_readback import tensor;from h1_authored_full_collider_plane_reference_v1 import extract,evaluate\nx=torch.ones((2,3));assert tensor(x) is x;assert callable(extract) and callable(evaluate)\n"
assert needle in install;install=install.replace(needle,extra+needle)
(B/'install_E2_native60_V3_source_CPU_once.py').open('x',encoding='utf8').write(install)
launch=(B/'launch_E2_native60_V2_after_E3_full_allout_once.py').read_text().replace('V2','V3').replace("old=Path('/home/lc01/Zonglin Li/zonglin2/tasks/GraduationE3_2110v85_full750_v1')","old=Path('/home/lc01/Zonglin Li/zonglin2/tasks/GraduationE2_2110v85_native60_v2')")
(B/'launch_E2_native60_V3_after_failed_V2_allout_once.py').open('x',encoding='utf8').write(launch)
for oldname,newname in [('collect_E2_native60_V2_bounded_once.py','collect_E2_native60_V3_bounded_once.py'),('review_E2_native60_allrows_CPU_V2_once.py','review_E2_native60_allrows_CPU_V3_once.py'),('launch_E2_full750_after_nativeV2_CPU_once.py','launch_E2_full750_V3_after_nativeV3_CPU_once.py'),('collect_E2_full750_bounded_once.py','collect_E2_full750_V3_bounded_once.py'),('review_E2_full750_allrows_CPU_V2_once.py','review_E2_full750_allrows_CPU_V3_once.py')]:
 s=(B/oldname).read_text().replace('V2','V3').replace('native60_v2','native60_v3').replace('full750_v2','full750_v3')
 if 'full750' in oldname:s=s.replace("'E2_FULL750'","'E2_FULL750_V3'").replace("'E2_full750_actual'","'E2_full750_V3_actual'")
 (B/newname).open('x',encoding='utf8').write(s);ast.parse(s)
print(json.dumps(v))
