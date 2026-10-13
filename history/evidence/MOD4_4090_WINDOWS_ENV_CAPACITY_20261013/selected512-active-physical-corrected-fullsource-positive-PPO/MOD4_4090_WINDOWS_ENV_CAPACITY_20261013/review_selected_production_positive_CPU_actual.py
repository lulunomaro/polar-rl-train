from pathlib import Path
import torch,json,sys,time
D=Path(__file__).resolve().parent
def main():
 f=Path(sys.argv[1]);a=json.loads(f.read_bytes());sys.path.insert(0,str(f.parent/'payload'));import temporary_state_binding as b
 assert not torch.cuda.is_initialized() and b.N==512
 states=[]
 for row in a['files']:
  p=Path(row['local_actual_path']);assert b.H(p)==row['sha256'];c=torch.load(p,map_location='cpu',weights_only=False);b.validate(c,row['sha256']);states.append(c)
 src,own=states;latest=a['latest'];u=latest['actual_updates'];assert u>0 and latest['actual_controls']==24*u and latest['actual_envsteps']==512*24*u and latest['callbacks']==4*24*u
 changed=[k for k,v in own['actor_state_dict'].items() if not b.same(v,src['actor_state_dict'][k])];delta=[float(v['step'])-float(src['optimizer_state_dict']['state'][k]['step']) for k,v in own['optimizer_state_dict']['state'].items()];assert len(changed)==9 and min(delta)==max(delta)==20*u
 startup=a['startup'];assert startup['passed'] and startup['num_envs']==512 and startup['source_episode_plus_one'] and startup['source_SHA']==a['files'][0]['sha256'] and len(startup['all12_original_CPUCUDA_restore_markers'])==12
 for row in startup['all12_original_CPUCUDA_restore_markers'].values():
  assert row['pid']==latest['pid']
  if 'passed' in row:assert row['passed']
 assert a['left']['passed'] and not a['left']['initialization_on_this_attempt'] and not a['left']['metadata']['initializer_repeated_on_this_resume']
 assert b.same(src['WINDOWS4090_EXPANDED_ENV_BRANCH'],own['WINDOWS4090_EXPANDED_ENV_BRANCH']) and b.floating_count(own)==107 and len(b.perenv_inventory(own))==99
 mf=a['manifest'];proof=mf['target_CPU_receipt'];ad=__import__('json').loads((D/'reports/CAPACITY_SELECTED_MEASURED_DECISION_ACTUAL.json').read_bytes());assert mf['source']['sha256']==ad['production_prePPO_source']['sha256'] and not mf['capacity_benchmark_only'] and not mf['production_weights_discarded'] and mf['max_formal_updates']==256
 stdout=a['whole_current_stdout'];p=Path(stdout['actual_local_path']);raw=p.read_bytes();assert b.H(p)==stdout['sha256'] and len(raw)==stdout['bytes'] and not any(x in raw for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'PhysX error:'))
 assert a['guardian']['peak_RSS_bytes']<20000000000 and not torch.cuda.is_initialized()
 result=dict(epoch=time.time(),passed=True,actual_512_production_PPO_saved=True,source_scope=a['scope'],own_fullsave=a['files'][1],valid_prePPO_source=a['files'][0],float107=True,perenv99=True,actual_updates=u,actual_controls=24*u,actual_envsteps=512*24*u,actual_callbacks=4*24*u,actor_changed=len(changed),Adam_stepdelta=min(delta),full12_CPUCUDA_disk_sourceepisode_plus_one=True,left_initializer_not_repeated=True,source_metadata_fullsame_exact=True,whole_current_stdout_no_PhysX_errors=True,peak_physical_resident_bytes=a['guardian']['peak_RSS_bytes'],source_collection=str(f),activity_not_final_or50mm_pass=True)
 out=D/'reports'/f'SELECTED512_OWN_POSITIVE_PPO_CPU_ACTUAL_{time.time_ns()}.json';out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps({k:result[k] for k in ('passed','actual_updates','actual_envsteps','actor_changed','Adam_stepdelta','peak_physical_resident_bytes')}));print(str(out))
if __name__=='__main__':main()
