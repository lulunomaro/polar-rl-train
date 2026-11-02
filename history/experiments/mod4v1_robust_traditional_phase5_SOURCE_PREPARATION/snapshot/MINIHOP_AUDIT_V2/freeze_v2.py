"""Hash-only freeze: no import of old runners, physics, SDK, or model construction."""
from pathlib import Path
import ast, hashlib, json, xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OLD=ROOT.parent/'traditional_control_20261101'

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def record(p):
    p=p.resolve();return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def dump(name,value):
    with (HERE/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)

def main():
    previous=ROOT/'SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1'
    frozen=json.loads((previous/'SOURCE_FREEZE.json').read_bytes());old={}
    def add(p,expected=None):
        r=record(p)
        if expected is not None:assert r['sha256']==expected,str(p)
        old[r['path']]=r
    for r in frozen['old_files']:add(Path(r['path']),r['sha256'])
    for r in json.loads((previous/'INDEX.json').read_bytes())['files']:add(Path(r['path']),r['sha256'])
    for n in ('INDEX.json','VALIDATION.json','MANIFEST.json','seal_01.log','seal_02.log'):add(previous/n)
    # Explicit paths admitted by host glob and inspected old source; no score parse.
    old_names=['MINIHOP_V1/'+n for n in ('contact_grade.py','controller.py','BRIDGE_AST.json','preflight.py','preflight001.log','preflight001/SOURCE_PREEXEC.json','preflight001/RESULT.json')]
    old_names+=['prepare_minihop_bridges_v1.py','physics_bridge_minihop_flat_v1.py','physics_bridge_minihop_rm_v1.py','run_minihop_case_v1.py','launch_r39_minihop4.py']
    cases=['r39_flat_d0_p10','r39_flat_d20_p10','r39_flat_d0_p14','r39_flat_d20_p14']
    for c in cases:
        old_names+=['results/'+c+'/'+n for n in ('config.json','SOURCE_MANIFEST.json','physics.jsonl','trace.jsonl','result.json')]
        old_names+=['batches/r39_minihop4/'+c+s for s in ('.json','.log')]
    old_names+=['batches/r39_minihop4/PROTOCOL.json','batches/r39_minihop4/BATCH_RESULT.json']
    for n in old_names:add(ROOT/n)
    sources=[ROOT/n for n in ('physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','physics_bridge_rm_grid_v1.py','physics_bridge_rm_buffer_v1.py','physics_bridge_rm_grade_v1.py','streamed_trace_rows_v1.py','sensor_core.py','sensor_core_v4.py','sensor_core_jump_v1.py','ground_controller_v4.py','rm_grid_terrain_v1.py','MODEL_AUDIT/mesh_support_helper_v1/mesh_support.py','MODEL_AUDIT/mod4v1_usd_source_aligned.xml','MODEL_AUDIT/MESH_DEPENDENCIES.json','JUMP270_V1/GAIN_BANK.json','TALL_ROUGH_BANK_V1/gain_delta0.json','TALL_ROUGH_BANK_V1/gain_delta20.json')]
    sources += [OLD/n for n in ('full_lqr.py','control_core.py','kinematics.py','dr_components.py','model_parameters.json','reports/model_manifest.json')]
    auth=ROOT.parent/'mod4v1_experts_fulldr_rm70_20261101/E1_actual_qualification_v1/SLOPE135_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4'
    sources += [auth/'pinned_source/height_field.py',auth/'ROUGH_V1_RESOLVED_RECIPE.json']
    source_rows=[record(p) for p in sources]
    for p in sources:
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
    xml=ROOT/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml'
    assets=sorted({(xml.parent/n.attrib['file']).resolve() for n in ET.fromstring(xml.read_bytes()).findall('.//mesh') if 'file'in n.attrib})
    asset_rows=[record(p) for p in assets]
    assert sha(ROOT/'MINIHOP_V1/controller.py')==next(r['sha256']for r in old.values()if r['path']==str((ROOT/'MINIHOP_V1/controller.py').resolve()))
    dump('SOURCE_FREEZE.json',dict(scope='NEW_PRIVATE_MINIHOP_AUDIT_V2_ONLY',old_files=list(old.values()),sources=source_rows,model_assets=asset_rows,R39_artifacts_hashed_only_not_regraded=True,new_physics_steps=0,old_preflight_executed=False,root_active_world_leg_touched=False))
    dump('GRADING_CONTRACT.json',dict(version=2,world_environment='all geom_bodyid == 0, independent of contype/conaffinity; exactly one world endpoint',normal_aggregation='math.fsum(max(0, fn)) over ALL world↔robot points BEFORE threshold',air_total_normal_N_lte=1.,minimum_air_interval_s=.02,physics_dt_s=.0005,air_duration='contiguous tick count * physics_dt; no per-contact cutoff',landing_contacts='every positive world↔robot point, including sub-1N; original ci and both geom/body identities',contact_force_world='force on geom2 = ct.frame.reshape(3,3).T @ local_force[:3]; robot geom1 negates',nonfinite='explicit latched instrumentation error, last good streamed prefix retained; never zero fill',stage_clock_tolerance_s=1e-8,clock_tolerance_does_not_change_force_or_duration_threshold=True,private_diagnostic='force sum + actual model body-mass sum + optional existing cached pre-stage root rotation/subtreeCOM; not complete trueCOMproper',public_projection_changed=False,controller_changed=False,operator_default_enabled=False,contact_FSM_MPC_permission_added=False,PH5_and_later_pending=True,current_PH4_cutoff_excludes_v2=True))
    print(json.dumps(dict(status='HASH_ONLY_FROZEN',old_files=len(old),source_refs=len(source_rows),model_assets=len(asset_rows),R39_scores_parsed_or_changed=False,physics_steps=0)))
if __name__=='__main__':main()
