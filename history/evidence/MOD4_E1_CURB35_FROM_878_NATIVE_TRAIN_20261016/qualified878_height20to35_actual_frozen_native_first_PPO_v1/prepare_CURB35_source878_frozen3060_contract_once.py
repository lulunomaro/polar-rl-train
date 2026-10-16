"""New height35 frozen source878 admission. Preserve old loops and explicit AST delta."""
from pathlib import Path
import ast,hashlib,json,shutil,time,zipfile
D=Path(__file__).resolve().parent;OLD=D.parent/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016';E=D/'frozen35_3060_v1';Q=E/'eval_payload_v2';R=E/'reports';ROOT='D:/MOD4_async_eval/'+D.name;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not E.exists();shutil.copytree(OLD/'eval_payload_v2',Q,ignore=shutil.ignore_patterns('__pycache__'));R.mkdir()
C=Q/'runtime/isaac/mod4'
for n in ('curb35_profile.json','curb35_geometry.py'):shutil.copy2(D/'payload/job0/runtime/isaac/mod4'/n,C/n)
worker=Q/'paired_full80_parameter_bound_v2.py';s=worker.read_text();s=s.replace("lease['namespace']=='MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016'","lease['namespace']=="+repr(E.name));worker.write_text(s)
p=Q/'curb_worldmesh_query_contract_v1.py';p.write_text(p.read_text().replace('from curb20_geometry import make_mesh','from curb35_geometry import make_mesh'))
p=Q/'full80_runtime_native_v1.py';orig=p.read_text();s=orig.replace('from curb20_geometry import configure_curb as configure_intro','from curb35_geometry import configure_curb as configure_intro').replace('.020','.035').replace('derived20mm_vertical','derived35mm_vertical').replace('approved_CURB20_final878','new_CURB35_frozen_source878')
old="assert source['E1_terrain_state']['geometry_triangles_sha256']==ray.geometry.receipt()['triangles_sha256']\n    assert source['E1_terrain_state']['ordered_partition_triangles_sha256']==e.scene.terrain.exact_partition_receipt['triangle_world_f32_order_sha256']"
new="assert source['E1_terrain_state']['CURB_height_m']==.020 and source['E1_terrain_state']['CURB_strip_width_m']==.150\n    assert source['E1_terrain_state']['geometry_triangles_sha256']!=ray.geometry.receipt()['triangles_sha256']\n    save('CURB20_SOURCE_TO_35_NEW_GEOMETRY_ACTUAL.json',dict(source_height_m=.020,actual_new_height_m=.035,source_only_actor_loaded=True,new_geometry_not_claimed_saved_source_same_scope=True,source_mesh_SHA=source['E1_terrain_state']['geometry_triangles_sha256'],actual_mesh=ray.geometry.receipt(),actual_partition=e.scene.terrain.exact_partition_receipt))"
assert old in s;s=s.replace(old,new);compile(s,str(p),'exec');p.write_text(s)
inverse=s.replace(new,old).replace('from curb35_geometry import configure_curb as configure_intro','from curb20_geometry import configure_curb as configure_intro').replace('.035','.020').replace('derived35mm_vertical','derived20mm_vertical').replace('new_CURB35_frozen_source878','approved_CURB20_final878');assert ast.dump(ast.parse(inverse))==ast.dump(ast.parse(orig))
mfile=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';m=json.loads(mfile.read_bytes());m['source_single_policy']['local_path']=ROOT+'/payload/source/CURB_final878.pt';m['explicit_new_scope']='Original source20mm actor evaluated on35mm; no fullstate geometry equality claimed'
for n in ('curb35_profile.json','curb35_geometry.py'):m['file_rows'].append(dict(relative='runtime/isaac/mod4/'+n,bytes=(C/n).stat().st_size,sha256=H(C/n)))
for row in m['file_rows']:
 p=Q/row['relative'];row.update(bytes=p.stat().st_size,sha256=H(p))
mfile.write_text(json.dumps(m,indent=2))
oldE=OLD/'curb113_frozen_v2'
replacements=[('CURB113','CURB35_SOURCE878'),('curb_independent113','curb35_source878'),('MOD4_CURB113_3060','MOD4_CURB35_SOURCE878_3060'),('3d2b0b6d9260383031e0c198501224fdaedefef9c283b43ce588419319b5de88','268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1'),('source/CURB113.pt','source/CURB_final878.pt')]
for name in ('dispatch_curb113_frozen3060_unused_case_once.py','collect_curb113_own_case_actual_readonly.py','review_curb113_actual_physical_source_route_CPU.py','finish_existing_native_then_unused_full_finite_v2_once.py'):
 s=(oldE/name).read_text();s=s.replace('D:/MOD4_async_eval/MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/curb113_frozen_v2',ROOT)
 for a,b in replacements:s=s.replace(a,b)
 if name.startswith('dispatch'):
  s=s.replace('len(ts)==185','len(ts)==181').replace('sum(x.is_floating_point() for x in ts)==105','sum(x.is_floating_point() for x in ts)==102').replace('floating=105','floating=102')
 if name.startswith('review'):s=s.replace("scope['height_m']==.02","scope['height_m']==.035")
 if name.startswith('finish'):
  s=s.replace("ROOT='D:/MOD4_async_eval/'+E.parent.name+'/'+E.name","ROOT='D:/MOD4_async_eval/'+E.parent.name")
  s=s.replace("for steps in (120,1500):","run('dispatch_curb113_frozen3060_unused_case_once.py',['--steps','120','--execute-own-unused-case'])\n for steps in (120,1500):")
 compile(s,name,'exec');(E/name).write_text(s)
z=E/'CURB35_SOURCE878_FROZEN_3060_V1.zip'
with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as a:
 for p in sorted(Q.rglob('*')):
  if p.is_file():a.write(p,p.relative_to(Q).as_posix())
prep=json.loads((OLD/'reports/CURB878_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').read_bytes());prep.update(epoch=time.time(),passed_CPU_only=True,source=m['source_single_policy'],package=dict(path=str(z.resolve()),bytes=z.stat().st_size,sha256=H(z)),manifest_SHA=H(mfile),worker_SHA=H(worker),runtime_SHA=H(Q/'full80_runtime_native_v1.py'),height_axis35_new_scope=True,physical_loop_inverse_AST_exact_except_declared_geometry_height_and_source_scope_witness=True,not_target_native_or_PPO_pass=True)
(R/'CURB35_SOURCE878_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').write_text(json.dumps(prep,indent=2));print(json.dumps(dict(package=prep['package'],new_height=.035,target_native_full_pending=True)))
