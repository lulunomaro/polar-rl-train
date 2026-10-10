"""New diagnostic SDK placement: use recorded generated support cells, retain refusals."""
from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;R=D/'reports';S=D/'signature_repair_payload';P=D/'assignment_reviewed_payload';P.mkdir(exist_ok=True)
def main():
 assert not (R/'ASSIGNMENT_SELECTOR_PREPARED.json').exists()
 s=(S/'native_e1_retention_sdk_reviewed_probe.py').read_text()
 old="  plane=[r for r in env.scene.terrain.retention_assignment if r['family']=='plane_for_rm' and r['actual_mesh_flat'] and 17<=r['row']<=21 and r['column'] in (9,10)]\n  assert len(plane)==10"
 assert s.count(old)==1
 new="""  assignments=env.scene.terrain.retention_assignment
  original_pick=[r for r in assignments if r['family']=='plane_for_rm' and r['actual_mesh_flat'] and 17<=r['row']<=21 and r['column'] in (9,10)]
  candidates=[r for r in assignments if r['family']=='plane_for_rm' and r['actual_mesh_flat']]
  Path(args.output+'.assignment.json').write_text(json.dumps(dict(actual_assignments=assignments,original_selector_count=len(original_pick),valid_plane_count=len(candidates),assignment_sha256=env.scene.terrain.retention_assignment_sha,diagnostic_before_any_probe_control=True),indent=2))
  candidates.sort(key=lambda r:sum(((r['bounds'][0][i]+r['bounds'][1][i])*.5)**2 for i in (0,1)))
  assert len(candidates)>=10,('Actual generated flat supports missing',len(candidates))
  plane=candidates[:10]
"""
 s=s.replace(old,new);ast.parse(s);(P/'native_e1_retention_assignment_reviewed_probe.py').write_text(s,encoding='utf8')
 s=(S/'supervise_e1_command_retention_sdk_reviewed_once.py').read_text()
 s=s.replace('native_e1_retention_sdk_reviewed_probe.py','native_e1_retention_assignment_reviewed_probe.py')
 s=s.replace('MOD4_S3_E1_G3_COMMAND_RETENTION_20261010/reports/SOURCE_FREEZE.json','MOD4_S3_E1_G3_COMMAND_RETENTION_SDK_REVIEWED_20261010/reports/SOURCE_FREEZE.json').replace('len(old)==348 and len(f)==348+','len(old)==353 and len(f)==353+')
 old="    assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')"
 assert s.count(old)==1
 extra="""    failed2=Path('/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_SDK_REVIEWED_20261010/reports')
    fs2=read(failed2/'E1_STATE.json');fg2=read(failed2/'E1_GUARDIAN_STARTED.json');fa2=read(failed2/'E1_ATTENTION.json')
    assert fa2['active_segment'] is None and not fa2['own_child_still_alive']
    for locator in (fs2['owner'],fs2['child'],fg2):
        v=identity(locator['pid']);assert not v or v['state']=='Z' or v['start_ticks']!=locator['start_ticks']
"""
 s=s.replace(old,extra+old);ast.parse(s);(P/'supervise_e1_command_retention_assignment_reviewed_once.py').write_text(s,encoding='utf8')
 files={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in P.rglob('*') if p.is_file()};assert len(files)==2
 v=dict(epoch=time.time(),trial_id='E1-G3-COMMAND-RETENTION-ACTUAL-ASSIGNMENT-SELECTOR-REPAIR-01',genuinely_new_command_scope=True,new_file_count=2,sha256=files,source353_byteexact=True,adapter_and_geometry_commands_rewards_unchanged=True,SDK_only_placement_from_actual_generated_plane_supports=True,original353_selector_rejected_before_probe_control=True,original_selector_count_unknown_pending_new_actual_diagnostic=True,CPU_installed_plane_component_true_not_physical_evidence=True,old_CPU14_and_signature_contracts_exactly_reused=True,new_budget_seconds=0)
 (R/'ASSIGNMENT_SELECTOR_PREPARED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(files=2,new_GPU_not_launched=True)))
if __name__=='__main__':main()
