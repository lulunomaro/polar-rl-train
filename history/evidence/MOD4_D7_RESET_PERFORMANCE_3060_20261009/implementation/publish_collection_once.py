"""Only after actual SDK acceptance, schedule two matched frozen 80-env stress runs."""
from pathlib import Path
import sys,json,time,hashlib,statistics
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'COLLECTION_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect();w=connect_eval();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 with c.open_sftp() as f,w.open_sftp() as wf:
  job=json.loads((R/'DEVICE_ALIGNED_SDK_PUBLISHED.json').read_text(encoding='utf8'))['job']['job_id'];returned={}
  for name in ('probe.json','result.json'):
   raw=f.open(E+'/eval_results/'+job+'/'+name).read();assert raw==wf.open(W+'/jobs/'+job+'/'+name).read()
   returned[name]=hashlib.sha256(raw).hexdigest();(R/job/name).write_bytes(raw)
  result=json.loads((R/job/'result.json').read_text(encoding='utf8'));probe=json.loads((R/job/'probe.json').read_text(encoding='utf8'))
  assert result['phase']=='complete' and result['exit_code']==0 and not result['errors'] and not result['error_files'] and result['new_learning'] is False
  p=probe['D7_reset_performance_review'];assert p['actual_num_envs']==10 and p['actual_steps']==300 and p['no_PPO_or_optimizer_update']
  assert [m['selected'] for m in p['microbench']]==[1,3,10]
  assert all(m['exact_COM_translation_episode_private_RNG_before_after'] and m['backend_buffer_bytes_exact_per_variant'] and m['physical_rotations_preserved_existing_dtype_contract'] and m['independent_full_original_audit_after_each_reset'] for m in p['microbench'])
  review=dict(epoch=time.time(),accepted_SDK_interface_only=True,actual_COM_translation_episode_private_RNG_exact=True,raw_quaternion_bytes_pairwise_exact=all(x['raw_quaternion_bytes_pairwise_exact'] for x in p['microbench']),physical_rotation_existing_dtype_contract=True,returned_JSON=returned,
      microbench=[dict(selected=m['selected'],baseline_ms=1000*m['baseline_median'],optimized_ms=1000*m['optimized_median'],speedup=m['baseline_median']/m['optimized_median']) for m in p['microbench']],
      full_collection_benchmark_pending=True,main_training_and_canonical_transactions=0)
  raw=json.dumps(review,indent=2).encode();(R/'ACTUAL_SDK_ACCEPTED.json').write_bytes(raw)
  remote='/home/egde/rl_candidates/'+D.name
  with f.open(remote+'/reports/ACTUAL_SDK_ACCEPTED.json','wb') as out:out.write(raw)
  pub=json.loads((R/'COLLECTION_PACKAGES.json').read_text(encoding='utf8'));jobs=[]
  for order,variant in enumerate(('baseline','optimized')):
   row=json.loads((R/'template.json').read_text(encoding='utf8'))
   j='clk2500-closure-episode-d3-102-d7-reset-performance-'+str(order)+'-'+variant+'-flat'
   row.update(job_id=j,published_epoch=time.time(),num_envs=80,steps=1500,
       role='Isolated 80-env matched reset-stress collection timing '+variant+'; not skill graduation',
       no_learning=True,canonical_write_authority=False,performance_test=True,
       reset_stress_schedule=dict(first_control=50,every_control=10,selected_rows=4))
   package=pub['packages'][variant]
   row['artifacts']['runtime']={k:package[k] for k in ('path','sha256','bytes')}
   dest=E+'/eval_queue/'+j+'.json'
   try:f.stat(dest)
   except FileNotFoundError:pass
   else:raise AssertionError('Matched collection job already exists')
   with f.open(dest+'.partial','wb') as out:out.write(json.dumps(row,indent=2).encode())
   f.rename(dest+'.partial',dest);jobs.append(j)
  v=dict(epoch=time.time(),jobs=jobs,SDK=review,same_actual_seed_checkpoint_actions_reset_schedule=True,production_mutations=0)
  raw=json.dumps(v,indent=2).encode();(R/'COLLECTION_PUBLISHED.json').write_bytes(raw)
  with f.open(remote+'/reports/COLLECTION_PUBLISHED.json','wb') as out:out.write(raw)
  print(json.dumps(v))
finally:c.close();w.close()
