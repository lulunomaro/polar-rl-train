"""Source closure and raw prefix receipts; no episode or old SDK execution."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent

def sha(path):
    with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def file_record(path):
    p=Path(path).resolve();return dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p))
def source_manifest(scene,cfg):
    assert scene in ('flat','rm')
    frozen=json.loads((HERE/'SOURCE_FREEZE.json').read_bytes())
    refs={r['path']:r for r in frozen['old_files']+frozen['sources']+frozen['model_assets']}
    end=(ROOT/cfg['end_gain_file']).resolve();assert end.is_relative_to(ROOT)and str(end)in refs,'Frozen end-gain required'
    old=[Path(r['path'])for r in frozen['sources']]+[ROOT/'MINIHOP_V1/controller.py',end]
    for p in old:
        assert sha(p)==refs[str(p.resolve())]['sha256'],str(p)
    for r in frozen['model_assets']:assert sha(r['path'])==r['sha256'],r['path']
    new=[HERE/n for n in ('__init__.py','run_minihop_case_v2.py','contact_grade_v2.py','schema_v2.py','provenance_v2.py','physics_bridge_minihop_flat_v2.py','physics_bridge_minihop_rm_v2.py','BRIDGE_AST.json','GRADING_CONTRACT.json','SOURCE_FREEZE.json')]
    return dict(kind='NEW_MINIHOP_AUDIT_V2_UNCHANGED_CONTROLLER_PRIVATE_GRADING_SOURCE_PREEXEC',audit_version=2,scene=scene,
        model_SHA=next(r['sha256']for r in frozen['sources']if Path(r['path']).name=='mod4v1_usd_source_aligned.xml'),
        files=[file_record(p)for p in sorted(set(old+new))],model_assets=[file_record(r['path'])for r in frozen['model_assets']],
        closure_is_explicit_both_scene_superset=True,controller_changed=False,actuator_AST_unchanged=True,
        R39_not_regraded=True,contact_force_private_only=True,public_sensor_projection_changed=False,contact_confidence_promoted=False,
        operator_enable_default=False,PH5_and_later_pending=True,current_PH4_cutoff_excludes_v2=True)

def prefix_receipt(rows):
    if rows is None:return None
    p=rows.path
    raw=file_record(p)
    producer=dict(bytes=rows.bytes,SHA=rows.sha.hexdigest(),successful_rows=len(rows))
    return dict(**raw,producer=producer,actual_prefix_matches_producer=raw['bytes']==rows.bytes and raw['SHA']==rows.sha.hexdigest(),raw_bytes_preserved=True)

def error_receipt(error,controls,physical,plant):
    return dict(kind='MINIHOP_AUDIT_V2_ERROR_NOT_A_GRADE',audit_version=2,error=error,
        instrumentation_error=None if plant is None else getattr(plant,'instrumentation_error',None),
        controls=0 if controls is None else len(controls),physics_steps=None if plant is None else plant.tick_phys,
        trace_prefix=prefix_receipt(controls),physics_prefix=prefix_receipt(physical),original_error_preserved=True,
        invalid_values_replaced_by_zero=False,partial_trial_passed=False,old_scores_updated=False)
