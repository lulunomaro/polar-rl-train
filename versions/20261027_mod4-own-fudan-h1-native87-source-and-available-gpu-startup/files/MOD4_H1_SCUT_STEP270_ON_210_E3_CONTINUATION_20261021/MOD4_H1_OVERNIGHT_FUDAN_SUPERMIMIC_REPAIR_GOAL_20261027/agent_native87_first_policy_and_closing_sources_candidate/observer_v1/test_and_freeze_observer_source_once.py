"""Synthetic first-publication metadata only; no observer/network/model execution."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ast,json,copy,hashlib,traceback,datetime,types
D=Path(__file__).resolve().parent;L=D.parent.parent;T=L.parent
module=types.ModuleType('observer_protocol');exec(compile((D/'native87_observer_protocol_v1.py').read_text(),str(D/'native87_observer_protocol_v1.py'),'exec'),module.__dict__)
entry=D/'observe_three_H1_native87_first_GO_policy_finite_unused_once.py';tree=ast.parse(entry.read_text())
rows=[]
def case(name,fn):
 try:detail=fn();rows.append(dict(name=name,passed=True,detail=detail))
 except Exception:rows.append(dict(name=name,passed=False,error=traceback.format_exc()))
def reject(fn):
 try:fn()
 except (ValueError,KeyError):return True
 raise AssertionError('expected rejection')
source=module.SOURCE_SHA
spec=dict(source_SHA=source,manifest_SHA='a'*64,seed=27,reference_artifact_SHA='b'*64)
go=dict(source_SHA=source,bootstrap_SHA=source,bootstrap_Adam=832460,source_qualification_kind=module.KIND,native_continuation_restore_required=False,manifest_SHA='a'*64,seed=27,num_envs=4096)
first=dict(policy_updates=1,world_updates=650,updates=65,path='/fixture/positive.pt',SHA='c'*64,bytes=123,before_control=240,
    original_source_actor_frozen_not_PPO_learning=True,not_PPO_or_production_source=True,native_actual_method='own_MOD4_converted_Fudan_jump_native_v3')
index=dict(controls=241,preupdate_full_sources=[dict(path=first['path'],SHA=first['SHA'],bytes=123,before_control=240,no_optimizer_call=True)])
pre=dict(actual_GPU_runtime_readback_passed=True,before_first_native_physical_control_and_Pi=True,actual_environment_count=4096,
    actual_static_context_dim=31,actual_dynamic_aux_dim=54,packed_state_dim=127,actor_obs_dim=86,goal_frame_dim=146,
    source_SHA=source,actual_reference_SHA='b'*64,actual_physics_dt=.0025,actual_control_dt=.01,actual_solver=[1,32,4],legacy_native86_model_or_optimizer_loaded=False,
    new_native_model_initialization=True,actual_joint_names=['j'+str(i) for i in range(30)],actual_body_names=['b'+str(i) for i in range(31)],
    actual_source_policy_bootstrap=dict(policy_actor9_critic8_STD6_17Adam832460_exact=True,old20k_environmental_state_restored=False))
case('synthetic_positive_new_publication_only',lambda:module.validate_first_positive(first,index,pre,go,spec))
for field,value in [('policy_updates',0),('before_control',226),('SHA','d'*64),('not_PPO_or_production_source',False)]:
 def bad(field=field,value=value):r=dict(first);r[field]=value;return reject(lambda:module.validate_first_positive(r,index,pre,go,spec))
 case('reject_stale_or_wrong_'+field,bad)
for field,value in [('actual_GPU_runtime_readback_passed',False),('actual_environment_count',20000),('legacy_native86_model_or_optimizer_loaded',True)]:
 def bad(field=field,value=value):r=dict(pre);r[field]=value;return reject(lambda:module.validate_first_positive(first,index,r,go,spec))
 case('reject_precontrol_'+field,bad)
for node in tree.body:
 if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str) and any(isinstance(t,ast.Name) and t.id in ('OWNER_READ','TARGET_READ') for t in node.targets):
  name=node.targets[0].id;code=node.value.value;case('compile_'+name,lambda code=code,name=name:compile(code,name,'exec') is not None)
text=entry.read_text()
case('explicit_own_parent_import_source',lambda:'sys.path.insert(0,str(Path(__file__).resolve().parent))' in text)
case('all3_native_no_normal20Adam_gate',lambda:'>58' not in text and '>680' not in text and 'phase_optional_not_model_gate=True' in text)
report=dict(passed=all(r['passed'] for r in rows),passed_count=sum(r['passed'] for r in rows),total=len(rows),tests=rows,
    all_metadata_positive_is_synthetic=True,no_actual_observer_process_model_checkpoint_or_network=True)
with (D/'OBSERVER_SOURCE_METADATA_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
assert report['passed']
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=[L/'root_native_bridge_integration_candidate/native_own_fudan87_training.py',L/'root_native_bridge_integration_candidate/native_finalization_own_v3.py',
    L/'native87_dispatcher_v3/native87_closed_source_CPU_v1.py',T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/observe_three_gpu86B_first_GO_updates_phase_finite_V2_unused_once.py']
with (D/'SOURCE_LINEAGE_AND_READER_ERRORS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sources],
    reader_errors=['PowerShell Select-Object -Index comma-separated ranges reader conversion error; corrected by reading separate slices, no source mutation.'],
    no_PT_raw_or_model_read=True),f,indent=2)
with (D/'FROZEN_OBSERVER_HANDOFF.md').open('x',encoding='utf8') as f:f.write('''Unused native87 first-positive observer source frozen. Explicit parent import supports transport runpy. Reads actual exe/argv/create/cwd using exact approved210Python/72ld recipe; actual worker UUID and signedGO source/manifest/seed/cap; actual GPU precontrol4096+127/54/31/86/146; all3 fresh nativePi>0.
First-positive proof must match trace preupdate source path/SHA/bytes/before_control, with source-pinned publication.policy_updates>0 and same-source/control guard. A positive counter with old216 checkpoint is rejected; no PT/raw or checkpoint hash reads. Phase sample metadata optional, not model/skill gate. Finite first-positive wait1200; failure/timeout text preserved, no training/stop/budget writes. All-three only: does not invent missing-ready cards or pretend a future available-card schedule is admitted.
CPU12/12 synthetic metadata/source compile only; actual observer never executed. Owner file root kept separate from global72 cwd. Collector/reviewer will be separate sibling sources. Root must add exact observer basename to finite transport allowlist and run only against actual detached report after activation.\n''')
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
files=[dict(path=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='FROZEN_OBSERVER_SHA_INDEX.json']
with (D/'FROZEN_OBSERVER_SHA_INDEX.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_at_UTC=stamp,files=files,count_excluding_index=len(files),parent_archive_pending=True),f,indent=2)
print(json.dumps(dict(passed=report['passed'],CPU=str(report['passed_count'])+'/'+str(report['total']),frozen_at_UTC=stamp,entry_SHA=H(entry),index_SHA=H(D/'FROZEN_OBSERVER_SHA_INDEX.json'))))
