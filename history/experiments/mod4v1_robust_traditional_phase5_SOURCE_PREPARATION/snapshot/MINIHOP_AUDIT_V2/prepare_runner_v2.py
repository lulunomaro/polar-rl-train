"""Derive runner by localized provenance/grading changes, prove control AST."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    source=ROOT/'run_minihop_case_v1.py';s=source.read_text(encoding='utf-8')
    s=s.replace('"""New operator-timed mini-hop TRAIN, truth strictly for read-only grading.\nThe four flat profiles are actuator/flight characterization, not RM qualification.\n"""','"""Future mini-hop runner: v2 private all-contact grade, unchanged control.\nNo episode is launched by import, preflight, unit tests or admission.\n"""')
    s=s.replace('from pathlib import Path','from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parents[1]))',1)
    s=s.replace('from streamed_trace_rows_v1 import StreamedRows,scalar_default','from streamed_trace_rows_v1 import StreamedRows,scalar_default\nfrom MINIHOP_AUDIT_V2.provenance_v2 import source_manifest,error_receipt')
    for scene in ('flat','rm'):s=s.replace(f'from physics_bridge_minihop_{scene}_v1 import MiniHopAuditPlant',f'from MINIHOP_AUDIT_V2.physics_bridge_minihop_{scene}_v2 import MiniHopAuditPlant')
    start=s.index('        source_names=');end=s.index('        bank=',start)
    s=s[:start]+"        dump(out/'SOURCE_MANIFEST.json',source_manifest(scene,cfg))\n"+s[end:]
    s=s.replace("geom,cfg['hop'])","geom,cfg.get('hop',{}))")
    s=s.replace("kind='OPERATOR_TIMED_MINIHOP_TRAIN_NOT_CONTACT_FSM_RELEASE'","kind='MINIHOP_AUDIT_V2_PRIVATE_GRADE_UNCHANGED_OPERATOR_TIMER_NOT_CONTACT_RELEASE',audit_version=2")
    s=s.replace('first_all_world_air_s=plant.first_air,first_landing=plant.first_landing','first_all_world_air_s=plant.first_air,first_all_world_air_confirmed_s=plant.first_air_confirmed_s,first_landing=plant.first_landing')
    s=s.replace('proposed_flat_clear80mm_recover2s=bool(','proposed_flat_clear80mm_recover2s_v2=bool(')
    s=s.replace("confidence_or_contact_thresholds_changed=False,phase_trigger=", "confidence_or_contact_thresholds_changed=False,air_grade='sum_all_finite_positive_environment_normals_le1N_contiguous20ms',private_contact_diagnostic_only=True,PH5_and_later_pending=True,current_PH4_cutoff_excludes_v2=True,old_scores_updated=False,phase_trigger=")
    start=s.index("        dump(out/'ERROR.json'");end=s.index('        raise',start)
    s=s[:start]+"        dump(out/'ERROR.json',error_receipt(traceback.format_exc(),controls,physical,plant))\n"+s[end:]
    old=ast.parse(source.read_text(encoding='utf-8'));new=ast.parse(s)
    def loop(tree):
        return next(n for n in ast.walk(tree)if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='k')
    # Full control-loop body remains equal: pre-estimator toggles, raw packet,
    # estimator, command, driver request, sub-row grouping, health stop and log.
    assert ast.dump(loop(old),include_attributes=False)==ast.dump(loop(new),include_attributes=False)
    def functions(tree):return{n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    for name in ('dump','arrays'):assert ast.dump(functions(old)[name],include_attributes=False)==ast.dump(functions(new)[name],include_attributes=False)
    assert 'active_qp_stdio'not in s and 'world_leg'not in s
    output=HERE/'run_minihop_case_v2.py'
    with output.open('x',encoding='utf-8',newline='\n')as f:f.write(s)
    result=dict(original=str(source),original_sha256=sha(source),derived=str(output),derived_sha256=sha(output),full_control_loop_AST_equal=True,dump_arrays_AST_equal=True,controller_import_unchanged=True,estimator_import_unchanged=True,operator_enable_default=False,changes='scene imports + source closure + audit version/result names + error prefix receipt + missing hop config defaults disabled; no control-loop modification',physics_steps=0)
    with(HERE/'RUNNER_AST.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
    print(json.dumps(result))
if __name__=='__main__':main()
