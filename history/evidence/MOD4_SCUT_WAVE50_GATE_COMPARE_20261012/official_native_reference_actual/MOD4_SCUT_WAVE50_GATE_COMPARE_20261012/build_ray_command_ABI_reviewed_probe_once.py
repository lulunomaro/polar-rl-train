"""Preserve initial full traces; admit the actually missing rough-sensor/command ABI."""
from scut_wave_io import *

def main():
    source=D/'scut_wave50_placement_reviewed_probe.py';s=source.read_text(encoding='utf8');before=s
    old="if path in ['/robot_cfg/init_state/rot','/dot_scanner/offset/rot']:";new="if path=='/robot_cfg/init_state/rot' or path.endswith('/offset/rot'):";assert s.count(old)==1;s=s.replace(old,new)
    s=s.replace("O=D/'original'","O=Path('D:/MOD4_async_eval/scut_wave50_gate_compare_detached_reviewed_20261012/original')")
    s=s.replace("D/'actual_mod4_wave50_query.npz'","Path('D:/MOD4_async_eval/scut_wave50_gate_compare_detached_reviewed_20261012/actual_mod4_wave50_query.npz')")
    anchor="  env.command_generator.command[:]=0.;env.command_generator.command[:,0]=targets";assert s.count(anchor)==1
    s=s.replace(anchor,"  if hasattr(env.command_generator,'special_mode_id'):env.command_generator.special_mode_id[:]=-1\n"+anchor)
    anchor="  manual();resets.append(dict(control=int(control),envs=ids.cpu().tolist()))";assert s.count(anchor)==1
    s=s.replace(anchor,"  env._record_reset_heading_target(ids);env._sync_heading_command_target_to_reset_heading(ids)\n"+anchor)
    anchor=" assert obs['policy'].shape==(80,35)";assert s.count(anchor)==1
    s=s.replace(anchor," assert obs['policy'].shape==(80,35)")
    anchor=" # Verify the collider's actual authored triangles, then query it independently.";assert s.count(anchor)==1
    proof=""" # This new scope requires the actual original height sensor to point down.
 scanner_receipts={}
 for name in ('height_scanner','right_wheel_height_scanner','left_wheel_height_scanner'):
  sensor=getattr(env,name,None)
  if sensor is None:continue
  dirs=torch_view(sensor.ray_directions);hit=torch_view(sensor.data.ray_hits_w)
  assert torch.all(dirs[...,2]<-.999999) and torch.isfinite(hit).all(), ('original_SCUT_sensor_direction_hit',name)
  scanner_receipts[name]=dict(local_direction=dirs.cpu().tolist(),initial_hit=hit.cpu().tolist(),config_offset=list(sensor.cfg.offset.rot),all_downward_and_all_hits_finite=True)
 (output.parent/'ORIGINAL_HEIGHT_SENSOR_GPU_ABI_VERIFIED.json').write_text(json.dumps(scanner_receipts,indent=2),encoding='utf8')
"""
    s=s.replace(anchor,proof+anchor)
    anchor="rows={k:[] for k in ('before_root','root','q','body_link_pos','command','action','episode','terminated','truncated','original_terminated','original_truncated','route_boundary','joint_vel','applied_torque')}";assert s.count(anchor)==1
    s=s.replace(anchor,anchor[:-2]+",'obs_policy','special_mode_ids')}")
    anchor="  with torch.inference_mode():action=model(obs['policy'])";assert s.count(anchor)==1
    s=s.replace(anchor,"  expected_command=env._scale_obs_component('command',env._clip_obs_component('command',env.command))\n  assert torch.allclose(obs['policy'][:,:3],expected_command,atol=1e-6,rtol=0), 'Original actor must receive requested scaled BODY command'\n  actual_obs=obs['policy'].cpu().numpy().copy();mode_ids=env.command_generator.special_mode_id.cpu().numpy().copy();assert np.all(mode_ids==-1)\n"+anchor)
    anchor="values=dict(before_root=before,command=requested,action=action.cpu().numpy(),episode=episodes.copy(),**current)";assert s.count(anchor)==1
    s=s.replace(anchor,"values=dict(before_root=before,command=requested,action=action.cpu().numpy(),episode=episodes.copy(),obs_policy=actual_obs,special_mode_ids=mode_ids,**current)")
    anchor="original_SCUT_termination_duration_and_plant_DR_kept=True,";assert s.count(anchor)==1;s=s.replace(anchor,anchor+"original_height_sensor_GPU_ABI_verified=scanner_receipts,actual_actor_command_obs_and_no_special_modes_verified=True,old_first_scope_ineligible_due_unconverted_rough_sensor_quaternion=True,legacy_any_substep_shadow_is_diagnostic_not_exact_control_gate=True,")
    compile(s,'scut_wave50_ray_command_ABI_reviewed_probe.py','exec');out=D/'scut_wave50_ray_command_ABI_reviewed_probe.py';assert not out.exists();out.write_text(s,encoding='utf8')
    save('RAY_COMMAND_ABI_REVIEWED_PROBE_PREPARED.json',dict(epoch=time.time(),passed=True,original_probe=dict(path=str(source),bytes=len(before.encode()),sha256=H(before.encode())),new_probe=dict(path=str(out),bytes=out.stat().st_size,sha256=H(out.read_bytes())),new_missing_scope='All original raycaster offset quaternions adapted wxyz->xyzw; actual down-rays/hits, actual actor scaled BODY-command observations and neutral special-mode IDs validated before/through control',original_model_USD_clock_solver_DR_dones_and_15s_route_unchanged=True,initial_two_fullraw_results_preserved_not_relabelled=True,no_old_GPU_scope_replayed=True,new_GPU_pending=True))
    print(json.dumps(dict(prepared=True,path=str(out),AST_passed=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('RAY_COMMAND_ABI_BUILD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),pre_GPU=True));raise
