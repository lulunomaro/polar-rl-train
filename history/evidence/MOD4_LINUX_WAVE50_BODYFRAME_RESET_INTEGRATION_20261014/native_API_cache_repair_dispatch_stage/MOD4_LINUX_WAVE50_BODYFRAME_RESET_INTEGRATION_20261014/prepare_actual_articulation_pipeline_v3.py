"""Use the actual installed ArticulationView API; independent sources/root."""
from pathlib import Path
import hashlib,json,time
B=Path(__file__).resolve().parent;P=B/'payload_v1'
adapter=P/'birth_bodyframe_reset_adapter_v4.py';assert not adapter.exists()
src=(P/'birth_bodyframe_reset_adapter_v3.py').read_text(encoding='utf8')
anchor="                q30_unchanged=True, qd30_unchanged=True, XY_and_velocities_exact=True,"
assert src.count(anchor)==1
src=src.replace(anchor,"                original_q30=q30.cpu(), actual_q30_after=tensor(robot.data.joint_pos)[flipped].cpu().clone(),\n"+anchor)
adapter.write_text(src,encoding='utf8')
ck=P/'birth_bodyframe_full_checkpoint_v3.py';assert not ck.exists()
src=(P/'birth_bodyframe_full_checkpoint_v2.py').read_text(encoding='utf8')
src=src.replace('from birth_bodyframe_reset_adapter_v3 import','from birth_bodyframe_reset_adapter_v4 import')
assert src.count('robot.root_physx_view.get_transforms()')==1
src=src.replace('robot.root_physx_view.get_transforms()','robot.root_physx_view.get_root_transforms()')
anchor="        birth = adapter.after_existing_birth(ids)\n        adapter.install()"
replace="        birth = adapter.after_existing_birth(ids)\n        torch.save(birth, Path(log_dir) / 'BIRTH_BODYFRAME_ACTUAL_NATIVE_PLACEMENT_READBACK.pt')\n        Path(log_dir, 'BIRTH_BODYFRAME_ACTUAL_NATIVE_ABI_BEFORE.json').write_text(json.dumps(backend, indent=2), encoding='utf8')\n        adapter.install()"
assert src.count(anchor)==1;src=src.replace(anchor,replace);ck.write_text(src,encoding='utf8')
for oldname,newname in [('bodyframe_native_worker_v4.py','bodyframe_native_worker_v5.py'),('bodyframe_formal_worker_v2.py','bodyframe_formal_worker_v3.py')]:
    p=P/newname;assert not p.exists();p.write_bytes((P/oldname).read_bytes().replace(b'from birth_bodyframe_full_checkpoint_v2 import',b'from birth_bodyframe_full_checkpoint_v3 import'))
parent=P/'bodyframe_finite_pipeline_parent_v3.py';assert not parent.exists()
parent.write_bytes((P/'bodyframe_finite_pipeline_parent_v2.py').read_bytes().replace(b'bodyframe_native_worker_v4.py',b'bodyframe_native_worker_v5.py').replace(b'bodyframe_formal_worker_v2.py',b'bodyframe_formal_worker_v3.py'))
mat=B/'bodyframe_target_materialize_CPU_v2.py';assert not mat.exists()
mat.write_bytes((B/'bodyframe_target_materialize_CPU_v1.py').read_bytes().replace(b'from birth_bodyframe_full_checkpoint_v2 import',b'from birth_bodyframe_full_checkpoint_v3 import'))
transport=B/'transport_bodyframe_pipeline_v3.py';assert not transport.exists()
transport.write_text("from transport_bodyframe_root_owned import *\nROOT=BASE+'/bodyframe20k_repair_pipeline_v3_articulation_api_20261014'\n",encoding='utf8')
src=(B/'materialize_and_dispatch_bodyframe_pipeline_v2_once.py').read_text(encoding='utf8')
for before,after in [('transport_bodyframe_pipeline_v2','transport_bodyframe_pipeline_v3'),('birth_bodyframe_reset_adapter_v3.py','birth_bodyframe_reset_adapter_v4.py'),('birth_bodyframe_full_checkpoint_v2.py','birth_bodyframe_full_checkpoint_v3.py'),('bodyframe_native_worker_v4.py','bodyframe_native_worker_v5.py'),('bodyframe_formal_worker_v2.py','bodyframe_formal_worker_v3.py'),('bodyframe_finite_pipeline_parent_v2.py','bodyframe_finite_pipeline_parent_v3.py'),('bodyframe_target_materialize_CPU_v1.py','bodyframe_target_materialize_CPU_v2.py'),('unique_upload_v2_lazy_query','unique_upload_v3_articulation_api'),('PIPELINE_V2_MATERIALIZE','PIPELINE_V3_MATERIALIZE')]:src=src.replace(before,after)
dispatch=B/'materialize_and_dispatch_bodyframe_pipeline_v3_once.py';assert not dispatch.exists();dispatch.write_text(src,encoding='utf8')
collector=B/'collect_bodyframe_finite_pipeline_v3_actual.py';assert not collector.exists()
collector.write_text((B/'collect_bodyframe_finite_pipeline_v2_actual.py').read_text(encoding='utf8').replace('transport_bodyframe_pipeline_v2','transport_bodyframe_pipeline_v3'),encoding='utf8')
for p in (adapter,ck,P/'bodyframe_native_worker_v5.py',P/'bodyframe_formal_worker_v3.py',parent,mat,dispatch,collector):compile(p.read_bytes(),str(p),'exec')
report=B/'reports/ARTICULATION_GET_ROOT_TRANSFORMS_V3_INDEPENDENT_REPAIR_ACTUAL.json';assert not report.exists()
report.write_text(json.dumps(dict(epoch=time.time(),original_v2_error='ArticulationView has no get_transforms; original13 restores already verified before this new audit failure',
    actual_installed_source_receipt='ARTICULATION_ACTUAL_INSTALLED_SOURCE_STDLIB_V2_1791979069317049400.json',
    actual_API='ArticulationView.get_root_transforms returns root link xyz+xyzw; root_state_w pose uses the same underlying getter',
    prior_source_reader_missing_rg_error_retained=True,no_physics_or_query_tolerance_changed=True,
    extra_own_native_readback_PT_includes_original_and_after_root_q30=True,
    no_old_GPU_retry_or_hotpatch=True,new_root='bodyframe20k_repair_pipeline_v3_articulation_api_20261014',
    source_SHA={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (adapter,ck,parent)}),indent=2),encoding='utf8')
print(json.dumps(dict(actual_native_API_source_bound=True,new_v3_sources_compiled=True)))
