"""Independent CPU review of complete benchmark states and runner timings."""
from pathlib import Path
import json,sys,time,torch,statistics
D=Path(__file__).resolve().parent
def main():
 f=Path(sys.argv[1]);a=json.loads(f.read_bytes());n=a['manifest']['num_envs'];sys.path.insert(0,str(f.parent/'payload'))
 import temporary_state_binding as b
 import expanded_source_projection as ex
 assert not torch.cuda.is_initialized() and b.N==n
 ck=[]
 for row in a['files']:
  p=Path(row['local_actual_path']);assert b.H(p)==row['sha256'];v=torch.load(p,map_location='cpu',weights_only=False);b.validate(v,row['sha256']);ck.append(v)
 parent_path=D.parent/'MOD4_4090_WINDOWS_TEMP20GB_20261013/OWN_PPO_CPU_INPUTS_1791894571823537900/OWN_PPO_SAVED.pt'
 assert b.H(parent_path)==b.PARENT_SHA;parent=torch.load(parent_path,map_location='cpu',weights_only=False)
 pre,post=ck
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):
  assert b.same(parent[key],pre[key]),key
 assert b.floating_count(post)==107 and len(b.perenv_inventory(post))==99
 changed=[k for k,v in post['actor_state_dict'].items() if not b.same(v,pre['actor_state_dict'][k])]
 delta=[float(v['step'])-float(pre['optimizer_state_dict']['state'][k]['step']) for k,v in post['optimizer_state_dict']['state'].items()]
 train=a['stages']['train'];latest=train['output/WINDOWS4090_LATEST_COMPLETE.json'];updates=latest['actual_updates']
 assert updates==4 and latest['actual_controls']==96 and latest['actual_envsteps']==96*n and latest['callbacks']==384
 assert len(changed)==9 and min(delta)==max(delta)==80
 for stage in ('fullrestore','train'):
  st=a['stages'][stage]['output/WINDOWS4090_FULLSTATE_STARTUP_VERIFIED.json'];assert st['passed'] and st['num_envs']==n and st['source_episode_plus_one']
  assert len(st['all12_original_CPUCUDA_restore_markers'])==12
  for row in st['all12_original_CPUCUDA_restore_markers'].values():
   if 'passed' in row:assert row['passed']
  init=a['stages'][stage]['output/LEFT_HEAD_ACTUAL_INIT_VERIFIED.json'];assert init['passed'] and not init['initialization_on_this_attempt'] and not init['metadata']['initializer_repeated_on_this_resume']
 assert train['output/WINDOWS4090_FULLSTATE_STARTUP_VERIFIED.json']['source_SHA']==a['files'][0]['sha256']
 health=train['output/WINDOWS4090_PPO_FORMAL_FINAL_ACTUAL.json']['health'];assert health['control_steps']==96 and health['actual_physics_callbacks']==384 and not health['nonfinite_observed'] and health['stop_reason'] is None
 assert health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact'] and health['integrity_task_reset_events']==health['unknown_task_reset_events']==0
 peak=max(x['EXIT_RECEIPT.json']['peak_RSS_bytes'] for x in a['stages'].values());assert peak<20000000000
 for k in ('native','fullrestore'):assert a['stages'][k]['EXIT_RECEIPT.json']['peak_RSS_bytes']*1.25+536870912<20000000000
 timing=train['output/CAPACITY_ACTUAL_PPO_TIMING.json'];rows=timing['rows'];assert len(rows)==3 and timing['full5epochs4minibatches'] and timing['benchmark_only']
 assert [r['update'] for r in rows]==[1,2,3] and all(r['num_envs']==n and r['steps']==24*n for r in rows)
 seconds=sum(r['collection_seconds']+r['learning_including_save_health_seconds'] for r in rows)
 proof=dict(epoch=time.time(),passed=True,num_envs=n,whole_CPU_no_CUDA=True,floating107_and_perenv99_exact=True,parent128_SHA=b.PARENT_SHA,prePPO_actorcritic_Adam_exact_parent=True,full12CPUCUDA_and_episode_plus_one=True,left_initializer_not_repeated=True,actor_changed=len(changed),Adam_delta=min(delta),actual_updates=updates,actual_envsteps=96*n,peak_physical_resident_bytes=peak,virtual_commit_separate_from_physicalRAM=True,measured_runner_rows=rows,measured_three_updates_envsteps_per_second=72*n/seconds,median_envsteps_per_second=statistics.median(r['envsteps_per_second'] for r in rows),last_two_envsteps_per_second=48*n/sum(r['collection_seconds']+r['learning_including_save_health_seconds'] for r in rows[1:]),load_learn_save_exit_parent_seconds=train['EXIT_RECEIPT.json']['actual_parent_phase_load_learn_save_exit_seconds'],prePPO_production_source=a['files'][0],discarded_benchmark_weights=a['files'][1],no50mm_qualification=True,source_collection=str(f))
 assert not torch.cuda.is_initialized()
 out=D/'reports'/f'CAPACITY{n}_COMPLETE_CPU_TIMING_ACTUAL.json';assert not out.exists();out.write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps({k:proof[k] for k in ('passed','num_envs','peak_physical_resident_bytes','measured_three_updates_envsteps_per_second','median_envsteps_per_second','last_two_envsteps_per_second','load_learn_save_exit_parent_seconds')}))
if __name__=='__main__':main()
