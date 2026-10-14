"""Preserve V2 NaN rejection; repair only the zero-control health/save ordering."""
from pathlib import Path
import json,ast,time,hashlib,copy
from s4_zero_control_state_integrity_v1 import verify_zero_control_restore
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def one(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def save(name,s):
    ast.parse(s);p=D/name;assert not p.exists();p.write_text(s,encoding='utf8');return dict(path=str(p),sha256=sha(p))
def main():
    old=json.loads(sorted((D/'reports').glob('S4_ZERO_HEALTH0_ORIGINAL_CLOSED_ACTUAL_*.json'))[-1].read_bytes())
    h=json.loads(next(v['text'] for v in old['files'] if v['path'].endswith('/CLOCK_TRAINING_HEALTH.json')))
    assert h['control_steps']==0 and h['actual_physics_callbacks']==0
    result=verify_zero_control_restore(h,True,0.0);assert result['perstep_closure_mimic_not_observed'] is True
    bad=0
    for name,value in (('version',2),('control_steps',1),('actual_physics_callbacks',4),('expected_physics_callbacks',4),('integrity_task_reset_events',1),('unknown_task_reset_events',1),('nonfinite_observed',True),('stop_reason','fault'),('termination_reason_coverage_exact',False)):
        v=copy.deepcopy(h);v[name]=value
        try:verify_zero_control_restore(v,True,0.)
        except AssertionError:bad+=1
        else:raise AssertionError('Bad zero-control health accepted '+name)
    for finite,qerr in ((False,0.),(True,1e-6),(True,float('nan'))):
        try:verify_zero_control_restore(h,finite,qerr)
        except AssertionError:bad+=1
        else:raise AssertionError('Bad live zero state accepted')
    worker=(D/'s4_linux20k_missing_zero_fullsave_worker_v2.py').read_text()
    worker=worker.replace('own_first_fullsave0_loggerfix','own_first_fullsave0_healthschema').replace('own_fullrestore0_loggerfix','own_fullrestore0_healthschema')
    oldblock="""        health.write();value=json.loads((folder/'CLOCK_TRAINING_HEALTH.json').read_bytes())
        assert learning_health_pass(value) and value['stop_reason'] is None
        assert value['control_steps']==controls and value['actual_physics_callbacks']==controls*4
        out=folder/'S4_OWN_INTEGRATION_FULLSAVE.pt';runner.save(str(out))"""
    newblock="""        # Save the complete live state before post-save reader assertions.
        out=folder/'S4_OWN_INTEGRATION_FULLSAVE.pt';runner.save(str(out))
        health.write();value=json.loads((folder/'CLOCK_TRAINING_HEALTH.json').read_bytes())
        assert controls==0 and value['control_steps']==0 and value['actual_physics_callbacks']==0
        from s4_zero_control_state_integrity_v1 import verify_zero_control_restore
        def tensor(v):return v.torch if hasattr(v,'torch') else v
        robot=env.scene['robot']
        finite=all(bool(torch.isfinite(tensor(v)).all()) for v in (robot.data.root_state_w,robot.data.joint_pos,robot.data.joint_vel))
        qerror=float((tensor(robot.data.joint_pos)-env._rescue_reset_q).abs().max())
        zero=verify_zero_control_restore(value,finite,qerror)
        (folder/'S4_ZERO_CONTROL_STATE_INTEGRITY_ACTUAL.json').write_text(json.dumps(zero,indent=2))"""
    worker=one(worker,oldblock,newblock)
    rows=[save('s4_linux20k_missing_zero_fullsave_worker_v3.py',worker)]
    parent=(D/'s4_missing_zero_fullsave_parent_v2.py').read_text().replace('own_first_fullsave0_loggerfix','own_first_fullsave0_healthschema').replace('own_fullrestore0_loggerfix','own_fullrestore0_healthschema').replace('s4_linux20k_missing_zero_fullsave_worker_v2.py','s4_linux20k_missing_zero_fullsave_worker_v3.py')
    rows.append(save('s4_missing_zero_fullsave_parent_v3.py',parent))
    material=(D/'materialize_s4_zero_fullsave_target_CPU_v2.py').read_text().replace('s4_missing_zero_fullsave_parent_v2','s4_missing_zero_fullsave_parent_v3')
    rows.append(save('materialize_s4_zero_fullsave_target_CPU_v3.py',material))
    publish=(D/'publish_s4_zero_fullsave_target_CPU_once_v2.py').read_text().replace('MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_LOGGER_V2_20261015','MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_HEALTH_V3_20261015').replace('MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_UPLOAD_V2_20261015','MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_UPLOAD_V3_20261015')
    publish=publish.replace('s4_linux20k_missing_zero_fullsave_worker_v2.py','s4_linux20k_missing_zero_fullsave_worker_v3.py').replace('s4_missing_zero_fullsave_parent_v2.py','s4_missing_zero_fullsave_parent_v3.py').replace('materialize_s4_zero_fullsave_target_CPU_v2.py','materialize_s4_zero_fullsave_target_CPU_v3.py').replace('zero_fullsave_logger_payload_v2','zero_fullsave_health_payload_v3').replace('S4_ZERO_FULLSAVE_LOGGER_V2','S4_ZERO_FULLSAVE_HEALTH_V3')
    publish=one(publish,"files=[D/name for name in (", "files=[D/'s4_zero_control_state_integrity_v1.py']+[D/name for name in (")
    rows.append(save('publish_s4_zero_fullsave_target_CPU_once_v3.py',publish))
    dispatch=(D/'continue_unexecuted_zero_fullsave_dispatch_import_v3.py').read_text().replace('S4_ZERO_FULLSAVE_LOGGER_V2','S4_ZERO_FULLSAVE_HEALTH_V3').replace('s4_missing_zero_fullsave_parent_v2','s4_missing_zero_fullsave_parent_v3').replace('own_first_fullsave0_loggerfix','own_first_fullsave0_healthschema').replace('own_fullrestore0_loggerfix','own_fullrestore0_healthschema')
    rows.append(save('dispatch_s4_missing_zero_fullsave_fixed_two_once_v3.py',dispatch))
    assert bad==12
    p=D/'reports/S4_ZERO_CONTROL_UNOBSERVED_HEALTH_SCHEMA_V3_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed_CPU=True,original_health0_NaN_and_false_preserved=True,not_physics_failure=True,
        actual_controls=0,live_current_buffers_and_q30_checks_required=True,negative_cases=bad,new_sources=rows,
        new_requested_controls=[0,0],no_native120_replay=True,positive_control_thresholds_unchanged=True,
        complete_live_save_precedes_later_reader_assertions=True,future_GPU_pass_not_inferred=True),indent=2))
    print(json.dumps(dict(passed=True,report=str(p),negative_cases=bad,new_zero_control_sources=len(rows))))
if __name__=='__main__':main()
