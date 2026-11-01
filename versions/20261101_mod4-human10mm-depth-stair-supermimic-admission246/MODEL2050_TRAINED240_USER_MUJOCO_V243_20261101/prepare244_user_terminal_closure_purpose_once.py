"""New human numerical question; freeze source/anchors before one local pose pass."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports';C=N.parent/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101'
def read(p):return json.loads(Path(p).read_bytes())
def H(b):return hashlib.sha256(b).hexdigest()
receipt=read(R/'ROOT243_SELECTED242_POSE_TRANSFERS_ACTUAL.json');pose=next(r for r in receipt['cases']if r['name']=='literal_jump')
purpose=read(R/'FROZEN243_FRESH_USER_DISPLAY_PURPOSE_BEFORE_IO.json');case=next(c for c in purpose['cases']if c['name']=='literal_jump');assert case['controls']==17 and case['original_terminal_flags']['closure']
manifest=read(C/'reports/INSTALL240_SOURCE_ASSET_MANIFEST.json');selected={}
for rel in('payload/job0/runtime/isaac/mod4/mod4_task.py','payload/job0/assets/import_contract.json'):
 row=next(r for r in manifest['files']if r['relative']==rel);p=C/'package'/rel;b=p.read_bytes();assert len(b)==row['bytes']and H(b)==row['SHA'];selected[rel]=dict(path=str(p),bytes=len(b),SHA=H(b),UTF8=b.decode('utf8'))
source=selected['payload/job0/runtime/isaac/mod4/mod4_task.py']['UTF8'];tree=ast.parse(source);names=['_closure_cache','closure_errors','closure_broken','_past_spawn_grace'];functions={n:ast.get_source_segment(source,next(f for f in tree.body if isinstance(f,ast.FunctionDef)and f.name==n))for n in names}
contract=read(C/'package/payload/job0/assets/import_contract.json');env=read(C/'package/E0_original_run_manifest_frozen_v1.json')['env'];grace=int(env.get('RM_SPAWN_GRACE_STEPS','10'))
v=dict(epoch=time.time(),kind='NEW244_USER_ASKED_TERMINAL_CLOSURE_EXCESS_SAVED242_JUMP',human_exact='我看过了，出发闭链终止时闭链误差超了多少？',pose=pose,source_case=case,body_names=purpose['body_names'],selected_npz_members=['body_position_w','body_quat_xyzw'],local_pose_byte_open=1,hash_and_np_load_from_same_bytes=1,selected_members_each=1,other_raw_models_SDK_GPU_remote_reads=0,original_threshold_m=.002,actual_original_spawn_grace_steps=grace,source_manifest_join_passed=True,source_identity=selected,original_function_segments=functions,closure_contract=contract['closures'],CPU_rotation_binding='Original saved242 SDK xyzw body quaternion; CPU float32 q-vector rotation v+2*w*cross(q.xyz,v)+cross(q.xyz,2*cross(q.xyz,v)); no renormalization. Original closure functions and anchor-to-world norm retained. This is a saved-pose CPU reconstruction, not a newly sampled original GPU scalar.',scope='Only this NEW242 literal_jump17frames. Report terminal sixloop norms/max/excess and immediately preceding frame; no new physics or model/optimizer, no broad performance statistics.')
with(R/'FROZEN244_USER_NUMERICAL_CLOSURE_PURPOSE_BEFORE_POSE_IO.json').open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
ast.parse((N/'read244_user_terminal_closure_CPU_once.py').read_text('utf8'))
print(json.dumps(dict(passed=True,manifest_source_join=True,closure_loops=len(contract['closures']),grace_steps=grace,pose_model_SDK_reads=0)))
