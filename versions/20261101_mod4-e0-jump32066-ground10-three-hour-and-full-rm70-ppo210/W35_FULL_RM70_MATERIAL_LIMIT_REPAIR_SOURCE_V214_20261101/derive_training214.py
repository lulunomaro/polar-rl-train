"""Unused after-probe training candidate: only the shared-field source changes.

The diagnostic MildDR observer/extra same-value reapply are not training code.
No actor/model/SDK or CPU fixture is invoked by this text derivation.
"""
from pathlib import Path
import hashlib,json,time
H=Path(__file__).resolve().parent;P=H.parent/'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031'


def main():
    with (H/'reports/TRAINING214_SOURCE_ONCE.json').open('x')as f:json.dump(dict(
        ID='NEW214_AFTER_CAPACITY_PROBE_TRAINING_SOURCE_ONLY',epoch=time.time()),f)
    pairs=[
        (P/'adapter_v3/config208_v3.py','config214_training.py',[
            ('from field208 import make_terrain_cfg','from field214 import make_terrain_cfg')]),
        (P/'adapter_v3/train_full208_v3.py','train_full214.py',[
            ('from config208_v3 import configure208 as configure_intro','from config214_training import configure208 as configure_intro')]),
        (P/'adapter_v3/worker_full208_v3.py','worker_full214.py',[
            ('MOD4_W35_FULL_RM70_208_V3','MOD4_W35_FULL_RM70_MATERIAL_SHARED214'),
            ("entry=mod/'train_full208_v3.py'","entry=mod/'train_full214.py'"),
            ("assert task['new_RM70_geometry_course_and_xyzw_source_reviewed'] is True",
             "assert task['new_RM70_geometry_course_and_xyzw_source_reviewed'] is True\n    assert task['actual_shared_material20k0PT_passed'] is True\n    assert task['actual_material_limit_error_count']==0")])]
    rows=[]
    for old,name,changes in pairs:
        raw=old.read_bytes();value=raw.decode('utf8').replace('\r\n','\n')
        for before,after in changes:
            if value.count(before)!=1:raise ValueError('Training source inverse mismatch: '+before)
            value=value.replace(before,after)
        dest=H/'source'/name
        with dest.open('x',encoding='utf8',newline='\n')as f:f.write(value)
        rows.append(dict(source=str(old),source_SHA=hashlib.sha256(raw).hexdigest(),output=str(dest),
            bytes=dest.stat().st_size,SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),changes=changes))
    with (H/'reports/TRAINING214_AFTER_PROBE_SOURCE_ONLY.json').open('x')as f:json.dump(dict(
        ID='NEW214_AFTER_CAPACITY_PROBE_TRAINING_SOURCE_ONLY',rows=rows,
        original_mildDR_class_sampling_and_RNG_unchanged=True,
        probe_MildDR_observer_and_extra_ownstate_reapply_not_used_in_training=True,
        original_35_38_6_400N50_TGS32_4_guards_fullstate_cache_and_parent_ABI_unchanged=True,
        no_current_owner_hotadd_or_code_change=True,
        promotion_requires_actual20k_capacity_probe_zero_64K_logs_and_root_actual_source_JOIN=True,
        source_only_not_new_training_permission_or_GO=True,child_model_SDK_GPU_remote_or_tests=0),f,indent=2)


if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        with (H/'reports'/('TRAINING214_SOURCE_ERROR_'+str(time.time_ns())+'.json')).open('x')as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
        raise
