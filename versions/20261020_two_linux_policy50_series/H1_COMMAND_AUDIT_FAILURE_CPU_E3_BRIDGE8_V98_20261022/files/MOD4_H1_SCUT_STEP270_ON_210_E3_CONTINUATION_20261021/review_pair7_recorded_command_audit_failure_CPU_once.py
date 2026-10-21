from pathlib import Path
import hashlib,json,time,traceback,torch
T=Path(__file__).resolve().parent;N=T/'H1_STEP270_E3_PAIR_V7_20261022';R=T/'reports';read=lambda p:json.loads(Path(p).read_bytes())
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
    proof=read(R/'V98_H1_FAILED_PREFIX_AND_ACTUAL_COMMAND_SDK_SOURCE_RETURNED_ACTUAL.json');p=proof['prefix'];assert p['twohost_complete_SHA'] and p['failed_partial_prefix']
    torch.set_num_threads(2);s=torch.load(p['local_path'],map_location='cpu',weights_only=False);phase=s['H1_step270_task_state']['phase'];command=s['H1_step270_task_state']['external_command']['vel_command_b'];age=phase['tensors']['age_control'];req=(age>=100)&(age<180)
    expected=torch.zeros_like(command);expected[:,0]=req.to(command.dtype)*.8
    assert phase['num_envs']==20000 and command.shape==(20000,3) and torch.isfinite(command).all()
    bad=torch.nonzero((command!=expected).any(-1)).flatten();old_zero=bool(torch.equal(command,torch.zeros_like(command)))
    trace=read(N/'current_pair_closed_text/h1/job0/production/control_prefix_raw/ACTUAL_STEP_ORIGINAL_ERROR.json')
    error=read(N/'current_pair_closed_text/h1/job0/production/LEARN_ORIGINAL_ERROR_BEFORE_SAVE.json')
    runtime=N/'current_pair_closed_text/h1/h1_step270_sdk_runtime_candidate.py';old=N/'current_pair_closed_text/h1/job0/runtime/isaac/mod4/h1_external_operator_command_v1.py';mod4=N/'current_pair_closed_text/h1/job0/runtime/isaac/mod4/mod4_env.py'
    assert "cmd.vel_command_b[:,0]=self.h1_phase.public_request().float()*.8" in runtime.read_text('utf8')
    assert "torch.equal(term.command,torch.zeros_like(term.command))" in old.read_text('utf8') and 'self.common_step_counter % 2400 == 1' in mod4.read_text('utf8')
    v=dict(epoch=time.time(),failed_prefix_producer=p,diagnostic_only_not_a_production_source=True,complete_updates_before_exception=error['complete_updates'],complete_control_rows=trace['completed_control_rows'],failing_periodic_audit_control=trace['completed_control_rows']+1,recorded_command_shape=list(command.shape),recorded_finite=True,nonzero_command_envs=int((command!=0).any(-1).sum()),public_request_envs=int(req.sum()),unique_actual_vx=[float(x) for x in torch.unique(command[:,0])],vy_wz_all_zero=bool((command[:,1:]==0).all()),original_zero_audit_would_pass=old_zero,recorded_command_exactly_matches_already_installed_step270_publisher=len(bad)==0,mismatch_count=len(bad),mismatch_first32=bad[:32].tolist(),actual_current_task_requests_forward_point8_while_legacy_audit_requires_zero=True,periodic_audit_only_at1_then2401_explains_short_native_scope=True,actual_error=error,actual_trace_error=trace,source_SHA={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (runtime,old,mod4)},no_command_input_or_physics_or_reward_change_made=True,no_GPU_or_native_or_raw_replay=True)
    put('V98_H1_RECORDED_STEP270_COMMAND_VERSUS_LEGACY_ZERO_AUDIT_CPU_ACTUAL.json',v)
    assert len(bad)==0 and not old_zero,'Recorded command differs from the already installed authorized publisher; do not infer a harmless audit mismatch'
    assert not torch.cuda.is_initialized()
    print(json.dumps(dict(recorded_exact_point8_publisher=True,legacy_zero_audit_rejects=True,request_envs=v['public_request_envs'],control=v['failing_periodic_audit_control'],failed_prefix_not_qualified=True)))
except BaseException:
    put('V98_H1_RECORDED_COMMAND_CPU_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_replay_or_source_admission=True));raise
