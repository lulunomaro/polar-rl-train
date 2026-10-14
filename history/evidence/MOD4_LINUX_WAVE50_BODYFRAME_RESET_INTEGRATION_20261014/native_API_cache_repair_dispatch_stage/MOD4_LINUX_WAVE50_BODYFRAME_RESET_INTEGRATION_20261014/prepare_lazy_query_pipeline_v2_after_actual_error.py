"""Independent pre-Kit import-order repair; all original attempts stay unchanged."""
from pathlib import Path
import hashlib,json,time
B=Path(__file__).resolve().parent;P=B/'payload_v1'
changes=[]
for oldname,newname in [('bodyframe_native_worker_v3.py','bodyframe_native_worker_v4.py'),('bodyframe_formal_worker_v1.py','bodyframe_formal_worker_v2.py')]:
    old=P/oldname;new=P/newname;assert not new.exists();text=old.read_text(encoding='utf8')
    if oldname.startswith('bodyframe_native'):
        before="    from wave50_entry_full_pose_reset_v2 import query\n    patch(original, manifest, typed, query, fixture=False)"
        after="    def query(env):\n        from wave50_entry_full_pose_reset_v2 import query as actual_query\n        return actual_query(env)\n    patch(original, manifest, typed, query, fixture=False)"
    else:
        before="    from wave50_entry_full_pose_reset_v2 import query\n    patch(original,manifest,typed,query,fixture=False)"
        after="    def query(env):\n        from wave50_entry_full_pose_reset_v2 import query as actual_query\n        return actual_query(env)\n    patch(original,manifest,typed,query,fixture=False)"
    assert text.count(before)==1;new.write_text(text.replace(before,after),encoding='utf8');compile(new.read_bytes(),str(new),'exec')
    changes.append(dict(original=oldname,original_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),new=newname,new_SHA=hashlib.sha256(new.read_bytes()).hexdigest()))
old=P/'bodyframe_finite_pipeline_parent_v1.py';new=P/'bodyframe_finite_pipeline_parent_v2.py';assert not new.exists()
new.write_bytes(old.read_bytes().replace(b'bodyframe_formal_worker_v1.py',b'bodyframe_formal_worker_v2.py').replace(b'bodyframe_native_worker_v3.py',b'bodyframe_native_worker_v4.py'))
compile(new.read_bytes(),str(new),'exec')
transport=B/'transport_bodyframe_pipeline_v2.py';assert not transport.exists()
transport.write_text("from transport_bodyframe_root_owned import *\nROOT=BASE+'/bodyframe20k_repair_pipeline_v2_lazy_query_20261014'\n",encoding='utf8')
src=(B/'materialize_and_dispatch_bodyframe_pipeline_once.py').read_text(encoding='utf8')
src=src.replace('import transport_bodyframe_root_owned as t','import transport_bodyframe_pipeline_v2 as t')
src=src.replace('bodyframe_native_worker_v3.py','bodyframe_native_worker_v4.py').replace('bodyframe_formal_worker_v1.py','bodyframe_formal_worker_v2.py').replace('bodyframe_finite_pipeline_parent_v1.py','bodyframe_finite_pipeline_parent_v2.py')
src=src.replace('.bodyframe_pipeline_unique_upload_v1_20261014','.bodyframe_pipeline_unique_upload_v2_lazy_query_20261014').replace('BODYFRAME_PIPELINE_MATERIALIZE_DISPATCH_INTENT.json','BODYFRAME_PIPELINE_V2_MATERIALIZE_DISPATCH_INTENT.json')
dispatch=B/'materialize_and_dispatch_bodyframe_pipeline_v2_once.py';assert not dispatch.exists();dispatch.write_text(src,encoding='utf8');compile(src,str(dispatch),'exec')
collector=B/'collect_bodyframe_finite_pipeline_v2_actual.py';assert not collector.exists()
collector.write_text((B/'collect_bodyframe_finite_pipeline_actual.py').read_text(encoding='utf8').replace('import transport_bodyframe_root_owned as t','import transport_bodyframe_pipeline_v2 as t'),encoding='utf8')
receipt=B/'reports/PREKIT_QUERY_IMPORT_ORIGINAL_ERROR_AND_INDEPENDENT_LAZY_V2.json';assert not receipt.exists()
receipt.write_text(json.dumps(dict(epoch=time.time(),original_root='bodyframe20k_repair_pipeline_v1_20261014',
    actual_error='Query module imported mod4_task/IsaacLab environment before AppLauncher; isaaclab_physx extension not yet available',
    before_Kit_physics_and_PPO=True,original_child_exit1_naturally=True,original_parent_load_probe_save_exit_seconds=1.2862696647644043,
    canonical_cost_0PPO_uncharged=True,no_installed_package_edit=True,
    repair='Defer only the actual query import until resume calls it after AppLauncher',changes=changes,
    new_independent_root='bodyframe20k_repair_pipeline_v2_lazy_query_20261014',no_old_once_replay=True),indent=2),encoding='utf8')
print(json.dumps(dict(new_workers_compile_passed=True,old_preKit_failure_preserved=True)))
