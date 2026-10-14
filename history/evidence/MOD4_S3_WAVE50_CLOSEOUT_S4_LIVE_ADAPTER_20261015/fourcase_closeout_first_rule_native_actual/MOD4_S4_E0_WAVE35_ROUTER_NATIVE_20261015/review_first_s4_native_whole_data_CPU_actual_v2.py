"""Independent own native data + shared-input routing review; never connects."""
from pathlib import Path
import os,sys,json,time,hashlib,importlib.util,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
import torch
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def main():
 case='s4_rule_pair_flat80_native120_v1'
 reports=sorted(R.glob(case+'_CURRENT_ACTUAL_*.json'));assert reports
 receipt=read(reports[-1]);boundary=read(R/(case+'_INDEPENDENT_BOUNDARY.json'))
 assert receipt['collected_files'] and all(r['two_host_byteSHA_exact'] for r in receipt['collected_files'])
 for row in receipt['collected_files']:
  p=Path(row['local_path']);assert p.stat().st_size==row['bytes'] and H(p)==row['sha256']
 probe_rows=[r for r in receipt['collected_files'] if r['relative']=='attempts/'+case+'/output/probe.json'];assert len(probe_rows)==1
 attempt=Path(probe_rows[0]['local_path']).parent.parent;O=attempt/'output'
 original=W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014/review_retention_full_actual_CPU_v8.py'
 spec=importlib.util.spec_from_file_location('original_v8_physical_reader',original)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 original_read=m.read;old_manifest=m.D/'payload/RETENTION_CPU_MANIFEST_V8.json'
 own_manifest=D/'payload_v2/RETENTION_CPU_MANIFEST_V8.json'
 m.read=lambda p: read(own_manifest) if Path(p)==old_manifest else original_read(p)
 physical=m.audit_case(attempt,boundary)
 assert physical['steps']==120 and physical['num_envs']==80 and not physical['full_behavior_review']
 source=read(O/'S4_FROZEN_PAIR_SOURCE_ACTUAL.json');routing=read(O/'S4_ROUTER_NATIVE_CONTROL_ACTUAL.json')
 manifest=read(D/'payload_v2/S4_PAIR_SOURCE_MANIFEST.json')
 assert source['optimizer_updates']==routing['gate_optimizer_updates']==routing['critic_optimizer_updates']==0
 assert source['all18_actor_weight_and_std_GPU_tensors_source_exact'] and source['no_CPU_or_CUDA_rng_draw_from_pair_construction']
 assert source['new_gate_and_E0_initialized_critic_fixture_constructed_but_unused_for_rule_selection']
 assert routing['source_all18_weights_std_unchanged'] and routing['rule_is_not_trained_gate']
 assert routing['optional_hysteresis_disabled_for_first_stateless_native']
 assert routing['sources']==manifest['sources'] and routing['source_pair_manifest_SHA']==H(D/'payload_v2/S4_PAIR_SOURCE_MANIFEST.json')
 assert routing['controls']==routing['feedback_provider_calls']==120
 router_raw=O/'S4_ROUTING_FULL_CONTROL_ACTUAL.npz'
 assert H(router_raw)==routing['router_raw']['sha256'] and router_raw.stat().st_size==routing['router_raw']['bytes']
 with np.load(router_raw,allow_pickle=False) as z:b={k:z[k].copy() for k in z.files}
 c=read(O/'COMPLETE_ACTUAL.json');raw=O/Path(c['raw']['path']).name
 with np.load(raw,allow_pickle=False) as z:a={k:z[k].copy() for k in z.files}
 assert b['shared_obs'].shape==(120,80,35) and b['expert_means'].shape==(120,80,2,6)
 assert all(np.isfinite(v).all() for v in b.values())
 assert np.array_equal(b['shared_obs'],a['policy_obs'])
 normal=np.zeros((120,80,7),np.float32);normal[...,0]=1
 assert np.array_equal(b['shared_obs'][...,28:35],normal)
 cmd=b['shared_obs'][...,:3]
 choice=((np.abs(cmd[...,0])>0)&(np.abs(cmd[...,0])<=.300001)&(np.max(np.abs(cmd[...,1:3]),axis=-1)<=1e-6)).astype(np.int64)
 assert np.array_equal(choice,b['z'])
 probabilities=np.stack((1-choice,choice),axis=-1).astype(np.float32)
 assert np.array_equal(probabilities,b['probabilities'])
 selected=np.take_along_axis(b['expert_means'],choice[...,None,None],axis=2).squeeze(2)
 assert np.array_equal(selected,b['raw_action']) and np.array_equal(selected,a['raw_actor_action'])
 assert np.array_equal(np.clip(selected,-6,6),b['clipped_action']) and np.array_equal(b['clipped_action'],a['processed_action'])
 done=a['terminated']|a['truncated'];previous=np.zeros((80,6),np.float32);switches=0;last_choice=np.full(80,-1)
 for t in range(120):
  assert np.array_equal(b['shared_obs'][t,:,22:28],previous)
  switches+=int(((last_choice>=0)&(last_choice!=choice[t])).sum())
  previous=a['processed_action'][t].copy();previous[done[t]]=0
  last_choice=choice[t].copy();last_choice[done[t]]=-1
 assert switches==routing['switches']
 sys.path.insert(0,str(W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014'))
 from hard_top1_frozen_expert_CPU_component_v1 import FrozenMean35
 errors=[];before=torch.get_rng_state().clone()
 for i,row in enumerate(manifest['sources']):
  p=D/'payload_v2/source'/Path(row['local_path']).name
  assert H(p)==row['sha256'] and p.stat().st_size==row['bytes']
  ck=torch.load(p,map_location='cpu',weights_only=False)
  assert ck['actor_state_dict']['distribution.std_param'].tolist()==source['source_std_scalar_retained'][i]
  model=FrozenMean35(ck['actor_state_dict'])
  with torch.inference_mode():out=model(torch.from_numpy(b['shared_obs'].reshape(-1,35))).numpy().reshape(120,80,6)
  errors.append(float(np.max(abs(out-b['expert_means'][:,:,i]))))
 assert torch.equal(before,torch.get_rng_state()) and not torch.cuda.is_initialized()
 # GPU raw selection is byte exact above. Cross-device arithmetic is reported separately.
 report=dict(epoch=time.time(),passed=True,scope='first stateless source-bound E0+WAVE35 rule native flat80/120',physical=physical,own_sources=manifest['sources'],controls=120,callbacks=480,provider_calls=120,whole6_action_selected_exact=True,shared35_actual_feedback_exact=True,previous_actual_clipped_control_and_selected_reset_exact=True,existing_mode_constant_normal=True,choice_depends_only_on_commands=True,actual_switches=switches,per_expert_selected_controls=np.bincount(choice.ravel(),minlength=2).tolist(),CPU_vs_actual_GPU_mean_maxabs=errors,CPU_GPU_bitexact_not_claimed=True,original_std_retained=True,gate_and_critic_fixture_present_untrained_unused_for_rule=True,optimizer_updates=0,global_CPU_RNG_unchanged=True,no_CUDA_or_PPO=True,latency=routing['inference_chain_latency_ms'],own_all_artifacts_twohost_SHA_verified=True,source_reader_reuse=dict(path=str(original),sha256=H(original),own_source_manifest_binding=str(own_manifest)),boundary=boundary,missing_EXIT_NATURAL_preserved=True,full35_transition_route_and_production_gate_fullsave_still_pending=True,gate_learning_not_admitted=True,qualification_not_claimed=True)
 output=R/'FIRST_S4_OWN_NATIVE120_WHOLE_PHYSICAL_AND_ROUTER_CPU_ADMITTED.json';assert not output.exists();output.write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(output=str(output),passed=True,controls=120,callbacks=480,switches=switches,selected_controls=report['per_expert_selected_controls'],CPU_GPU_maxabs=errors,no_gate_training=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('FIRST_S4_NATIVE_CPU_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_or_SSH=True),indent=2),encoding='utf8');raise
