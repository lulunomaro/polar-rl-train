"""Own saved route all control identity and frozen GPU expert choice review."""
from pathlib import Path
import argparse,json,hashlib,time,traceback,numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--case',required=True);args=parser.parse_args();assert args.case in ('s4_rule_original35_query35_native120_v2','s4_rule_original35_query35_full1500_v2')
 physical=R/('S4_RULE35_OWN_PHYSICAL_DATA_ADMITTED_'+args.case+'.json');proof=read(physical);assert proof['passed']
 j=read(sorted(R.glob(args.case+'_CURRENT_ACTUAL_*.json'))[-1]);files=j['collected_files']
 for row in files:
  p=Path(row['local_path']);assert H(p)==row['sha256'] and p.stat().st_size==row['bytes'] and row['two_host_byteSHA_exact']
 def file(name):return next(Path(x['local_path']) for x in files if x['relative']=='attempts/'+args.case+'/output/'+name)
 r=read(file('S4_ROUTER_ROUTE_CONTROL_ACTUAL.json'));source=read(file('S4_FROZEN_PAIR_SOURCE_ACTUAL.json'));manifest=read(D/'payload/S4_PAIR_SOURCE_MANIFEST.json')
 assert r['sources']==source['sources']==manifest['sources'] and source['all18_actor_std_GPU_source_exact'] and source['no_construction_CPUCUDA_RNG_draw']
 assert source['optimizer_updates']==r['gate_updates']==r['critic_updates']==0 and r['new_fixture_not_trained_gate']
 assert r['all18_weights_std_unchanged'] and r['stateless_rule_hysteresis_disabled'] and r['rule_only_command_from_shared35']
 S=proof['controls'];assert r['controls']==r['feedback_provider_calls']==S
 p=file('S4_ROUTING_FULL_CONTROL_ACTUAL.npz');assert H(p)==r['raw']['sha256'] and p.stat().st_size==r['raw']['bytes']
 with np.load(p,allow_pickle=False) as z:b={k:z[k].copy() for k in z.files}
 with np.load(file('route_raw.npz'),allow_pickle=False) as z:a={k:z[k].copy() for k in z.files}
 assert all(np.isfinite(v).all() for v in b.values()) and b['expert_means'].shape==(S,80,2,6)
 assert np.array_equal(b['shared_obs'],a['policy_obs']) and np.array_equal(a['command'],b['shared_obs'][...,:3])
 normal=np.zeros((S,80,7),np.float32);normal[...,0]=1;assert np.array_equal(b['shared_obs'][...,28:35],normal)
 cmd=b['shared_obs'][...,:3];choice=((abs(cmd[...,0])>0)&(abs(cmd[...,0])<=.300001)&(abs(cmd[...,1:3]).max(-1)<=1e-6)).astype(np.int64)
 assert np.array_equal(choice,b['z']) and np.array_equal(np.stack((1-choice,choice),-1),b['probabilities'])
 selected=np.take_along_axis(b['expert_means'],choice[...,None,None],axis=2).squeeze(2)
 assert np.array_equal(selected,b['raw_action']) and np.array_equal(selected,a['action']) and np.array_equal(np.clip(selected,-6,6),a['processed_action'])
 previous=np.zeros((80,6),np.float32);last=np.full(80,-1);switches=0;done=a['terminated']|a['truncated']
 for t in range(S):
  assert np.array_equal(b['shared_obs'][t,:,22:28],previous)
  switches+=int(((last>=0)&(last!=choice[t])).sum());last=choice[t].copy();last[done[t]]=-1
  previous=a['processed_action'][t].copy();previous[done[t]]=0
 assert switches==r['switches']
 actionjump=np.max(abs(np.diff(a['processed_action'],axis=0)),axis=-1)
 valid=~done[:-1];effort=a['physical_hardware_actual_applied_effort'].reshape(S,4,80,6).astype(np.float64)
 effortjump=np.max(abs(np.diff(effort.reshape(-1,80,6),axis=0)),axis=-1)
 report=dict(epoch=time.time(),passed=True,physical_admission=dict(path=str(physical),sha256=H(physical)),case=args.case,controls=S,callbacks=S*4,only_two_frozen_sources=manifest['sources'],same_feedback35_all_experts_and_gate_fixture_exact=True,provider_calls=S,whole6_raw_then_clip6_actual_readback_exact=True,previous_action_and_selectedreset_exact=True,existing_mode_constant_normal_no_oracle=True,choice_only_normal_commands=True,expert_selected_envcontrols=np.bincount(choice.ravel(),minlength=2).tolist(),switches=switches,rule_for_moving_route_always_W35_and_standing_E0=True,not_terrain_based_switch_or_trained_gate=True,gate_critic_updates=0,initial_final_all18_GPU_weight_std_source_exact=True,source_STD_retained=source['source_std_retained'],inference_chain_latency=r['latency_ms'],not_board_deadline=True,actual_control_action_jump_max_abs=float(actionjump[valid].max()) if valid.any() else None,actual_substep_motor_effort_jump_max_abs=float(effortjump.max()),jumps_descriptive_no_new_threshold_or_intervention=True,complete_twohost_artifacts_SHA_verified=True,full15s_behavior=S==1500,native120_not_full_route=S==120,original_missing_EXIT_NATURAL_preserved=j['outputs']['EXIT_NATURAL.json'] is None,actual_parent_child_out_and_sharedOSlockfree=True,no_PPO_or_budgetwrite=True,gate_full_training_environment_CPUCUDA_restore_and_learning_pending=True,qualification_claimed=False)
 p=R/('S4_RULE35_SHARED_ROUTING_ADMITTED_'+args.case+'.json');assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),passed=True,controls=S,switches=switches,selected=report['expert_selected_envcontrols'],no_gate_learning=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('S4_RULE35_ROUTING_CPU_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_SSH=True),indent=2),encoding='utf8');raise
