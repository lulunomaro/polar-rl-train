"""Prepare a new72 role; do not mutate195/194 or load model/raw data."""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
O=T/'E0_82_LITERAL_FUDAN_JUMP_PLANE_400N50_START_V195_20261031'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
with (R/'SOURCE198_PREPARATION_CONSUMED.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),user='e0分支可以交给子代理去启动，不浪费时间，训1个时，照一张空闲卡',
   source_only=True,model_reads=0,remote_or_GPU_or_GO_calls=0,sole_writer_owned_by_root=True),f,indent=2,ensure_ascii=False)
D=N/'package';shutil.copytree(O/'train_package',D)
task=json.loads((D/'TASK195.json').read_bytes());(D/'TASK195.json').unlink()
task.update(schema='mod4.E0_82.literal-original-JUMP72.400N50.D0-D7.one-hour.v198',kind='E0_82_FULLSTATE_JUMP72_ORIGINAL_REWARD',
 formal_source_model='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt',
 source_input_location_scope='Existing original72 published E0 formal; no new model upload or CPU reread',
 actual_target='72 genuine RTX4090 selected by fresh light resource query; no GPU PID query',
 worker_role='e0_72',shared_owner_scope='Root197 new unified cohort; worker never creates owner or writes canonical',
 starts_only_after194_closed_and_qualified=False,
 starts_only_after_root_unified_original_owner_GO=True,
 maximum_parent_seconds=3900,save_deadline_seconds=3600,exit_headroom_seconds=300,
 expected_next_iteration=31985,expected_first_Adam_step=641220,
 source_model_GPU_byte_reads=1,source_model_GPU_decodes=1,source_model_CPU_reads=0,
 source_reset_bank_scope='Original physical constructor only; no extra NPZ/raw decode or proof reread',
 physics_fresh_scope='Same approved400N50D0-D7 with new task physics/queues; no exact PhysX continuation claim',
 reward_core_source=str(D/'literal_original_methods.py'))
(D/'TASK198.json').write_text(json.dumps(task,indent=2,ensure_ascii=False),encoding='utf8')
s=(D/'run195_literal_jump_plane_worker.py').read_text('utf8')
s=s.replace("task=read(P/'TASK195.json')", "task=read(P/'TASK198.json')")
old=""" assert go['run_id']==args.run_id and go['max_parent_seconds']==3900 and go['save_deadline']>time.time()
 assert go['literal_jump195_400N50'] and go['source_model_SHA']==task['source_SHA']"""
new=""" from e0_jump198_task_protocol import validate_go
 assert validate_go(go,args.run_id,task,time.time())"""
assert old in s;s=s.replace(old,new)
s=s.replace('typed_JUMP195_task','typed_E0_JUMP198_task')
s=s.replace('ACTUAL_SOURCE195','ACTUAL_SOURCE198').replace('ACTUAL195','ACTUAL198')
s=s.replace('FudanJUMP195 reward/plane','literal pinned FudanJUMP reward/plane on72')
s=s.replace('source195_config_only_no_old_main','source198_config_only_no_old_main')
s=s.replace('Full delivered actor/critic/STD/Adam inherited','Full E0_82 actor/critic/STD/Adam inherited')
s=s.replace("  measured_state_bridge='root FD velocity rotated into current BODY; actual SDK q/dq/approximate applied motor effort; current77point originalFudanheight samples; true own hip-wheel BODY theta; exact original6 permutation and previous2 action history',", "  measured_state_bridge=real.binding_receipt(),")
ast.parse(s)
(D/'run195_literal_jump_plane_worker.py').unlink()
(D/'run198_E0_JUMP72_400N50_worker.py').write_text(s,encoding='utf8')
shutil.copyfile(N/'e0_jump198_task_protocol.py',D/'e0_jump198_task_protocol.py')
shutil.copyfile(D/'run198_E0_JUMP72_400N50_worker.py',N/'run198_E0_JUMP72_400N50_worker.py')
old=json.loads((O/'TRAIN195_COMPLETE_MANIFEST.json').read_bytes());known={r['relative']:r for r in old['files']}
rows=[]
for p in sorted(D.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(D).as_posix()
 if p.suffix.lower() in ('.usd','.usda','.npz','.npy'):
  k=known[rel];assert p.stat().st_size==k['bytes'];sha=k['SHA']
 else:
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if p.suffix=='.py':ast.parse(raw)
 rows.append(dict(relative=rel,local_relative='package/'+rel,bytes=p.stat().st_size,SHA=sha))
manifest=dict(schema=task['schema'],files=rows,models_uploaded=0,source_model_metadata_only=dict(path=task['formal_source_model'],SHA=task['source_SHA'],bytes=task['source_bytes'],new_CPU_reads=0,new_GPU_read_decode=1),
 worker_script='run198_E0_JUMP72_400N50_worker.py',role='e0_72')
(N/'PACKAGE198_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(dict(prepared=True,files=len(rows),bytes=sum(r['bytes'] for r in rows),model_reads=0)))
