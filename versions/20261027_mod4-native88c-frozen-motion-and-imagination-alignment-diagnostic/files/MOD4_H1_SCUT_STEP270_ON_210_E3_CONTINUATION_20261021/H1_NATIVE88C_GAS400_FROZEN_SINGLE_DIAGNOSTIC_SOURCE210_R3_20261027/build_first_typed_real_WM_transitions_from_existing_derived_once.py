"""Small real-transition adapter proof, from derived arrays; no original raw read."""
from pathlib import Path
import numpy as np
import json,hashlib,time,traceback
S=Path(__file__).resolve().parent;R=S/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 put('NEW_REAL61_WM_DATASET_ADAPTER_PURPOSE_CONSUMED_ACTUAL.json',dict(epoch=time.time(),user_requested_own_historical_expert_data_for_WM=True,source='already derived native88C single N1 fixed frozen attempt',no_raw_checkpoint_GPU_or_model_forward=True))
 p=S/'NEW88C_SINGLE_RECORDED_DERIVED_SMALL.npz'
 with np.load(p,allow_pickle=False) as d:
  state=d['packed127'];terminal=d['terminal127'];xi=d['xi31'];raw=d['raw6'];executed=d['executed'];applied=d['physical_applied'];times=d['time']
 assert state.shape==terminal.shape==(61,127) and xi.shape==(61,31) and raw.shape==(61,6)
 for value in (state,terminal,xi,raw,executed,applied):assert np.isfinite(value).all()
 action=executed[4::4].copy();clipped=np.clip(raw,-6,6)
 assert action.shape==(61,6) and np.array_equal(action,clipped),'Recorded ingress must match clip6 of actual stored native command'
 executed_blocks=executed[1:].reshape(61,4,6)
 assert np.array_equal(executed_blocks,np.broadcast_to(action[:,None,:],executed_blocks.shape))
 physical=applied[1:].reshape(61,4,6).copy()
 assert len(times)==245 and np.allclose(np.diff(times),.0025,atol=1e-7)
 done=np.zeros(61,dtype=bool);done[-1]=True
 # Preserve any pack boundary difference as metadata; no arbitrary continuity gate.
 gap=np.abs(terminal[:-1]-state[1:]);not_equal_columns=np.where(np.any(gap!=0,axis=0))[0]
 output=S/'REAL61_H1_GAS400_TYPED_WM_ADAPTER_PROOF.npz';assert not output.exists()
 np.savez_compressed(output,state127=state,next_terminal127=terminal,xi31=xi,
     ingress_executed6=action,applied_action_4x6=physical,done=done,
     terminal_bad_orientation=done.copy(),episode_id=np.zeros(61,dtype=np.int32),
     transition_control_index=np.arange(61),control_dt_s=np.asarray(.01),physics_dt_s=np.asarray(.0025))
 report=dict(epoch=time.time(),passed_dataset_adapter_only=True,transitions=61,episodes=1,
  native_source_SHA='a9bf6dca376e9d570ef0a6e2c15604f38656c4ebfedaa829a34830ee57c73aaf',
  state_schema='native127_history_not_reconstructed_here',xi_schema='existing_recorded_xi31',
  backend='IsaacLab6.1.14_PhysX_2p5ms_TGS32_4',control_Hz=100,nominal_gas_each_N=400,
  nominal_spring_k_N_per_m=2000,source_physical_recipe='actual88C',
  action_ingress_exact_recorded_clip6=True,all_four_physical_applied_actions_preserved=True,
  no_reset_crossing=True,terminal_transition_retained=True,
  next_pack_boundary_max_abs_difference=float(gap.max()),different_boundary_pack_columns=not_equal_columns.tolist(),
  all_samples_are_one_failed_prejump_episode=True,no_successful_jump_data=True,
  not_a_full_historical_dataset_or_WM_training=True,
  historical_700N_400N_50Hz_100Hz_backend_domains_must_remain_explicit=True,
  history_and_queue_alignment_required_before_current_WM_sampler_admission=True,
  derived_input_path=str(p),output=dict(path=str(output),bytes=output.stat().st_size,SHA=hashlib.sha256(output.read_bytes()).hexdigest()))
 put('REAL61_WM_DATASET_ADAPTER_PROOF_ACTUAL.json',report)
 print(json.dumps(report))
if __name__=='__main__':
 try:main()
 except BaseException:put('REAL61_WM_DATASET_ADAPTER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),source_not_retried=True));raise
